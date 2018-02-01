from telethon.tl.functions import InitConnectionRequest, InvokeWithLayerRequest
from telethon.tl.functions import langpack  # GetLangPackRequest, GetDifference
from telethon.tl import all_tlobjects  # for LAYER
from telethon.tl.types import LangPackString, LangPackStringPluralized, LangPackStringDeleted

from telethon.tl.functions import InitConnectionRequest, InvokeWithLayerRequest
from telethon.tl.functions import langpack  # GetLangPackRequest, GetDifference
from telethon.tl import all_tlobjects
from telethon.tl.types import LangPackString, LangPackStringPluralized, LangPackStringDeleted

def get_lang_pack(client, lang_pack, lang_code='en', from_version=None):
    if from_version is not None:
        query = langpack.GetDifference(from_version=from_version)
    else:
        query = langpack.GetLangPackRequest(lang_code=lang_code)

    init_connection_request = InitConnectionRequest(
        api_id=client.api_id,
        lang_pack=lang_pack,
        query=query,
        lang_code=lang_code,
        **{x: 'shitfuck' for x in ['device_model', 'system_version', 'app_version', 'system_lang_code']}
    )
    return client(InvokeWithLayerRequest(layer=all_tlobjects.LAYER, query=init_connection_request))

def parse_lang_pack(pack):
    parsed = dict()
    
    for lpstr in pack.strings:
        if isinstance(lpstr, LangPackString):
            parsed[lpstr.key] = lpstr.value
        elif isinstance(lpstr, LangPackStringPluralized):
            for mode in ['zero', 'one', 'two', 'few', 'many', 'other']:
                val = getattr(lpstr, mode + '_value')
                if val is not None:
                    parsed['%s#%s' % (lpstr.key, mode)] = val
        elif isinstance(lpstr, LangPackStringDeleted):
            # HOW DO I HANDLE THIS LOL
            pass

    return parsed


"""
# Usage example:

from telethon import TelegramClient
from pprint import pprint
from langpacker import *
# see telethon docs
client = TelegramClient(session_name, api_id, api_hash)
client.connect()

pprint(parse_lang_pack(get_lang_pack(client, 'android', 'ru')))

client.disconnect()
"""