# Copyright (c) 2017 Stanislav Bobokalo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import DeleteMessagesRequest
from telethon.tl.types import Channel
import shelve
from os import listdir
from time import sleep

# Просто утилиты

def chunks(l, n):
    """Разбивает список l на чанки размером n. Возвращает генератор"""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def print_header(text):
    """Просто для красивого вывода"""
    print('====================')
    print('= {} ='.format(text))
    print('====================')
    
###########################################

API_ID = 666666
API_HASH = 'xxxxxxxxxxxxxxxxxxxxxxx'
PHONE = '+xxxxxxxxx'
NUMBER_OF_CHUNKS = 1 # Сколько чанков подгрузить за выполнение скрипта
CHUNK_SIZE = 1000 # Сколько сообщений нужно просканировать за чанк
FROM_ID = 123456 # ID пользователя, сообщения которого нужно удалить

class DeleterClient(TelegramClient):
    def __init__(self, session_user_id, user_phone, api_id, api_hash):
        super().__init__(session_user_id, api_id, api_hash)

        self.messages_to_delete = set()
        self.chunk_size = CHUNK_SIZE  # Сколько сообщений нужно просканировать за чанк

        # Проверка соеденения с сервером. Проверка данных приложения
        print('Connecting to Telegram servers...')
        if not self.connect():
            print('Initial connection failed. Retrying...')
            if not self.connect():
                print('Could not connect to Telegram servers.')
                return

        # Проверка авторизирован ли юзер под сессией
        if not self.is_user_authorized():
            print('First run. Sending code request...')
            self.send_code_request(user_phone)

            self_user = None
            while self_user is None:
                code = input('Enter the code you just received: ')
                try:
                    self_user = self.sign_in(user_phone, code)

                # Two-step verification may be enabled
                except SessionPasswordNeededError:
                    pw = input('Two step verification is enabled. Please enter your password: ')
                    self_user = self.sign_in(password=pw)

        limit = input('Enter limit of chats (empty for all): ')
        # Добавляем количество отображаемых групп
        if limit:
            self.limit = int(limit)
        else:
            self.limit = None

        # Создание пустого хранилища для сдвигов сканирования
        if 'parsed_chunks.db' not in listdir('.'):
            self._init_shelve(*self.get_dialogs(self.limit))

    def run(self):
        # Запрос выбора чата для сканирования
        peer = self.choose_peer()
        # ID пользователя чьи сообщения удалить
        from_id = FROM_ID
        # Основная функция выкачки сообщений и фильтрация от нужного юзера
        self.filter_messages_from_chunk(peer, from_id)
        # Основная функция удаления сообщений юзера из чата
        r = self.delete_messages_from_peer(peer)
        return r

    def choose_peer(self):
        dialogs, entities = self.get_dialogs(limit=self.limit)
        s = ''

        entities = [entity for entity in entities if isinstance(entity, Channel)]   # Удаляем все супергруп и каналов
        entities = [entity for entity in entities if entity.megagroup]  # А теперь и каналы

        for i, entity in enumerate(entities):
            s += '{}. {}\t | {}\n'.format(i, entity.title, entity.id)

        print(s)
        num = input('Choose group: ')
        print('Chosen: ' + entities[int(num)].title)

        return entities[int(num)]

    def delete_messages_from_peer(self, peer):
        messages_to_delete = list(self.messages_to_delete)
        print_header('УДАЛЕНИЕ {} СВОИХ СООБЩЕНИЙ В ЧАТЕ {}'.format(len(messages_to_delete), peer.title))
        for chunk_data in chunks(messages_to_delete, 100):
            # Поскольку удалить больше чем 100 сообщеий мы не можем - разделяем на маленькие кусочки
            r = self(DeleteMessagesRequest(peer, chunk_data))
            if r.pts_count:
                print('Удалено сообщений: {}'.format(r.pts_count))
            sleep(1)
        return True

    def filter_messages_from_chunk(self, peer, from_id):
        number_of_chunks = NUMBER_OF_CHUNKS
        messages = []

        for n in range(number_of_chunks):
            msgs, status = self.get_chunk(peer, n)
            messages.extend(msgs)
            if not status:
                break

        # Генератор который фильтрует сообщения от нужного пользователя
        filter_generator = (msg.id for msg in messages if msg.from_id == from_id)
        self.messages_to_delete.update(filter_generator)

    def get_chunk(self, peer, chunk_number, limit=100, offset_date=None, offset_id=0, max_id=0, min_id=0):
        add_offset = self._shelve_read(peer.id)
        print_header('ВЫКАЧКА ЧАНКА #{}'.format(chunk_number))
        local_offset = 0
        messages = []

        while True and local_offset < self.chunk_size:
            sleep(1)
            # Поскольку лимит на выкачку сообщений 100 - выкачиваем по 100 и делаем шаг равный выкачанному ранее
            result = self(GetHistoryRequest(
                peer,
                limit=limit,
                offset_date=offset_date,
                offset_id=offset_id,
                max_id=max_id,
                min_id=min_id,
                add_offset=add_offset
            ))

            if result.messages:
                print('Скачано сообщений: {}. Сдвиг: {}.'.format(len(result.messages), add_offset))
                messages.extend(result.messages)
                add_offset += len(result.messages)
                local_offset += len(result.messages)
                # Записываем значение смещения для данной группы
                self._shelve_write(peer.id, add_offset)
            else:
                print_header('ПОЛУЧЕНО 0 СООБЩЕНИЙ. ВЫКАЧКА ЧАНКА #{} ОСТАНОВЛЕНА, '
                             'СКОРЕЕ ВСЕГО ДОШЛО ДО КОНЦА ЧАТА'.format(chunk_number))
                return messages, False

        return messages, True

    @staticmethod
    def _shelve_write(k, v):
        with shelve.open('parsed_chunks.db') as db:
            db[str(k)] = v

    @staticmethod
    def _shelve_read(k):
        with shelve.open('parsed_chunks.db') as db:
            return db[str(k)]

    def _init_shelve(self, dialogs, entities):
        for entity in entities:
            self._shelve_write(entity.id, 0)

client = DeleterClient('Deleter', PHONE, API_ID, API_HASH)  # 1 аргумент - название сессии, второй - телефон,
                                                            # третий - айди приложения, четвертый - хэш приложения
client.run()