from git_api import *

if __name__ == "__main__":
    # =================== variables =============================
    url_dataset = "https://api.github.com/repos/ogbozoyan/Dataset/contents"
    us_name = "ogbozoyan"
    token = ""
    who_work_now = "Oganes Bozoyan"
    who_work_now_mail = "ogi@mail.ru"
    # ===========================================================
    path = os.getcwd()
    fnames = find_fls(path, ".py")
    print(fnames)
    for i in fnames:
        upload(url_dataset, us_name, token, who_work_now, who_work_now_mail, i[40:])
