import time
import glob
import os
import json
import requests
from base64 import b64encode

from utilities import file_names


def upload_images(album_title, paths):
  client_secret = os.environ['IMGUR_APIKEY']
  client_id = '8d534890d5e8bae'

  albumURL = "https://api.imgur.com/3/album.json"
  imageURL = "https://api.imgur.com/3/upload.json"
  headerData = {"Authorization": "Client-ID {}".format(client_id)}

  albumResponse = requests.post(
    albumURL, 
    headers = headerData,
    data = {
      'key': client_secret, 
      'title': album_title
    }
  )

  album = albumResponse.json()['data']

  for i, img in enumerate(paths):
    b64_image = None
    with open(img, "rb") as f:
      image_data = f.read()
      b64_image = b64encode(image_data)

    imageResponse = requests.post(
      imageURL, 
      headers = headerData,
      data = {
        'key': client_secret,
        'image': b64_image,
        "album": album['deletehash'],
      }
    )
    # print(imageResponse.status_code)
    # os.remove(img)

  return album


def postDebug():
  try:
    print('')
    title = "{} Iowa COVID19 Debug Screenshots".format(time.strftime("%m/%d"))
    fileList = glob.glob(os.path.join(file_names.screenshotDir, "Screenshot_*"))
    album = upload_images(title, fileList)
    url = "https://imgur.com/a/{}".format(album['id'])
    print('Debug Screenshots ' + url)
    print('')
  except Exception as e:
    print('something wrong with imgur {}'.format(e))


if __name__ == "__main__":
  postDebug()
  
  
