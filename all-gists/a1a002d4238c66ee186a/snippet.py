# -*- coding: UTF-8 -*-

"""
CLI скрипт, поддерживающий две ветви параметров:
userdb.py append <username> <age>
userdb.py show <userid>

Заглушка предусматривает, что:
    пользователь с именем admin уже существует
    по userid = 1 всегда возвращается User(name='admin', age=20)

"""

import argparse

class User:
    """"Заглушка для ORM-объекта"""

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return 'Name: {0.name}, Age: {0.age}'.format(self)

    @staticmethod
    def add(name, age):
        if User.exists(name):
            raise ValueError('User with name "{}" already exists'.format(name))

        print 'User added with name [', name, '] and age [', age, ']'

    @staticmethod
    def exists(name):
        return name == 'admin'

    @staticmethod
    def select(id):
        if id == 1:
            return User('admin', '20')

        raise ValueError('User with ID: {} not found'.format(id))


def create_new_user(args):
    """Эта функция будет вызвана для создания пользователя"""

    User.add(name=args.username, age=args.age)


def user_from_db(user_id):
    """Возвращает объект-пользователя, если id прошел валидацию, или
    генерирует исключение.
    """
    # валидируем user_id
    id = int(user_id)

    return User.select(id=id)  # создаем объект ORM и передаем его программе


def print_user(args):
    """Отображение информации о пользователе"""

    print str(args.user_dbobj)


def parse_args():
    """Настройка argparse"""

    parser = argparse.ArgumentParser(description='User database utility')
    subparsers = parser.add_subparsers()

    parser_append = subparsers.add_parser('append', help='Append a new user to database')
    parser_append.add_argument('username', help='Name of user')
    parser_append.add_argument('age', type=int, help='Age of user')
    parser_append.set_defaults(func=create_new_user)

    parser_show = subparsers.add_parser('show', help='Show information about user')
    parser_show.add_argument('user_dbobj', type=user_from_db, metavar='userid', help='ID of user')
    parser_show.set_defaults(func=print_user)

    return parser.parse_args()


def main():
    """Это все, что нам потребуется для обработки всех ветвей аргументов"""
    args = parse_args()
    try:
        args.func(args)

    except Exception as e:
        print e.message


if __name__ == '__main__':
    main()
