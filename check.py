import json
import requests as rq
import os
import base64
from hashlib import sha1

def file_to_base64(fname: str):
    with open(fname, "rb") as img_file:
        base64_file = base64.b64encode(img_file.read())
    return base64_file.decode("utf-8")

def _jsn(commit: str, who_work_now: str, who_work_now_mail: str, file_name: str):
    fields = {
        "message": commit,
        "committer": {
            "name": who_work_now,
            "email": who_work_now_mail
        },
        "content": file_to_base64(file_name)
    }
    return fields

# =================== variables =============================
url_dataset = "https://api.github.com/repos/ogbozoyan/Dataset"
us_name = "ogbozoyan"
token = "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"
content = "Проверка GitHub API"
who_work_now = "Oganes Bozoyan"
who_work_now_mail = "ogi@mail.ru"

#name_of_file = str(input("File name: "))
# ===========================================================

r = rq.get(url_dataset, auth=(us_name, token))

for rep in r.json():
    if rep[0]['name'] == "1img":
        print(rep[0]['name'])


url = url_dataset + "/" +name_of_file

f_resp = rq.put(
    url,
    auth=(us_name, token),
    headers={"Content-Type": "application/json"},
    data=json.dumps(_jsn("upload image_test", who_work_now, who_work_now_mail, "my_image.jpg"))
)
print(f_resp.json())
