from git_api import *
import PyQt5


def setup():
    try:
        f = open("config.json")
        config = json.load(f)
        # =================== variables =============================
        url = config.get('url')
        name = config.get('name')
        token = config.get('token')
        who_work_now = config.get('who_work_now')
        who_work_now_mail = config.get('who_work_now_mail')
        fnames = find_fls()  # можно задать в первом параметре поиск в какой директории производить а вторым какое расширение файла
        # ===========================================================
        workspace = GitApi_params(url, name, token, who_work_now, who_work_now_mail, fnames)
        return workspace

    except Exception as e:
        print("Handle this: ")
        print(e)


if __name__ == "__main__":
    env = setup()
    add(env,2)
    add_by_name(env,"git_api.py")
    env.url = env.content.get("dirs")[0]
    r = rq.get(
        env.url,
        auth=(env.name, env.token))


