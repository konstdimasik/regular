#!/usr/bin/env python

import datetime as dt
import json
import sys


def add_task():
    with open('regular_data.json', 'r') as tasks_db:
        tasks = json.load(tasks_db)
    dist = {}
    list_str = input('Опишите задачу:').split(';')
    dist['name'] = list_str[0]
    dist['description'] = list_str[1]
    dist['dates'] = [list_str[2]]
    dist['period'] = list_str[3]
    tasks.append(dist)
    for task in tasks:
        print(task['name'])
    with open('regular_data.json', 'w') as tasks_db:
        json.dump(tasks, tasks_db, indent=4, ensure_ascii=False)


def print_tasks():
    with open('regular_data.json', 'r') as tasks_db:
        tasks = json.load(tasks_db)
    for task in tasks:
        list_date = task['dates'][0].split(',')
        year = int(list_date[0])
        month = int(list_date[1])
        day = int(list_date[2])
        task_time = dt.date(year, month, day)
        print('{0: <40}'.format(task['name']), end='')
        print('{0: >10}'.format(task_time.strftime('%d.%m.%Y')))


def print_next_tasks():
    with open('regular_data.json', 'r') as tasks_db:
        tasks = json.load(tasks_db)
    now = dt.datetime.utcnow()
    period = dt.timedelta(hours=3)
    moscow_moment = now + period
    print('{0: >50}'.format(moscow_moment.strftime('%d.%m.%Y')))
    for task in tasks:
        list_date = task['dates'][0].split(',')
        year = int(list_date[0])
        month = int(list_date[1])
        day = int(list_date[2])
        task_time = dt.date(year, month, day)
        next_task_time = task_time + dt.timedelta(days=int(task['period']))
        print('{0: <40}'.format(task['name']), end='')
        print('{0: >10}'.format(next_task_time.strftime('%d.%m.%Y')))


# # First program was on JSON DB and fisrt off all I made migration
# def migration():
#     with open('regular_data.json', 'r') as file:
#         data = json.load(file)
#     id_counter = 0
#     for task in data:
#         id_counter += 1
#         name = task['name']
#         desc = task['description']
#         list_date = task['dates'][0].split(',')
#         year = int(list_date[0])
#         month = int(list_date[1])
#         day = int(list_date[2])
#         period = task['period']
#         sql.execute('SELECT name FROM task WHERE name = ?', name)
#         if sql.fetchone() is None:
#             sql.execute('INSERT INTO task VALUES (?, ?, ?, ?)',
#                         (id_counter, name, desc, period))
#             sql.execute('INSERT INTO date_updates VALUES(?,?,?)',
#                         (id_counter, dt.date(year, month, day), id_counter))
#             db.commit()
#             print('Данные перенесены!')
#         else:
#             print('Такая задача уже есть')
#             for value in sql.execute('SELECT * FROM task'):
#                 print(value)


def main():
    print('Сейчас доступны -add, -tasks, -next')
    if sys.argv[1] == '-add':
        add_task()
    if sys.argv[1] == '-tasks':
        print_tasks()
    if sys.argv[1] == '-next':
        print_next_tasks()


if __name__ == '__main__':
    main()
