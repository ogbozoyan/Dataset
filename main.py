from git_api import *
import PyQt5

if __name__ == "__main__":
    try:
        f = open("config.json")
        config = json.load(f)
        # =================== variables =============================
        url = config.get('url')
        uname = config.get('name')
        token = config.get('token')
        who_work_now = config.get('who_work_now')
        who_work_now_mail = config.get('who_work_now_mail')
        fnames = find_fls()
        # =========================================================== path = os.getcwd() - returns own path
    except:
        print("File can't open")


    print(delete(url+'/'+fnames[0],uname,token))

    #for i in fnames:
    #    upload(url_dataset, us_name, token, who_work_now, who_work_now_mail, i)