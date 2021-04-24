#!/usr/bin/env python

import datetime as dt
import sqlite3

import prompt
from prettytable import from_db_cursor

global db
global sql

db = sqlite3.connect('regular_code/regular.db')
db.execute('PRAGMA foreign_keys = 1')
sql = db.cursor()


# Model
def create_table():
    sql.execute('CREATE TABLE IF NOT EXISTS task(\n'
                '        task_id INTEGER PRIMARY KEY,\n'
                '        name TEXT NOT NULL,\n'
                '        description TEXT,\n'
                '        period INT,\n'
                '        next_date DATE\n'
                '    )')
    sql.execute('CREATE TABLE IF NOT EXISTS date_updates(\n'
                '        date_id INTEGER PRIMARY KEY,\n'
                '        dates DATE NOT NULL,\n'
                '        task_id INT NOT NULL,\n'
                '        FOREIGN KEY (task_id) REFERENCES task(task_id)\n'
                '    )')
    db.commit()


def add_task(input_str):
    input_task = input_str.split(';')
    name = input_task[0]
    sql.execute('SELECT name FROM task WHERE name = ?', input_task[0])
    task_name = sql.fetchone()
    if task_name is not None:
        return 'Такая задача уже есть:\n' + str(sql.fetchone())
    if len(input_task) == 2:
        desc = input_task[1]
    if len(input_task) == 3:
        period = input_task[2]
    sql.execute('INSERT INTO task VALUES (?, ?, ?, ?)',
                (None, name, desc, period))
    db.commit()
    print('Задача добавлена')
    input_date = prompt.string('Задача уже выполнена? "Нет" '
                               'или дата(год.месяц.число)\n')
    if input_date == 'Нет':
        return 'Ок, выполним позднее'
    list_date = input_date.split('.')
    year = int(list_date[0])
    month = int(list_date[1])
    day = int(list_date[2])
    sql.execute('SELECT task_id FROM task WHERE name = ?', (name,))
    task_id = sql.fetchone()
    sql.execute('INSERT INTO date_updates VALUES(?,?,?)',
                (None, dt.date(year, month, day), task_id[0]))
    db.commit()
    return 'Дата выполнения задачи добавлена'


def add_date(input_str):
    list_input_date = input_str.split(';')
    name = list_input_date[0]
    sql.execute('SELECT task_id FROM task WHERE name = ?', (name,))
    task_id = sql.fetchone()
    if task_id is None:
        return 'Нет такой задачи'
    list_date = list_input_date[1].split('.')
    year = int(list_date[0])
    month = int(list_date[1])
    day = int(list_date[2])
    sql.execute('INSERT INTO date_updates VALUES(?,?,?)',
                (None, dt.date(year, month, day), task_id[0]))
    db.commit()
    return 'Дата выполнения задачи добавлена'


def update_period(task_name):
    sql.execute('                SELECT t.task_id, t.period, d.dates\n'
                '                FROM date_updates AS d\n'
                '                JOIN task AS t\n'
                '                WHERE d.task_id = t.task_id and t.name = ?\n'
                '                ORDER BY d.dates\n'
                '                ', (task_name,))
    date_list = sql.fetchall()
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
    sql.execute('UPDATE task SET period = ? WHERE name = ?',
                (avg_delta.days, task_name,))
    db.commit()
    return (f'Периодичность задачи "{task_name}" '
            f'пересчитана и равна {avg_delta.days}')


def update_next_date(task_name):
    sql.execute('                SELECT t.task_id, t.period, MAX(d.dates)\n'
                '                FROM task AS t\n'
                '                JOIN date_updates AS d\n'
                '                WHERE d.task_id = t.task_id and t.name = ?\n', (task_name,))
    date_list = sql.fetchone()
    task_date = dt.date.fromisoformat(date_list[2])
    next_task_date = task_date + dt.timedelta(date_list[1])
    sql.execute('UPDATE task SET next_date = ? WHERE task_id = ?',
                (next_task_date, date_list[0],))
    db.commit()
    return (f'Новая дата задачи "{task_name}" '
            f'пересчитана и равна {next_task_date}')


# View
def print_table(table_name):
    sql.execute('SELECT * FROM ?', (table_name,))
    my_pretty_table = from_db_cursor(sql)
    print(my_pretty_table)


def last_completed_task():
    sql.execute('                SELECT t.name, MAX(d.dates)\n'
                '                FROM task as t\n'
                '                JOIN date_updates AS d\n'
                '                WHERE d.task_id = t.task_id\n'
                '                GROUP BY t.name\n'
                '                ORDER BY d.dates\n'
                '                ')
    return sql


def next_tasks():
    sql.execute('                SELECT name, next_date\n'
                '                FROM task\n'
                '                ORDER BY next_date\n'
                '                ')
    return sql


def main():
    # Controller
    start = prompt.string('Сейчас доступны \nadd_task (1)\nadd_date (2)\nprint_table (3)\n'
                          'next_tasks (4)\nЧто делаем?\n')
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
        input_str = prompt.string('Какую таблицу вывести?\n')
        print_table(input_str)
    elif start == '4':
        print(from_db_cursor(last_completed_task()))
        print(f'СЕГОДНЯ {dt.date.today().strftime("%Y-%m-%d"): >41}')
        print(from_db_cursor(next_tasks()))
    print(f'Неизвестная команда "{start}"')


if __name__ == '__main__':
    main()
