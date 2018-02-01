from __future__ import unicode_literals

import os
import sys

import requests


def get_emojis(token):
    response = requests.get("https://slack.com/api/emoji.list",
                            params={"token": token})
    return response.json()


def download_emojis(emojis, path):
    for name, url in emojis.items():
        print(name)
        if url.startswith("alias:"):
            continue
        try:
            response = requests.get(url)
            content_type = response.headers["content-type"]
            if content_type == "image/png":
                extension = "png"
            elif content_type == "image/jpeg":
                extension = "jpg"
            else:
                extension = ""
            image_file = os.path.join(path, name + "." + extension)
            with open(image_file, "wb") as f:
                f.write(response.content)
        except requests.RequestException as e:
            print(e)



if __name__ == "__main__":
    token = os.environ.get("SLACK_API_TOKEN")
    if token is None:
        sys.exit(1)

    if len(sys.argv) <= 1:
        sys.exit(1)
    path = sys.argv[1]

    result = get_emojis(token)
    if not result["ok"]:
        sys.exit(1)

    download_emojis(result["emoji"], path)

    sys.exit(0)
