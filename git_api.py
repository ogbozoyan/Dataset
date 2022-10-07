import json
import io
import requests as rq
import os
import base64
import subprocess
from PIL import Image

def find_fls(std_dir="raw_pic", std_ext=".jpg"):
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


def upload(url: str, aut_name: str, token: str, who_work_now: str, who_work_now_mail: str, fname: str,sha = ''):
    try:

        url = url + '/' + fname  # makes dir if fname has dir

        fields = {
            "message": "commit from upload()",
            "committer": {
                "name": who_work_now,
                "email": who_work_now_mail
            },
            "sha": sha,
            "content": file_to_base64(fname)
        }

        f_resp = rq.put(
            url,
            auth=(aut_name, token),
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

def download(url=''):
    meta = []  # indexes 0 - name 1 - metainfo
    subprocess.run(["ls", "-l"])

def delete(url: str,usname: str,token: str):

    resp = rq.delete(
            url,
            auth=(usname,token)
    )
    print(resp.text)

def download_image(url, image_file_path): #image_file_path - path to save of file
    r = rq.get(url)
    if r.status_code != rq.codes.ok:
        assert False, "Status code error: {}.".format(r.status_code)
    with Image.open(io.BytesIO(r.content)) as im:
        im = im.convert("RGB")
        im.save(image_file_path)

#r = rq.get("https://api.github.com/repos/ogbozoyan/Dataset/contents/raw_pic")
#print(r.headers)
#download_image("https://raw.githubusercontent.com/ogbozoyan/Dataset/main/my_image.jpg","1img.jpg")
"""
write json to file
    with open("res.json","w+") as f:
        json.dump(rs.text, f)
        """