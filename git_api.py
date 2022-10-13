import json
import io
import requests as rq
import os
import base64
from PIL import Image
import sys


class GitApiParams:
    """
    just for params
    content - repo page
    """

    token: str
    content: dict

    def __init__(
        self,
        url="",
        name="",
        token="",
        who_work_now="",
        who_work_now_mail="",
        fnames=[],
    ):
        self.url = url
        self.name = name
        self.token = token
        self.who_work_now = who_work_now
        self.who_work_now_mail = who_work_now_mail
        self.fnames = fnames
        self.content = load_git_content(self)

    def __str__(self):
        info = (
            f"Url: {self.url} \n"
            f"Username: {self.name} \n"
            f"Who_work_now_commit_info: {self.who_work_now} \n"
            f"Who_work_now_mail_commit_info: {self.who_work_now_mail} \n"
            f"Files: {self.fnames} \n"
            f"Content: {self.content} \n"
        )
        return info


def file_to_base64(fname: str):
    """
    переводит файл в base64
    """
    try:
        with open(fname, "rb") as file:
            base64_file = base64.b64encode(file.read())
        return base64_file.decode("utf-8")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("============Error==============")
        print(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print("===============================")
        exit()


def find_fls(std_ext=".jpg", std_dir="raw_pic"):
    """
    Ищет в std_dir файлы расширения jpg, можно менять
    и возвращает список flist
    """
    if std_ext != "":
        flist = []
        for file in os.listdir(std_dir):
            if file.endswith(std_ext):
                flist.append(os.path.join(std_dir, file))
        return flist
    else:
        flist = []
        for file in os.listdir(std_dir):
            flist.append(os.path.join(std_dir, file))
        return flist


def download_files(url, val=1):
    """
    image_file_path - path to save of file
    url - ссылка на директорию где нужно качать
    val - количество файлов,если  = 1, то качает первый файл в директории
    если = 0 то качает все
    """
    if val == 1:
        r = rq.get(url)
        if r.status_code != rq.codes.ok:
            assert False, "Status code error: {}.".format(r.status_code)
        r = r.json()
        fls_link_to_download = []
        meta = {}
        for i in r:
            meta.update({"name": i.get("path"), "download_url": i.get("download_url")})
            fls_link_to_download.append(meta)
            break
        r = rq.get(fls_link_to_download[0].get("download_url"))
        try:
            with Image.open(io.BytesIO(r.content)) as im:
                im = im.convert("RGB")
                im.save(fls_link_to_download[0].get("name"))
        except Exception:
            with open(fls_link_to_download[0].get("name"), "wb") as f:
                f.write(r.content)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("============Error==============")
            print(e)
            print(exc_type, fname, exc_tb.tb_lineno)
            print("===============================")
            exit()

    elif val == 0:
        r = rq.get(url)
        count = 1
        if r.status_code != rq.codes.ok:
            assert False, "Status code error: {}.".format(r.status_code)
        r = r.json()
        meta = {}
        fls_link_to_download = []
        for i in r:
            fls_link_to_download.append(
                {"name": i.get("path"), "download_url": i.get("download_url")}
            )
        for i in fls_link_to_download:
            r = rq.get(i.get("download_url"))
            try:
                with Image.open(io.BytesIO(r.content)) as im:
                    im = im.convert("RGB")
                    im.save(i.get("name"))
                    print("Downloaded: " + i.get("name"))
                    count += 1
            except Exception:
                with open(i.get("name"), "wb") as f:
                    f.write(r.content)
                print("Downloaded: " + i.get("name"))
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("============Error==============")
                print(e)
                print(exc_type, fname, exc_tb.tb_lineno)
                print("===============================")
                exit()


def upload(env: GitApiParams, mode=0, sha=""):
    """
    upload - с помощью put запроса начинает отправлять все,
    что находится в env.fnames
    mode 0 - upload all
    mode от 1 до n - upload первые n файлов в env.fnames
     return 409 - Если файл уже лежит на гите
    422 - ошибка
    Если успешно - выводит сообщение об этом
    """
    try:
        if mode == 0:
            for fname in env.fnames:
                url = env.url + "/" + fname  # makes dir if fname has dir
                fields = {
                    "message": "commit from upload()",
                    "committer": {
                        "name": env.who_work_now,
                        "email": env.who_work_now_mail,
                    },
                    "content": file_to_base64(fname),
                    "sha": sha,
                }

                f_resp = rq.put(
                    url,
                    auth=(env.name, env.token),
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(fields),
                )
                if f_resp.ok:
                    print("Uploaded " + fname + " to " + url)
                elif f_resp.status_code == 409:
                    fields = {
                        "message": f"commit from upload_by_name({fname})",
                        "committer": {
                            "name": env.who_work_now,
                            "email": env.who_work_now_mail,
                        },
                        "content": file_to_base64(fname),
                        "sha": str(
                            rq.get(url, auth=(env.name, env.token)).json().get("sha")
                        ),
                    }
                    f_resp = rq.put(
                        url,
                        auth=(env.name, env.token),
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(fields),
                    )
                    if f_resp.ok:
                        print("Uploaded " + fname + " to " + url)
                    else:
                        print(fname)
                        print(f_resp.status_code)
                else:
                    # 409 - file already exist
                    print(fname)
                    print(f_resp.status_code)
        else:
            count = 0
            print(env.fnames)
            for fname in env.fnames:
                if count < mode:
                    count += 1
                    url = env.url + "/" + fname  # makes dir if fname has dir
                    fields = {
                        "message": "commit from upload()",
                        "committer": {
                            "name": env.who_work_now,
                            "email": env.who_work_now_mail,
                        },
                        "content": file_to_base64(fname),
                        "sha": sha,
                    }

                    f_resp = rq.put(
                        url,
                        auth=(env.name, env.token),
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(fields),
                    )
                    if f_resp.ok:
                        print("Uploaded " + fname + " to " + url)
                    elif f_resp.status_code == 409:
                        fields = {
                            "message": f"commit from upload_by_name({fname})",
                            "committer": {
                                "name": env.who_work_now,
                                "email": env.who_work_now_mail,
                            },
                            "content": file_to_base64(fname),
                            "sha": str(
                                rq.get(url, auth=(env.name, env.token))
                                .json()
                                .get("sha")
                            ),
                        }
                        f_resp = rq.put(
                            url,
                            auth=(env.name, env.token),
                            headers={"Content-Type": "application/json"},
                            data=json.dumps(fields),
                        )
                        if f_resp.ok:
                            print("Uploaded " + fname + " to " + url)
                        else:
                            print(fname)
                            print(f_resp.status_code)
                    else:
                        # 409 - file already exist
                        print(fname)
                        print(f_resp.status_code)
                else:
                    break
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("============Error==============")
        print(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print("===============================")


def upload_by_name(env: GitApiParams, name):
    """
    все предельно просто, тоже самое что и upload,но добавляет
    только один файл с названием name
    """
    try:
        search = ""
        for fname in env.fnames:
            if fname == name:
                search = fname
                break
        if search == "":
            print("Not found: " + name)
            return
        else:
            fname = search
            url = env.url + "/" + fname  # makes dir if fname has dir
            fields = {
                "message": "commit from upload()",
                "committer": {"name": env.who_work_now, "email": env.who_work_now_mail},
                "content": file_to_base64(fname),
                "sha": "",
            }

            f_resp = rq.put(
                url,
                auth=(env.name, env.token),
                headers={"Content-Type": "application/json"},
                data=json.dumps(fields),
            )
            if f_resp.ok:
                print("Uploaded " + fname + " to " + url)
            elif f_resp.status_code == 409:
                fields = {
                    "message": f"commit from upload_by_name({fname})",
                    "committer": {
                        "name": env.who_work_now,
                        "email": env.who_work_now_mail,
                    },
                    "content": file_to_base64(fname),
                    "sha": str(
                        rq.get(url, auth=(env.name, env.token)).json().get("sha")
                    ),
                }
                f_resp = rq.put(
                    url,
                    auth=(env.name, env.token),
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(fields),
                )
                if f_resp.ok:
                    print("Uploaded " + fname + " to " + url)
                else:
                    print(fname)
                    print(f_resp.status_code)
            else:
                print(fname)
                print(f_resp.status_code)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("============Error==============")
        print(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print("===============================")


def add(params, mode=0):
    """
    Простой вызывает upload
    использовать:
    add(env,val- сколько файлов добавить)
    """
    try:
        upload(params, mode)
        return params
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("============Error==============")
        print(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print("===============================")


def add_by_name(params, name):
    """
    все очень просто
    вызывает upload_by_name, нужно только задать имя файла которое
    нужно загрузить
    """
    try:
        if name not in params.fnames:
            params.fnames.append(name)
        upload_by_name(params, name)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("============Error==============")
        print(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print("===============================")


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
    content = {"files": __files, "dirs": __dirs}
    req = rq.get(env.url, auth=(env.name, env.token))
    for i in req.json():
        if i.get("type") == "file":
            __files.append(i.get("name"))
            content.update({"files": __files})

        elif i.get("type") == "dir":
            __dirs.append(i.get("url"))
            content.update({"dirs": __dirs})
    return content


'''
РАБОТАЕТ НО ХУЕВО ДОПИЛИТЬ НАДО ОШИБКА В СЧИТЫВАНИИЕ ФАЙЛОВ В ДИРЕКТОРИИ 
НУЖНО СЧИТАТЬ ЧТО НАХОДИТСЯ НЕ В params.fnames А В ДИРЕКТОРИИ url
def delete(params: GitApiParams, val=0):

    Удаляет первый элемент в директории val = 0  
     Если name = '' val = n удаляет первые n элементы

    if val < 0:
        print("val error")
        exit()
    try:
        for i in req.json():
            if i.get("type") == "file":

        if val <= 1:
            sha = ""
            for i in params.fnames:
                fname = i
                print(fname)
                url = params.url + "/" + fname
                resp = rq.get(url, auth=(params.name, params.token))
                sha = resp.json().get("sha")
                if sha is not None:
                    break

            print(url + " " + sha)
            fields = {
                "message": "commit from delete()",
                "committer": {
                    "name": params.who_work_now,
                    "email": params.who_work_now_mail,
                },
                "sha": sha,
            }
            resp = rq.delete(
                url, auth=(params.name, params.token), data=json.dumps(fields)
            )

            print("Deleted: " + fname)

        elif val > 0:
            for j in range(val):
                sha = ""
                for i in params.fnames:
                    fname = i
                    url = params.url + "/" + fname
                    resp = rq.get(url, auth=(params.name, params.token))
                    sha = resp.json().get("sha")
                    if sha is not None:
                        break

                print(url + " " + sha)
                fields = {
                    "message": "commit from delete()",
                    "committer": {
                        "name": params.who_work_now,
                        "email": params.who_work_now_mail,
                    },
                    "sha": sha,
                }
                resp = rq.delete(
                    url, auth=(params.name, params.token), data=json.dumps(fields)
                )
                print("Deleted: " + fname)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("============Error==============")
        print(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print("===============================")

"""
Заметки
write json to file
    with open("res.json","w+") as f:
        json.dump(rs.text, f)
path = os.getcwd() - returns own path
"""
'''
