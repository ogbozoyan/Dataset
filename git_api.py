from hashlib import sha1
import json
import requests as rq
import os
import base64


def find_fls(std_dir = "raw_pic",std_ext = ".jpg"):
    flist = []
    for file in os.listdir(std_dir):
        if file.endswith(std_ext):
            flist.append(os.path.join(std_dir, file))
    return flist

def file_to_base64(fname: str):
    try:
        with open(fname, "rb") as file:
            base64_file = base64.b64encode(file.read())
        return base64_file.decode("utf-8")
    except:
        print("File error")
        exit()


def _jsn(commit: str, who_work_now: str, who_work_now_mail: str, file_name: str):
    try:
        fields = {
            "message": commit,
            "committer": {
                "name": who_work_now,
                "email": who_work_now_mail
            },
            "content": file_to_base64(file_name)
        }
        return fields
    except:
        print('_json error')
        exit()

def upload(url: str, aut_name: str, token: str, who_work_now: str, who_work_now_mail: str, fname: str):
    try:
        tmp_url = url
        url = url + '/' + fname
        f_resp = rq.put(
            url,
            auth=(aut_name, token),
            headers={"Content-Type": "application/json"},
            data=json.dumps(_jsn("upload image_test", who_work_now, who_work_now_mail, fname))
        )
        print(f_resp.json())
        if f_resp.ok:
            print("Uploaded " + fname + " to " + url)
        else:
            print(fname + " already exist")

        """ Reuploading works slow
        elif (f_resp.ok) and sha != "":
            print("Reuploaded " + fname + " to " + url)
        else:
            req = rq.get(tmp_url, auth=(aut_name, token))
            sha = ''
            for r in req.json():
                name_search = r.get('name')
                if name_search == fname:
                    sha = r.get('sha')
                    break
            upload(tmp_url, aut_name, token, who_work_now, who_work_now_mail, fname, sha)"""
    except:
        print("Upload error")
        exit()
