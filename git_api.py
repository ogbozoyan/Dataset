import json
import io
import requests as rq
import os
import base64
from PIL import Image


class GitApi_params:
    """
    just for params
    """
    token: str
    content: dict

    def __init__(self, url='', name='', token='', who_work_now='', who_work_now_mail='', fnames=[]):
        self.url = url
        self.name = name
        self.token = token
        self.who_work_now = who_work_now
        self.who_work_now_mail = who_work_now_mail
        self.fnames = fnames
        self.content = load_git_content(self)


def file_to_base64(fname: str):
    """
    переводит файл в base64
    """
    try:
        with open(fname, "rb") as file:
            base64_file = base64.b64encode(file.read())
        return base64_file.decode("utf-8")
    except:
        print("File error")
        exit()


def find_fls(std_dir="raw_pic", std_ext=".jpg"):
    """
    Ищет в std_dir файлы расширения jpg, можно менять
    и возвращает список flist
    """
    flist = []
    for file in os.listdir(std_dir):
        if file.endswith(std_ext):
            flist.append(os.path.join(std_dir, file))
    return flist


def delete(params: GitApi_params):
    try:
        fname = params.fnames[1]
        print(fname)
        url = params.url + '/' + fname
        resp = rq.get(url,
                      auth=(params.name,
                            params.token)
                      )
        sha = resp.json().get('sha')
        print(url + " " + sha)
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
            data=json.dumps(fields)
        )
        print(resp.text)
        print("Deleted: " + fname)
    except Exception as e:
        print(e)


def download_files(url, val=1, image_file_path="raw_pic/save_from_git.jpg"):  # image_file_path - path to save of file
    """
    url - ссылка на директорию где нужно качать
    val - количество файлов, если
    """
    if (val == 1):
        r = rq.get(url)
        if r.status_code != rq.codes.ok:
            assert False, "Status code error: {}.".format(r.status_code)
        r = r.json()
        fls_link_to_download = []
        for i in r:
            fls_link_to_download.append(i.get('download_url'))
        r = rq.get(fls_link_to_download[0])
        with Image.open(io.BytesIO(r.content)) as im:
            im = im.convert("RGB")
            im.save(image_file_path)
    else:
        r = rq.get(url)
        count = 1
        image_file_path = "raw_pic/"
        if r.status_code != rq.codes.ok:
            assert False, "Status code error: {}.".format(r.status_code)
        r = r.json()
        print(r)
        fls_link_to_download = []
        for i in r:
            fls_link_to_download.append(i.get('download_url'))
        for i in fls_link_to_download:
            r = rq.get(i)
            with Image.open(io.BytesIO(r.content)) as im:
                im = im.convert("RGB")
                im.save(image_file_path + str(count) + 'downloaded.jpg')
                count += 1


def upload(env: GitApi_params, mode=0, sha=''):
    """
    upload - с помощью put запроса начинает отправлять все,
    что находится в env.fnames
    mode 0 - upload all
    mode 1-n - upload первые n файлов в env.fnames
     return 409 - Если файл уже лежит на гите
    422 - ошибка
    Если успешно - выводит сообщение об этом
    """
    if mode == 0:
        try:
            for fname in env.fnames:
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
                    # 409 - file already exist
                    print(f_resp.status_code)
        except:
            print("Upload error")
            exit()
    else:
        try:
            count = 0
            for fname in env.fnames:
                if (count < mode):
                    count += 1
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
                        # 409 - file already exist
                        print(f_resp.status_code)
        except:
            print("Upload error")
            exit()


def upload_by_name(env: GitApi_params, name):
    """
    все предельно просто, тоже самое что и upload,но добавляет
    только один файл с названием name
    """
    try:
        search = ''
        for fname in env.fnames:
            if fname == name:
                search = fname
                break
        if(search == ''):
            print("Not found: "+name)
            exit()
        else:
            fname = search
            url = env.url + '/' + fname  # makes dir if fname has dir
            fields = {
                "message": "commit from upload()",
                "committer": {
                    "name": env.who_work_now,
                    "email": env.who_work_now_mail
                },
                "sha": '',
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
                # 409 - file already exist
                print(f_resp.status_code)

    except:
        print("Upload error")
        exit()


def add(params, val=0):
    """
    Простой вызывает upload
    использовать:
    add(env,val- сколько файлов добавить)
    """
    try:
        upload(params, val)
        return params
    except Exception as e:
        print(e)


def add_by_name(params, name):
    """
    все очень просто
    вызывает upload_by_name, нужно только задать имя файла которое
    нужно загрузить
    """
    try:
        if(name not in params.fnames):
            params.fnames.append(name)
        upload_by_name(params, name)
    except Exception as e:
        print(e)


def load_git_content(env):
    """
    load_git_content - обновляет контент на текущей env.url, автоматический парсит
    все данные при первом объявлении объекта класса
    Дальнейшее использование:
    env.content = load_git_content(env)
    __files - файлы в текущей директории гита
    __dirs - директории
    """
    __files = []
    __dirs = []
    content = {
        "files": __files,
        "dirs": __dirs
    }
    req = rq.get(
        env.url,
        auth=(env.name, env.token)
    )
    for i in req.json():
        if i.get('type') == 'file':
            __files.append(i.get('name'))
            content.update({"files": __files})

        elif i.get("type") == 'dir':
            __dirs.append(i.get('url'))
            content.update({"dirs": __dirs})
    return content


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
                    upload(tmp_url, aut_name, token, who_work_now, who_work_now_mail, fname, sha)
    """


"""
Заметки
write json to file
    with open("res.json","w+") as f:
        json.dump(rs.text, f)
path = os.getcwd() - returns own path
"""
