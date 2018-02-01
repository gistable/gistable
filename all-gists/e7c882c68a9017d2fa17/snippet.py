#!/usr/bin/env python3
# A simple command-line client for Yandex.Translate.
# You may pass translate direction as command line parameter e.g. "./dict-client.py fr-en"
# Default translate direction is from English to Russian.

#!/usr/bin/env python3

import requests
import sys

TRANSLATE_DIRECTION = "en-ru"
# Ключ для API должен лежать в файле api_key
# Получать здесь: https://tech.yandex.ru/keys/get/?service=dict

def process(line, api_key):
    r = requests.get("https://dictionary.yandex.net/api/v1/dicservice.json/lookup?" +
                     "key=" + api_key +
                     "&lang=" + TRANSLATE_DIRECTION +
                     "&text=" + line)

    defs = r.json()["def"]
    for d in defs:
        l = d["tr"]
        for x in l:
            print("\t" + x["text"])
            if "ex" in x:
                for ex in x["ex"]:
                    print("\t" * 2 + ex["text"] + " - ", end="")
                    for tr in ex['tr']:
                        print(tr["text"], end=",")
                    print()
    print("*" * 80)

# Ключ для API должен лежать в файле api_key
# Получать здесь: https://tech.yandex.ru/keys/get/?service=dict
def get_api_key():
    with open("api_key") as f:
        return f.readline().rstrip("\n")


def show_langs(api_key):
    pass

if __name__ == "__main__":

    api_key = get_api_key()

    if len(sys.argv) == 2:
        TRANSLATE_DIRECTION = sys.argv[1]
    else:
        show_langs(api_key)

    print("Введите слово для перевода или EOF для выхода")
    for line in sys.stdin:
        process(line, api_key)
