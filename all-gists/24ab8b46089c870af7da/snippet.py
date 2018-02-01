# -*- coding: utf-8 -*-

import json


def prettify_json(jsondata):
    return json.dumps(jsondata, sort_keys=True, indent=4)


def prettify_json_str(texte):
    return prettify_json(json.loads(texte))
