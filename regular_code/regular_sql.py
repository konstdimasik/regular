#!/usr/bin/env python

import datetime as dt
import sqlite3

import prompt
from prettytable import from_db_cursor

global conn
global cursor

conn = sqlite3.connect('regular_code/regular.db')
conn.execute('PRAGMA foreign_keys = 1')
cursor = conn.cursor()


# Model
def create_table():
    cursor.execute('CREATE TABLE IF NOT EXISTS task(\n'
                   'task_id INTEGER PRIMARY KEY,\n'
                   'name TEXT NOT NULL,\n'
                   'description TEXT,\n'
                   'period INT,\n'
                   'next_date DATE\n'
                   ')')
    cursor.execute('CREATE TABLE IF NOT EXISTS date_updates(\n'
                   'date_id INTEGER PRIMARY KEY,\n'
                   'dates DATE NOT NULL,\n'
                   'task_id INT NOT NULL,\n'
                   'FOREIGN KEY (task_id) REFERENCES task(task_id)\n'
                   ')')
    conn.commit()


def add_task(input_str):
    input_task = input_str.split('; ')
    name = input_task[0]
    cursor.execute('SELECT name FROM task WHERE name = ?', (name,))
    task_name = cursor.fetchone()
    if task_name is not None:
        return 'Такая задача уже есть:\n' + str(cursor.fetchall())
    if len(input_task) >= 2:
        desc = input_task[1]
    else:
        desc = prompt.string("Опишете суть задачи\n")
    if len(input_task) >= 3:
        period = input_task[2]
    else:
        period = prompt.string("Как часто нужно выполнять задачу\n")
    cursor.execute('INSERT INTO task VALUES (?, ?, ?, ?, ?)',
                   (None, name, desc, period, None))
    conn.commit()
    print('Задача добавлена')
    input_date = prompt.string('Задача уже выполнена? "Нет" '
                               'или дата(год.месяц.число)\n')
    if input_date == 'Нет':
        return 'Ок, выполним позднее'
    list_date = input_date.split('.')
    year = int(list_date[0])
    month = int(list_date[1])
    day = int(list_date[2])
    cursor.execute('SELECT task_id FROM task WHERE name = ?', (name,))
    task_id = cursor.fetchone()
    cursor.execute('INSERT INTO date_updates VALUES(?,?,?)',
                   (None, dt.date(year, month, day), task_id[0]))
    output_str = update_next_date(task_id[0])
    print(output_str)
    conn.commit()
    return 'Следующая дата выполнения задачи добавлена'


def add_date(input_str):
    list_input_date = input_str.split(';')
    task_id = list_input_date[0]
    #cursor.execute('SELECT task_id FROM task WHERE name = ?', (name,))
    cursor.execute("SELECT * FROM task WHERE task_id = ?", (task_id,))
    result = cursor.fetchone()
    if result is None:
        return 'Нет такой задачи'
    list_date = list_input_date[1].split('.')
    year = int(list_date[0])
    month = int(list_date[1])
    day = int(list_date[2])
    cursor.execute('INSERT INTO date_updates VALUES(?,?,?)',
                   (None, dt.date(year, month, day), task_id))
    conn.commit()
    return 'Дата выполнения задачи добавлена'


def update_period(task_id):
    cursor.execute('                SELECT t.task_id, t.period, d.dates\n'
                   '                FROM date_updates AS d\n'
                   '                JOIN task AS t\n'
                   '                WHERE d.task_id = t.task_id and t.task_id = ?\n'
                   '                ORDER BY d.dates\n'
                   '                ', (task_id,))
    date_list = cursor.fetchall()
    num_delta = len(date_list)
    sum_delta = dt.timedelta(days=0)
    i = 1
    while i < len(date_list):
        date_i = dt.date.fromisoformat(date_list[i][2])
        date_prev = dt.date.fromisoformat(date_list[i - 1][2])
        delta = date_i - date_prev
        sum_delta += delta
        i += 1
    avg_delta = (sum_delta + dt.timedelta(date_list[0][1])) / num_delta
    cursor.execute('UPDATE task SET period = ? WHERE task_id = ?',
                   (avg_delta.days, task_id,))
    cursor.execute('SELECT name FROM task WHERE task_id = ?', (task_id,))
    task_name = cursor.fetchone()[0]
    conn.commit()
    return (f'Периодичность задачи "{task_name}" '
            f'пересчитана и равна {avg_delta.days}')


def update_next_date(task_id):
    cursor.execute('                SELECT t.task_id, t.period, MAX(d.dates)\n'
                   '                FROM task AS t\n'
                   '                JOIN date_updates AS d\n'
                   '                WHERE d.task_id = t.task_id and t.task_id = ?\n', (task_id,))
    date_list = cursor.fetchone()
    task_date = dt.date.fromisoformat(date_list[2])
    next_task_date = task_date + dt.timedelta(date_list[1])
    cursor.execute('UPDATE task SET next_date = ? WHERE task_id = ?',
                   (next_task_date, date_list[0],))
    cursor.execute('SELECT name FROM task WHERE task_id = ?', (task_id,))
    task_name = cursor.fetchone()[0]
    conn.commit()
    return (f'Новая дата задачи "{task_name}" '
            f'пересчитана и равна {next_task_date}')


# View
def print_table(table_name):
    query = "SELECT 1 FROM sqlite_master WHERE type='table' and name = ?"
    if cursor.execute(query, (table_name,)).fetchone() is not None:
        if table_name == 'task':
            query = 'SELECT name, description, period, next_date FROM task'
        else:
            query = 'SELECT task_id, dates FROM date_updates'
        cursor.execute(query)
        my_pretty_table = from_db_cursor(cursor)
        print(my_pretty_table)
    else:
        print('Wrong table name')


def print_table_names():
    cursor.execute('SELECT name FROM sqlite_schema WHERE type = "table"')
    table_names = from_db_cursor(cursor)
    print(table_names)


def last_completed_task():
    cursor.execute('                SELECT t.name, MAX(d.dates), t.period\n'
                   '                FROM task as t\n'
                   '                JOIN date_updates AS d\n'
                   '                WHERE d.task_id = t.task_id\n'
                   '                GROUP BY t.name\n'
                   '                ORDER BY d.dates\n'
                   '                ')
    return cursor


def next_tasks():
    cursor.execute('                SELECT task_id, name, next_date, period\n'
                   '                FROM task\n'
                   '                ORDER BY next_date\n'
                   '                ')
    return cursor


def main():
    # Controller
    while True:
        start = prompt.string('Сейчас доступны:\n add_task (1)\n add_date (2)\n print_table (3)\n '
                              'next_tasks (4)\n exit (5)\nЧто делаем?\n')
        if start == '1':
            input_str = prompt.string('Опишите задачу: название; описание; '
                                      'как часто выполнять(раз в N дней).\n')
            output_str = add_task(input_str)
            print(output_str)
        elif start == '2':
            input_str = prompt.string('Какую задачу; когда сделали (год.месяц.число)\n')
            output_str = add_date(input_str)
            print(output_str)
            if output_str == 'Дата выполнения задачи добавлена':
                output_str = update_period(input_str.split(';')[0])
                print(output_str)
                output_str = update_next_date(input_str.split(';')[0])
                print(output_str)
        elif start == '3':
            print_table_names()
            input_str = prompt.string('Какую таблицу вывести?\n')
            print_table(input_str)
        elif start == '4':
            print(from_db_cursor(last_completed_task()))
            print(f'СЕГОДНЯ {dt.date.today().strftime("%Y-%m-%d"): >41}')
            print(from_db_cursor(next_tasks()))
        elif start == '5':
            conn.close()
            exit()
        else:
            print(f'Неизвестная команда "{start}"')


if __name__ == '__main__':
    main()
