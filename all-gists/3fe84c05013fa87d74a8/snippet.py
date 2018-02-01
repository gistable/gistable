import os
import json
import tarfile
import urllib.request
import easygui
import configparser

user_docsets_url = 'https://dashes-to-dashes.herokuapp.com/docsets/contrib'
app_title = 'Download Zeal user docsets'


def get_user_docsets(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    docsets = json.loads(text)
    return docsets


def choose_docset(user_docsets):
    msg = "Choose which user docset to download."
    choice = easygui.multchoicebox(
        msg, app_title, [d['name'] for d in user_docsets])
    return choice


def get_zeal_docsets_dir():
    config = configparser.ConfigParser()
    config.read([os.path.expanduser('~/.config/Zeal/Zeal.conf')])
    return config['docsets']['path']


def download_docset(url, directory):
    with urllib.request.urlopen(url) as response:
        with tarfile.open(fileobj=response, mode='r:gz') as tar:
            tar.extractall(directory)


def search_url(choice, user_docsets):
    return [d['archive'] for d in user_docsets if d['name'] == choice][0]


def confirm_docset_download(choice, docset_url, docsets_dir):
    return easygui.ccbox('The {0} docset will be downloaded from {1} and extracted into {2}.\n\nPlease wait.'.format(choice, docset_url, docsets_dir), app_title)


def docset_successfully_downloaded(choice):
    easygui.msgbox(
        '{0} docset successfully downloaded.'.format(choice), app_title)


def download_more_docsets():
    return easygui.ynbox('Do you want to download another docset?', app_title, ('Yes', 'No'))


def exit_message():
    easygui.msgbox(
        'Bye bye.\n\nPlease remember to restart Zeal to refresh the docsets.', app_title, 'Quit')


def show_exception(e):
    easygui.exceptionbox('Error: {0}'.format(e), app_title)

if __name__ == '__main__':
    try:
        user_docsets = get_user_docsets(user_docsets_url)
        while True:
            choice = choose_docset(user_docsets)
            if not choice:
                break
            docset_url = search_url(choice, user_docsets)
            docsets_dir = get_zeal_docsets_dir()
            if confirm_docset_download(choice, docset_url, docsets_dir):
                download_docset(docset_url, docsets_dir)
                docset_successfully_downloaded(choice)
            if not download_more_docsets():
                break
        exit_message()
    except Exception as e:
        show_exception(e)