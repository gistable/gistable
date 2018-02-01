# -*- coding: utf-8 -*-
import requests
from time import sleep
from datetime import datetime
import json
import sys

database = {"admins":[],
            "suggestions":{}
}
tempdb = {}

with open("access_token.txt", "r") as myfile:
    token = myfile.read().replace('\n', '')  

publics = [78047404, 23854739, 73127371]  # список пабликов для парсинга
list_id = None  # для списков новостей
current_next_post = None


#Получение своего айди для дальнейшего его исключения из выдачи
def get_my_id():
    url = 'https://api.vk.com/method/users.get'
    request = requests.get(url, params = {'access_token': token})
    decode = request.json()
    try:
        id = decode['response'][0]['uid']
        return id

    except KeyError:
        print ('Невалидный токен')
        exit()

#Создание списка новостей с нужным пабликом
def create_work_list(target_id):
    global list_id
    print('создаем список')
    url = 'https://api.vk.com/method/newsfeed.saveList'
    par = {'title': 'title', 'source_ids': target_id, 'access_token': token}
    request = requests.get(url, params=par)
    request = request.json()
    if 'response' in request:
        list_id = request['response']
    else:
        if 'error' in request and 'error_code' in request['error'] and request['error']['error_code'] == 1170:
            print('у тебя слишком много списков, для работы нужно удалить хотя бы один. сделай это сам')
        else:
            print('неизвестная ошибка')
            print(request)
        exit()
    print ('Список с id:'+str(list_id)+' создан')
    pass

#Newsfeed_get для списка новостей
def get_post(x, count):
    url = 'https://api.vk.com/method/newsfeed.get'
    par = {'access_token': token,
           'count': count,
           'filters': 'post',
           'v': 5.24,
           'start_from': x,
           'source_ids': 'list'+str(list_id) }
    request = requests.get(url, params = par)
    decode = request.json()
    post = decode['response']
    return post

#Получение общего количества постов
def get_posts_in_work():
    full_length = 0
    next_from = ""
    post = get_post(next_from, 100)
    length = len(post['items'])
    full_length += length
    sleep(1)
    while has_next(post):
        next_from = post['next_from']
        post = get_post(next_from, 0)
        length = len(post['items'])
        full_length += length

    return full_length

#Проверяем наличие списка с таким именем
def check_list_exists(id):
    try:
        tempdb[id][0]
        return True
    except:
        return False

#Получаем список айди для поста
def get_ids(post, my_id):
    profiles = post['profiles']
    ids = []
    for item in profiles:
        id = item['id']
        if id != my_id:
            id = str(id)
            ids.append(id)

    return ids

#Получаем ссылку на пост
def get_link(post):
    content = post['items']
    link = ''
    for item in content:
        source = str(item['source_id'])
        post_id = str(item['post_id'])
        text = item['text']
        date = str(datetime.fromtimestamp(item['date']))
        link = "http://vk.com/wall%s_%s" % (source, post_id)
    return link

#Айди поста получает
def get_id(post):  # так легче читать
    content = post['items']
    post_id = 0
    for item in content:
        post_id = str(item['post_id'])
    return post_id


#Получаем параметр next_from для следующего поста
def get_next(post):
    next = post['next_from']
    return next

#Пишем в словарик
def add_to_db(link, ids):
    for item in ids:
        if check_list_exists(item) == False:
            tempdb[item] = []
            tempdb[item].append(link)
        else:
            tempdb[item].append(link)

#Проверяем отдало ли апи next_from
def has_next(post):
    if post['next_from']:
        return True
    else:
        return False

#Удаляем список новостей после парсинга
def delete_work_list():
    global list_id
    url = 'https://api.vk.com/method/newsfeed.deleteList'
    par = {'list_id': list_id, 'access_token': token}
    request = requests.get(url, params=par)
    print('список с id '+str(list_id)+' удалено')
    pass

#Анализируем ДБ и пишем результаты
def get_suggestions(dictionary):
    for key in dictionary:
        if len(tempdb[key]) == 4:
            link = tempdb[key][3]
            id = "http://vk.com/id"+key
            try:
                database['suggestions'][id] = link
            except:
                print ("Ошибка добавления в словарь предложки")
                print ("Ключ: "+id)
        elif len(tempdb[key]) != 4 and len(tempdb[key]) != 8 and len(tempdb[key]) != 12   :
            database['admins'].append("http://vk.com/id"+key)

#Прогресс бар
def progress_bar(count, progress):
    percentage = progress*100/count
    sys.stdout.write("\r%d%%" % percentage)
    sys.stdout.flush()

# Работаем
def get_result():
    global current_next_post
    my_id = get_my_id()
    for public_id in publics:
        progress = 0
        print ("Начинаем парсинг")
        create_work_list(-public_id)
        posts = get_posts_in_work()
        print (str(posts)+(" постов будет обработано"))
        time = (posts/120)
        print ("Предположительное время работы: "+(str(time))[:4]+" минут")
        post = get_post(0, 1)
        ids = get_ids(post, my_id)
        link = get_link(post)
        add_to_db(link, ids)
        nextpost = get_next(post)
        sleep(1)
        progress += 1
        progress_bar(posts, progress)
        while has_next(post):  # начало нужно для того, чтобы запустить цикл, иначе не получить некст_фром
            post = get_post(nextpost, 1)
            ids = get_ids(post, my_id)
            link = get_link(post)
            add_to_db(link, ids)
            nextpost = get_next(post)
            sleep(0.5)
            progress += 1
            progress_bar(posts, progress)
        print ("Парсинг окончен")
        get_suggestions(tempdb)
        delete_work_list()
        with open(public_id+'.json', 'w') as outfile:
            json.dump(database, outfile)

get_result()
exit()


