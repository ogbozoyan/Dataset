import json
import io
import requests as rq
import os
import base64
from PIL import Image

class GitApi_params:
    token: str
    def __init__(self, url='', name='', token='', who_work_now='', who_work_now_mail='',fnames = []):
        self.url = url
        self.name = name
        self.token = token
        self.who_work_now = who_work_now
        self.who_work_now_mail = who_work_now_mail
        self.fnames = fnames

def file_to_base64(fname: str):
    try:
        with open(fname, "rb") as file:
            base64_file = base64.b64encode(file.read())
        return base64_file.decode("utf-8")
    except:
        print("File error")
        exit()


def find_fls(std_dir="raw_pic", std_ext=".jpg"):
    flist = []
    for file in os.listdir(std_dir):
        if file.endswith(std_ext):
            flist.append(os.path.join(std_dir,file))
    return flist


def delete(params: GitApi_params):
    try:
        fname = params.fnames[3]
        print(fname)
        url = params.url+'/'+fname
        resp = rq.get(url,
                      auth=(params.name,
                            params.token)
        )
        sha = resp.json().get('sha')
        print(url + " "+sha)
        fields = {
            "message": "commit from delete()",
            "committer": {
                "name": params.who_work_now,
                "email": params.who_work_now_mail
            },
            "sha": sha
        }
        resp = rq.delete(
            url,
            auth=(params.name,
                  params.token),
            data = json.dumps(fields)
        )
        print(resp.text)
        print("Deleted: "+fname)
    except Exception as e:
        print(e)

def download_image(url, image_file_path):  # image_file_path - path to save of file
    r = rq.get(url)
    if r.status_code != rq.codes.ok:
        assert False, "Status code error: {}.".format(r.status_code)
    with Image.open(io.BytesIO(r.content)) as im:
        im = im.convert("RGB")
        im.save(image_file_path)

def upload(env: GitApi_params,sha=''):
    try:
        fname = env.fnames[0]
        url = env.url + '/' + fname  # makes dir if fname has dir
        fields = {
                "message": "commit from upload()",
                "committer": {
                    "name": env.who_work_now,
                    "email": env.who_work_now_mail
                },
                "sha": sha,
                "content": file_to_base64(fname)
        }

        f_resp = rq.put(
                url,
                auth=(env.name, env.token),
                headers={"Content-Type": "application/json"},
                data=json.dumps(fields)
        )
        if f_resp.ok:
            print("Uploaded " + fname + " to " + url)
        else:
            print(f_resp)  # 422 - file already exist
            print(f_resp.status_code)
    except:
        print("Upload error")
        exit()
def add(params):
    try:
        upload(params)
        return params
    except Exception as e:
        print(e)

def reupload(url: str, aut_name: str, token: str, who_work_now: str, who_work_now_mail: str, fname: str):
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

"""
Заметки
write json to file
    with open("res.json","w+") as f:
        json.dump(rs.text, f)
path = os.getcwd() - returns own path
"""
