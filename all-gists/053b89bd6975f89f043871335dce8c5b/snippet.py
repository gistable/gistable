import pprint
import requests
import os
from urllib.request import urlopen

accessToken = "xxxxxxxxxx"
boardId = "0000000000"
folderPath = "./images"

response = requests.get(
    'https://api.pinterest.com/v3/boards/'+boardId+'/pins/',
    params={'access_token':accessToken,
            'fields':'pin.images[750x],pin.description,pin.image_signature',
            'page_size':100
            })

if(os.path.isdir(folderPath) == False):
    os.makedirs(folderPath)

imageDatas = response.json()['data']
for imageData in imageDatas:
    pprint.pprint(imageData)
    imageUrl = imageData['images']['750x']['url']
    imageDesc = imageData['description']
    imageSig = imageData['image_signature']

    extensions = imageUrl.split('.')
    extension = extensions[len(extensions)-1]

    f = open(folderPath+"/"+imageSig+"."+extension,'wb')
    f.write(urlopen(imageUrl).read())
    f.close()