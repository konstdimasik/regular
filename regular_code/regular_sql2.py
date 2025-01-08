#!/usr/bin/env python

import datetime as dt
import sqlite3
from typing import Dict, List

#import prompt
from prettytable import from_db_cursor

global conn
global cursor

conn = sqlite3.connect('regular_code/regular2.db')
conn.execute('PRAGMA foreign_keys = 1')
cursor = conn.cursor()

def ask_for_user_command(command_options: Dict) -> None:
    command = input('Your command:\n').lower()
    if command in command_options:
        command_options[command]()
    else:
        print('Invalid input')


class Interface:
    def __init__(self):
        self.app_opened = True
        self._main_menu_options = {
            # 'new': self.ask_for_new,
            # 'fin': self.make_done,
            # 'up': self.change_period,
            'v': self.view,
            # 'h': self.help,
            'exit': self.exit_app,
        }
    
    def view(self) -> None:
        engine = Engine()
        print(from_db_cursor(engine.run_the_engine('last')))
        today = dt.date.today()
        print(f'СЕГОДНЯ {today.strftime("%Y-%m-%d"): >31}')
        print(from_db_cursor(engine.run_the_engine('today')))
        tomorrow = today + dt.timedelta(days=1)
        print(f'ПОТОМ {tomorrow.strftime("%Y-%m-%d"): >33}')
        print(from_db_cursor(engine.run_the_engine('next')))
        self.run_main_menu

    def exit_app(self) -> None:
        self.app_opened = False
        print('_____Bye! Its nice to work with u!_____')

    def run_main_menu(self) -> None:
        while self.app_opened:
            print('\t Опции:')
            print('[New] task\n[V]iew\n[Fin]ish task\n[Up]date task\n[H]elp\n[Exit]\n')
            ask_for_user_command(self._main_menu_options)

class Engine:
    def __init__(
        self,
    ):
        self.engine_works = True
        self.engine_tasks = {
            'last': self.last_completed_task,
            'next': self.next_tasks,
            'today': self.today,
        }
    
    def last_completed_task(self):
        cursor.execute('             SELECT t.task_id, t.name, MAX(d.dates), t.period\n'
                    '                FROM task as t\n'
                    '                JOIN date_updates AS d\n'
                    '                WHERE d.task_id = t.task_id\n'
                    '                GROUP BY t.name\n'
                    '                ORDER BY d.dates\n'
                    '                ')
        return cursor


    def next_tasks(self):
        cursor.execute('             SELECT task_id, name, next_date, period\n'
                    '                FROM task\n'
                    '                ORDER BY next_date\n'
                    '                ')
        return cursor
    
    def today(self):
        cursor.execute('             SELECT task_id, name, next_date, period\n'
                    '                FROM task\n'
                    '                WHERE next_date = date("now")\n'
                    '                ORDER BY next_date\n'
                    '                ')
        return cursor

    def run_the_engine(self, task: int):
        while self.engine_works:
            if task in self.engine_tasks:
                return self.engine_tasks[task]()
            else:
                print('Invalid input')


def main():
    app = Interface()
    app.run_main_menu()


if __name__ == '__main__':
    main()