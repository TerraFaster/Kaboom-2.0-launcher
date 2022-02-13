import urllib.request, requests, psycopg2
import concurrent.futures, subprocess, psutil, os
import zipfile, string, json, time, PIL

from PIL import ImageTk
from tkinter import *
from tkinter import messagebox
from cryptography.fernet import Fernet
from threading import Thread
from io import BytesIO
from ctypes import windll
from pyperclip import copy
from random import choice as rchoice


def set_appwindow(root):
    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080

    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
    
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())


class LauncherMenu:
    def __init__(self):
        self.elements = {}
        self.__is_hidden = True

    def add_element(self, element_name: str, element, settings: dict, **kwargs):
        self.elements[element_name] = [element, settings, kwargs]

        return self.elements[element_name][0]

    def get_element(self, element_name: str):
        return self.elements[element_name][0]

    def show(self):
        if self.__is_hidden:
            self.__is_hidden = False

            for e in self.elements.values():
                if "page" in e[2] and e[2]["page"] != self.page:
                    continue

                e[0].place(**e[1])

    def hide(self):
        if not self.__is_hidden:
            self.__is_hidden = True

            for e in self.elements.values():
                e[0].place_forget()


def split(l: list, n: int):
    return [l[i:i + n] for i in range(0, len(l), n)]


def drag_window(e, w):
    x = w.winfo_pointerx() - w._offsetx
    y = w.winfo_pointery() - w._offsety

    w.geometry(f"+{x}+{y}")


def click_window(e, w):
    w._offsetx = e.x
    w._offsety = e.y


CIPHER = Fernet(b"BifPqTUU2vDIbQlmHFb-qHbdTPEdggy10NyIsa-eLEU=")
VERSION = "0.0.1"

ROOT_DIR = os.getcwd()

BG_COLOR = "#1a1a1a"
FONT_COLOR = "#E0E2E4"
SIDEPANEL_COLOR = "#2a2a2a"

auth_menu = LauncherMenu()
sidebar_menu = LauncherMenu()
modpacks_menu = LauncherMenu()
downloads_menu = LauncherMenu()
settings_menu = LauncherMenu()
rpc_menu = LauncherMenu()


Config = {
    "username": None,
    "password": None,
    "uuid": None,
    "access_token": None,
    "remember": False,
    "memory": 4,
}

Temp = {
    "downloading": []
}


def db_execute(sql: str, fetch_all: bool=False):
    conn = psycopg2.connect("postgres://sqmpbccifbzupx:c73ce70b96b24b57880648d07324232fbcf3f3b24a0e2a4b32ae20e727173d58@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/d9f0uq1kajf9id", sslmode="require")
    cur = conn.cursor()

    cur.execute(sql)
    conn.commit()

    try:
        r = cur.fetchall() if fetch_all else cur.fetchone()

    except:
        r = None

    conn.close()
    cur.close()

    return r


def create_popup(w: int=400, h: int=400):
    window = Toplevel(tk)

    window.title("TerraLauncher")
    window.geometry(f"{w}x{h}+{screen_size[0] // 2 - w // 2}+{screen_size[1] // 2 - h // 2}")
    window.resizable(False, False)

    window.overrideredirect(True)

    window.bind("<Button-1>", lambda e, w=window: click_window(e, w))
    window.bind("<B1-Motion>", lambda e, w=window: drag_window(e, w))

    window.protocol("WM_DELETE_WINDOW", lambda: 0)

    background = Label(window, bg=BG_COLOR)
    background.place(x=0, y=0, relwidth=1, relheight=1)

    window.after(10, lambda: set_appwindow(window))

    return window


def get_modpacks_data() -> dict:
    f_id = "12HgarGqJV20WuTjN69sAH4YKAWLX6P4B"

    data = urllib.request.urlopen(f"https://www.googleapis.com/drive/v3/files/{f_id}?alt=media&key=AIzaSyCBkHuKnayFBEghYaAR1wKgCyU51RITJ6Q")

    return json.loads(data.read().decode("utf-8"))
    
    # data = {
    #     "versions": ["1.7.10", "1.12.2"],
    #     "1.7.10": {
    #         "tesla": ["Tesla", 76.9688, "1.7.10"], "skyfactory": ["SkyFactory", 106.11, "1.7.10"], "spacex": ["SpaceX", 117.87, "1.7.10"], 
    #         "dragonglory": ["DragonGlory", 149.03, "1.7.10"], "darkshire": ["Darkshire", 145.82, "1.7.10"], "nevermine": ["Nevermine", 155.98, "1.7.10"]
    #     },
    #     "1.12.2": {
    #         "edison": ["Edison", 86.793, "1.12.2"], "pixelmon": ["Pixelmon", 409.9, "1.12.2"], "claustrophobia": ["Клаустрофобия", 179.48, "1.12.2"],
    #         "cybermagic": ["Кибермагия", 181.85, "1.12.2"], "nightmare": ["Nightmare", 90.4922, "1.12.2"], "terrafirmacraft": ["Примитив", 116.71, "1.12.2"]
    #     },
    #     "all": [],
    #     "all_names": [],
    #     "by_name": {},
    #     "tweak_class": {
    #         "1.7.10": "cpw.mods",
    #         "1.12.2": "net.minecraftforge"
    #     }
    # }

    # for ver in data["versions"]:
    #     for k, v in data[ver].items():
    #         data["all"].append([k, *v])
    #         data["all_names"].append(k)
    #         data["by_name"][k] = [k, *v]

    # return data

# IN PROGRESS
def get_updates() -> None:
    f_id = "1Dl8IghSkPFalIJDZtwGAN1YILeXBnXPh"

    data = urllib.request.urlopen(f"https://www.googleapis.com/drive/v3/files/{f_id}?alt=media&key=AIzaSyCBkHuKnayFBEghYaAR1wKgCyU51RITJ6Q")

    return json.loads(data.read().decode("utf-8"))


def get_local_modpacks() -> list:
    local_modpacks = []

    for ver in modpacks["modpacks"]["versions"]:
        if not os.path.exists(f"{ROOT_DIR}/modpacks/{ver}/modpacks"):
            os.makedirs(f"{ROOT_DIR}/modpacks/{ver}/modpacks")

        else:
            local_modpacks += [
                modpacks["modpacks"]["by_name"][d] for d in os.listdir(f"{ROOT_DIR}/modpacks/{ver}/modpacks") if d in modpacks["modpacks"]["all_names"]
            ]

    return local_modpacks


def read_config() -> None:
    global Config

    if not os.path.exists(f"{ROOT_DIR}/config"):
        with open(f"{ROOT_DIR}/config", "w", encoding="utf-8") as cfg_file:
            json.dump(CIPHER.encrypt(bytes(json.dumps(Config), "utf-8")).decode(), cfg_file)

    with open(f"{ROOT_DIR}/config", "r", encoding="utf-8") as cfg_file:
        decrypted = CIPHER.decrypt(bytes(cfg_file.read(), "utf-8")).decode().replace("'", '"')

    try:
        config_json = json.loads(decrypted)

        if not all([k in config_json for k in Config]):
            raise Exception

        Config = dict.copy(config_json)

    except:
        with open(f"{ROOT_DIR}/config", "w", encoding="utf-8") as cfg_file:
            json.dump(CIPHER.encrypt(bytes(json.dumps(Config), "utf-8")).decode(), cfg_file)

def save_config() -> None:
    with open(f"{ROOT_DIR}/config", "w", encoding="utf-8") as cfg_file:
        json.dump(CIPHER.encrypt(bytes(json.dumps(Config), "utf-8")).decode(), cfg_file)


def download_file(id: str, path: str):
    try:
        if path.split("/")[:-1] in Temp["downloading"]:
            return False

        Temp["downloading"].append(path.split("/")[-1])

        file = urllib.request.urlopen(f"https://www.googleapis.com/drive/v3/files/{id}?alt=media&key=AIzaSyCBkHuKnayFBEghYaAR1wKgCyU51RITJ6Q")

        fp = "/".join(path.split("/")[:-1])

        if fp and not os.path.exists(fp):
            os.makedirs(fp)

        with open(path, "wb") as f:
            f.write(file.read())

    except:
        messagebox.showerror("Ошибка!", f"Произошла непредвиденная ошибка при скачивании {path.split('/')[-1].title()}!\nПожалуйста, обратитесь к разработчику!")
        Temp["downloading"].pop(Temp["downloading"].index(path.split('/')[-1]))

        return False

    else:
        Temp["downloading"].pop(Temp["downloading"].index(path.split("/")[-1]))

        return True

def unzip(fp: str):
    with zipfile.ZipFile(fp, "r") as f:
        f.extractall(fp.replace(".zip", ""))

    if os.path.exists(fp):
        os.remove(fp)


def download_modpack(name: str, btn: Button) -> None:
    version = modpacks["modpacks"]["by_name"][name][3]
    f_id = modpacks["links"]["modpacks"][version][name]

    messagebox.showinfo("Скачивание", f"Началось скачивание сборки {name}\n на версии {version}!")
    btn.config(text="Скачивается", state=DISABLED)

    success = download_file(f_id, f"modpacks/{version}/modpacks/{name}.zip")

    if not success:
        btn.config(text="Скачать", state=NORMAL)

    else:
        unzip(f"modpacks/{version}/modpacks/{name}.zip")

        messagebox.showinfo("Скачивание", f"Скачивание {name} завершено успешно!")
        btn.config(text="Скачано", state=DISABLED)


def download_needed_files():
    need_to_download = False

    for ver in modpacks["modpacks"]["versions"]:
        if not os.path.exists(f"modpacks/{ver}/assets") or not os.path.exists(f"modpacks/{ver}/libs") or not os.path.exists(f"modpacks/{ver}/natives"):
            need_to_download = True

    if need_to_download:
        tk.iconify()

        window = create_popup()

        Label(window, text="TerraLauncher", font="Arial 18", fg=FONT_COLOR, bg=BG_COLOR).place(x=120, y=25)
        Label(window, text="Подождите, лаунчер скачивает\nнеобходимые файлы.", font="Arial 16", fg=FONT_COLOR, bg=BG_COLOR).place(x=50, y=175)

    else:
        tk.deiconify()
        return

    for ver in modpacks["modpacks"]["versions"]:
        if not os.path.exists(f"modpacks/{ver}/assets") or not os.path.exists(f"modpacks/{ver}/libs") or not os.path.exists(f"modpacks/{ver}/natives"):
            download_file(modpacks["links"]["modpacks-data"][ver], f"modpacks/{ver}.zip")
            unzip(f"modpacks/{ver}.zip")

    window.destroy()
    window.update()

    tk.deiconify()


def start_modpack(modpack_name: str, modpack_version: str, btn: Button) -> None:
    tweak_class = modpacks["modpacks"]["tweak_classes"][modpack_version]

    cmd = f"javaw -Xmx{Config['memory']}G -Xms{Config['memory']}G -Dlog4j.skipJansi=true -Dfml.ignoreInvalidMinecraftCertificates=true \
        -Dfml.ignorePatchDiscrepancies=true -Dsun.net.maxDatagramSockets=32768 -Djava.library.path=\"../../natives\" \
        -cp \"../../libs/*\" net.minecraft.launchwrapper.Launch --tweakClass {tweak_class}.fml.common.launcher.FMLTweaker \
        --version {modpack_version} --username {Config['username']} --assetsDir \"../../assets\" \
        --assetIndex {modpack_version} --uuid {Config['uuid']} --accessToken {Config['access_token']} --userProperties {{}} --userType mojang"

    os.chdir(f"modpacks/{modpack_version}/modpacks/{modpack_name}")
    subprocess.Popen(cmd)
    os.chdir(ROOT_DIR)

    btn.config(text="Запущено", state=DISABLED)
    time.sleep(5)
    btn.config(text="Запустить", state=NORMAL)


def register():
    global Config

    window = create_popup()

    Label(window, text="TerraLauncher", font="Arial 18", fg=FONT_COLOR, bg=BG_COLOR).place(x=120, y=25)

    info_text = Label(window, text="Запустите любую сборку\nс обычного лаунчера.\nРегистрация произойдет\nавтоматически.", 
        font="Arial 16", fg=FONT_COLOR, bg=BG_COLOR)
    info_text.place(x=55, y=175)

    wait_var = IntVar()
    wait_btn = Button(window, text="Продолжить", font="Arial 10 bold", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=1, width=14, height=1, 
        command=lambda: wait_var.set(1))

    tk.iconify()
    window.grab_set()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_data_from_process)
        fut_res = future.result()

        r = db_execute(f"select Password from Users where Login = '{fut_res['username']}'")

        if not r:
            Config = {k: fut_res.get(k, v) for k, v in Config.items()}
            Config["password"] = "".join([rchoice(string.ascii_letters + string.digits) for i in range(16)])
            Config["remember"] = remember.get()

            db_execute(f"insert into Users values ('{Config['username']}', '{Config['password']}', '{Config['uuid']}', '{Config['access_token']}')")

            if Config["remember"]:
                save_config()

            info_text.destroy()

            info_text = Label(window, text=f"Ваш логин: {Config['username']}\nВаш пароль: {Config['password']}\n\nВсе было скопировано\nв буфер обмена.", 
                font="Arial 16", fg=FONT_COLOR, bg=BG_COLOR)
            info_text.place(x=45, y=150)

            copy(f"Ваш логин: {Config['username']}\nВаш пароль: {Config['password']}")

            wait_btn.place(x=145, rely=0.8)
            wait_btn.wait_variable(wait_var)

            auth_menu.hide()

            create_sidebar_menu()
            sidebar_menu.show()

        else:
            info_text.destroy()

            info_text = Label(window, text="Такой пользователь\nуже существует.\nНажмите \"Продолжить\" чтобы\nвернуться обратно.", 
                font="Arial 16", fg=FONT_COLOR, bg=BG_COLOR)
            info_text.place(x=55, y=175)

            wait_btn.place(x=145, rely=0.8)
            wait_btn.wait_variable(wait_var)


        window.destroy()
        window.update()

        window.grab_release()
        tk.deiconify()

def auth(username: str, password: str) -> None:
    if username == "" or password == "":
        return

    try:
        r = db_execute(f"select Password, UUID, Token from Users where Login = '{username}'")
        
        if r:
            if password == r[0]:
                Config["username"] = username
                Config["password"] = password
                Config["uuid"] = r[1]
                Config["access_token"] = r[2]
                Config["remember"] = remember.get()

                if Config["remember"]:
                    save_config()

                auth_menu.hide()

                create_sidebar_menu()
                sidebar_menu.show()

            else:
                messagebox.showerror("Ошибка!", "Неверный пароль!")

        else:
            messagebox.showerror("Ошибка!", "Такого пользователя\nне существует")

    except:
        messagebox.showerror("Ошибка!", "Не удалось подключиться к серверам!\nПожалуйста проявите терпение, скоро мы все починим.")

def de_auth():
    Config["username"] = None
    Config["password"] = None
    Config["uuid"] = None
    Config["access_token"] = None

    save_config()

    hide_all_menus()
    sidebar_menu.hide()
    
    create_auth_menu()
    auth_menu.show()



def get_data_from_process() -> dict:
    while True:
        for proc in psutil.process_iter():
            if proc.name() == "javaw.exe":
                cmd_line = os.popen("wmic process where(name=\"javaw.exe\") get commandline").read()

                data = {
                    "username": cmd_line.split("--username ")[1].split(" ")[0],
                    "uuid": cmd_line.split("--uuid ")[1].split(" ")[0],
                    "access_token": cmd_line.split("--accessToken ")[1].split(" ")[0]
                }

                os.popen("taskkill /IM Kaboom.Client.Launcher.exe /F")
                os.popen("taskkill /IM javaw.exe /F")

                return data

        time.sleep(0.25)

def update_token():
    global Config

    window = create_popup()

    Label(window, text="TerraLauncher", font="Arial 18", fg=FONT_COLOR, bg=BG_COLOR).place(x=120, y=25)

    Label(window, text="Запустите любую сборку\nс обычного лаунчера.", font="Arial 16", fg=FONT_COLOR, bg=BG_COLOR).place(x=75, y=175)

    # tk.wm_attributes("-disabled", True)
    tk.iconify()
    window.grab_set()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_data_from_process)
        
        Config = {k: future.result().get(v, v) for k, v in Config.items()}

        save_config()

    window.destroy()
    window.update()

    window.grab_release()
    tk.deiconify()
    # tk.wm_attributes("-disabled", False)



def create_auth_menu() -> None:
    auth_menu.add_element("title", Label(tk, text="TerraLauncher", font="Arial 28", bg=BG_COLOR, fg=FONT_COLOR), {"x": 205, "y": 20})

    auth_menu.add_element("username_label", Label(tk, text="● Логин", font="Arial 14", bg=BG_COLOR, fg=FONT_COLOR), {"x": 250, "y": 105})
    auth_menu.add_element("username_entry", Entry(tk, font="Arial 8 bold", bg=BG_COLOR, fg=FONT_COLOR, insertbackground=FONT_COLOR, width=24), {"x": 250, "y": 135})

    auth_menu.add_element("password_label", Label(tk, text="● Пароль", font="Arial 14", bg=BG_COLOR, fg=FONT_COLOR), {"x": 250, "y": 170})
    auth_menu.add_element("password_entry", Entry(tk, show="●", bg=BG_COLOR, fg=FONT_COLOR, insertbackground=FONT_COLOR, width=24), {"x": 250, "y": 205})

    auth_menu.add_element("remember", Checkbutton(tk, text="Запомнить", bg=BG_COLOR, fg=FONT_COLOR, activebackground=BG_COLOR, 
        selectcolor=SIDEPANEL_COLOR, variable=remember, onvalue=1, offvalue=0), {"x": 250, "y": 230})

    auth_menu.add_element("login_btn", Button(tk, text="Войти", font="Arial 10 bold", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=1, width=14, height=1, 
        command=lambda: auth(auth_menu.get_element("username_entry").get(), auth_menu.get_element("password_entry").get())), {"x": 267, "y": 275})
    auth_menu.add_element("register_btn", Button(tk, text="Зарегистрироваться", font="Arial 10 bold", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=1, width=20, height=1, 
        command=register), {"x": 242, "y": 310})



def create_sidebar_menu() -> None:
    sidebar_menu.add_element("panel", Label(tk, bg=SIDEPANEL_COLOR), {"x": 0, "y": 0, "relheight": 1, "relwidth": 0.2})

    sidebar_menu.add_element("local_modpacks_btn", Button(tk, text="Запустить сборку", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=0, width=14, height=2, 
        command=lambda: [hide_all_menus(), create_modpacks_menu(), modpacks_menu.show()]), {"x": 0, "y": 25, "relwidth": 0.2})
    sidebar_menu.add_element("download_modpacks_btn", Button(tk, text="Скачать сборку", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=0, width=14, height=2, 
        command=lambda: [hide_all_menus(), create_downloads_menu(), downloads_menu.show()]), {"x": 0, "y": 75, "relwidth": 0.2})

    sidebar_menu.add_element("settings_btn", Button(tk, text="Настройки", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=0, width=14, height=2, 
        command=lambda: [hide_all_menus(), create_settings_menu(), settings_menu.show()]), {"x": 0, "y": 125, "relwidth": 0.2})
    sidebar_menu.add_element("rpc_btn", Button(tk, text="Discord RPC", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=0, width=14, height=2, 
        command=lambda: [hide_all_menus(), create_rpc_menu(), rpc_menu.show()]), {"x": 0, "y": 175, "relwidth": 0.2})

    sidebar_menu.add_element("nickname_label", Label(tk, text=Config["username"], font=("Calibri", "12"), bg=BG_COLOR, fg=FONT_COLOR), 
        {"x": 0, "y": 275, "relwidth": 0.2})
    sidebar_menu.add_element("skin_head_canvas", Canvas(tk, bg=BG_COLOR, borderwidth=0, highlightbackground=BG_COLOR, width=125, height=125), 
        {"x": 0, "y": 300, "relwidth": 0.2})


    skin_image = PIL.Image.open(BytesIO(requests.get(f"https://static.kaboom2.ru/images/skins/{Config['uuid']}.png").content))

    size = int(skin_image.size[0] / 8)
    im_crop = skin_image.crop((size, size, size * 2, size * 2))
    im_res = im_crop.resize((130, 130), PIL.Image.BOX)

    skin_head_img = ImageTk.PhotoImage(im_res)
    sidebar_menu.get_element("skin_head_canvas").image = skin_head_img
    sidebar_menu.get_element("skin_head_canvas").create_image(0, 0, anchor="nw", image=skin_head_img)


def create_modpacks_menu(page: int=1) -> None:
    page = int(page)
    local_modpacks = get_local_modpacks()

    if not local_modpacks:
    #     modpacks_menu.add_element("nothing_found_label", 
    #         Label(tk, text="У вас еще не скачана ни одна сборка.\nЧтобы скачать сборку, перейдите \nво вкладку \"Скачать сборку\".", font="Arial 14", bg=BG_COLOR, fg=FONT_COLOR), 
    #         {"x": 225, "y": 200})

        return

    modpacks_menu.pages = (len(local_modpacks) - 1) // 6 + 1
    modpacks_menu.page = page

    modpacks_on_page = split(split(local_modpacks, 3), 2)[page - 1]

    for i, mp in enumerate(modpacks_on_page[0]):
        canv = modpacks_menu.add_element(f"mp_canvas_{(page - 1) * 6 + i + 1}", Canvas(tk, bg=SIDEPANEL_COLOR, bd=0, highlightbackground=SIDEPANEL_COLOR, 
            height=140, width=100), {"x": 170 * (i + 1), "y": 75}, page=page)

        canv.create_text(50, 15, text=(f"{mp[1]}"), font="Arial 11 bold", fill=FONT_COLOR, justify=CENTER)
        canv.create_text(50, 35, text=(f"{mp[3]}"), font="Arial 11 bold", fill=FONT_COLOR, justify=CENTER)

        start_btn = modpacks_menu.add_element(f"mp_start_btn_{(page - 1) * 6 + i + 1}", Button(tk, text="Запустить", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=0, 
            height=1, width=10, state=NORMAL), {"x": 170 * (i + 1) + 12, "y": 185}, page=page)

        start_btn.config(command=lambda mp=mp, btn=start_btn: Thread(target=start_modpack, args=[mp[0], mp[3], btn]).start())

    if len(modpacks_on_page) > 1:
        for i, mp in enumerate(modpacks_on_page[1]):
            canv = modpacks_menu.add_element(f"mp_bottom_canvas_{(page - 1) * 6 + i + 1}", Canvas(tk, bg=SIDEPANEL_COLOR, bd=0, highlightbackground=SIDEPANEL_COLOR, 
                height=140, width=100), {"x": 170 * (i + 1), "y": 75 + 175}, page=page)

            canv.create_text(50, 15, text=(f"{mp[1]}"), font="Arial 11 bold", fill=FONT_COLOR, justify=CENTER)
            canv.create_text(50, 35, text=(f"{mp[3]}"), font="Arial 11 bold", fill=FONT_COLOR, justify=CENTER)

            start_btn = modpacks_menu.add_element(f"mp_start_btn_{(page - 1) * 6 + i + 1}", Button(tk, text="Запущено", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=0, 
                height=1, width=10, state=NORMAL), {"x": 170 * (i + 1) + 12, "y": 360}, page=page)

            start_btn.config(command=lambda mp=mp, btn=start_btn: Thread(target=start_modpack, args=[mp[0], mp[3], btn]).start())

    for i in range(modpacks_menu.pages):
        page_btn = modpacks_menu.add_element(f"page_btn_{i + 1}", Button(tk, text=str(i + 1), bg=SIDEPANEL_COLOR, fg=FONT_COLOR, borderwidth=0, 
            height=1, width=3, state=NORMAL), {"x": 350 + i * 60, "y": 415})

        page_btn.config(command=lambda p=page_btn["text"]: [hide_all_menus(), create_modpacks_menu(p), modpacks_menu.show()])


def create_downloads_menu(page: int=1) -> None:
    page = int(page)

    downloads_menu.pages = (len(modpacks["modpacks"]["all"]) - 1) // 6 + 1
    downloads_menu.page = page
    
    downloads_menu.add_element("title", Label(tk, text="Скачать сборку", font="Arial 20", fg=FONT_COLOR, bg=BG_COLOR), {"x": 290, "y": 5})

    modpacks_on_page = split(split(modpacks["modpacks"]["all"], 3), 2)[page - 1]

    local_modpacks = get_local_modpacks()

    for i, mp in enumerate(modpacks_on_page[0]):
        canv = downloads_menu.add_element(f"mp_canvas_{(page - 1) * 6 + i + 1}", Canvas(tk, bg=SIDEPANEL_COLOR, bd=0, highlightbackground=SIDEPANEL_COLOR, 
            height=140, width=100), {"x": 170 * (i + 1), "y": 75}, page=page)

        canv.create_text(50, 15, text=(f"{mp[1]}"), font="Arial 11 bold", fill=FONT_COLOR, justify=CENTER)
        canv.create_text(50, 35, text=(f"{mp[3]}"), font="Arial 11 bold", fill=FONT_COLOR, justify=CENTER)
        canv.create_text(50, 80, text=f"Размер сборки\n{mp[2]} Mb", font="Arial 8 bold", fill=FONT_COLOR, justify=CENTER)

        download_btn = downloads_menu.add_element(f"mp_download_btn_{(page - 1) * 6 + i + 1}", Button(tk, text="Скачано", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=0, 
            height=1, width=10, state=DISABLED), {"x": 170 * (i + 1) + 12, "y": 185}, page=page)

        if f"{mp[0]}.zip" in Temp["downloading"]:
            download_btn.config(text="Скачивается")

        elif mp[0] not in [i[0] for i in local_modpacks]:
            download_btn.config(text="Скачать", state=NORMAL,
                command=lambda mp=mp, btn=download_btn: Thread(target=download_modpack, args=[mp[0], btn]).start()
            )

    if len(modpacks_on_page) > 1:
        for i, mp in enumerate(modpacks_on_page[1]):
            canv = downloads_menu.add_element(f"mp_bottom_canvas_{(page - 1) * 6 + i + 1}", Canvas(tk, bg=SIDEPANEL_COLOR, bd=0, highlightbackground=SIDEPANEL_COLOR, 
                height=140, width=100), {"x": 170 * (i + 1), "y": 75 + 175}, page=page)

            canv.create_text(50, 15, text=(f"{mp[1]}"), font="Arial 11 bold", fill=FONT_COLOR, justify=CENTER)
            canv.create_text(50, 35, text=(f"{mp[3]}"), font="Arial 11 bold", fill=FONT_COLOR, justify=CENTER)
            canv.create_text(50, 80, text=f"Размер сборки\n{mp[2]} Mb", font="Arial 8 bold", fill=FONT_COLOR, justify=CENTER)

            download_btn = downloads_menu.add_element(f"mp_bottom_download_btn_{(page - 1) * 6 + i + 1}", Button(tk, text="Скачано", bg=BG_COLOR, fg=FONT_COLOR, borderwidth=0, 
                height=1, width=10, state=DISABLED), {"x": 170 * (i + 1) + 12, "y": 360}, page=page)

            if f"{mp[0]}.zip" in Temp["downloading"]:
                download_btn.config(text="Скачивается")

            elif mp[0] not in [i[0] for i in local_modpacks]:
                download_btn.config(text="Скачать", state=NORMAL,
                    command=lambda mp=mp, btn=download_btn: Thread(target=download_modpack, args=[mp[0], btn]).start()
                )

    for i in range(downloads_menu.pages):
        page_btn = downloads_menu.add_element(f"page_btn_{i + 1}", Button(tk, text=str(i + 1), bg=SIDEPANEL_COLOR, fg=FONT_COLOR, borderwidth=0, 
            height=1, width=3, state=NORMAL), {"x": 350 + i * 60, "y": 415})

        page_btn.config(command=lambda p=page_btn["text"]: [hide_all_menus(), create_downloads_menu(p), downloads_menu.show()])


def create_settings_menu() -> None:
    settings_menu.add_element("title", Label(tk, text="Настройки", font="Arial 20", bg=BG_COLOR, fg=FONT_COLOR), {"x": 310, "y": 5})

    settings_menu.add_element("memory_label", Label(tk, text="Оперативная память\n(Гигабайты)", font="Arial 15", bg=BG_COLOR, fg=FONT_COLOR), {"x": 165, "y": 100})
    memory_entry = settings_menu.add_element("memory_entry", Entry(tk, bg=BG_COLOR, fg=FONT_COLOR, insertbackground=FONT_COLOR, width=17, validate="key"), {"x": 210, "y": 165})
    memory_entry.insert(0, str(Config["memory"]))
    memory_entry.config(validatecommand=(memory_entry.register(lambda v: v.isdigit()), "%P"))

    settings_menu.add_element("log_out_label", Label(tk, text="Выйти из аккаунта", font="Arial 15", bg=BG_COLOR, fg=FONT_COLOR), {"x": 445, "y": 100})
    settings_menu.add_element("log_out_btn", Button(tk, text="Выйти", bg=BG_COLOR, fg=FONT_COLOR, command=de_auth), {"x": 507, "y": 135})

    settings_menu.add_element("update_token_label", Label(tk, text="Обновить токен", font="Arial 15", bg=BG_COLOR, fg=FONT_COLOR), {"x": 445, "y": 210})
    settings_menu.add_element("update_token_btn", Button(tk, text="Обновить", bg=BG_COLOR, fg=FONT_COLOR, command=lambda: Thread(target=update_token).start()), 
        {"x": 500, "y": 245})

    settings_menu.add_element("design_label", Label(tk, text="Дизайн игры", font="Arial 15", bg=BG_COLOR, fg=FONT_COLOR), {"x": 165, "y": 210})
    settings_menu.add_element("design_btn_1", Radiobutton(text="Стандартный", bg=BG_COLOR, fg=FONT_COLOR, activeforeground=FONT_COLOR, activebackground=BG_COLOR, 
        selectcolor=BG_COLOR, variable=design, value=1), {"x": 175, "y": 235})
    settings_menu.add_element("design_btn_2", Radiobutton(text="Наш", bg=BG_COLOR, fg=FONT_COLOR, activeforeground=FONT_COLOR, activebackground=BG_COLOR, 
        selectcolor=BG_COLOR, variable=design, value=2), {"x": 175, "y": 255})


def create_rpc_menu() -> None:
    rpc_menu.add_element("title", Label(tk, text="Discord RPC", font="Arial 20", fg=FONT_COLOR, bg=BG_COLOR), {"x": 305, "y": 5})

    rpc_menu.add_element("rpc_mode_label", Label(tk, text="Режим RPC", font="Arial 15", fg=FONT_COLOR, bg=BG_COLOR), {"x": 165, "y": 100})

    rpc_menu.add_element("rpc_mode_btn_1", Radiobutton(text="Обычный", bg=BG_COLOR, fg=FONT_COLOR, selectcolor=BG_COLOR, 
        activeforeground=FONT_COLOR, activebackground=BG_COLOR, variable=rpc_mode, value=1, 
        command=lambda: [rpc_menu.get_element("nickname_entry").config(state=DISABLED), rpc_menu.get_element("phrase_entry").config(state=DISABLED)]), {"x": 175, "y": 125})
    rpc_menu.add_element("rpc_mode_btn_2", Radiobutton(text="Собственный", bg=BG_COLOR, fg=FONT_COLOR, selectcolor=BG_COLOR, 
        activeforeground=FONT_COLOR, activebackground=BG_COLOR, variable=rpc_mode, value=2, 
        command=lambda: [rpc_menu.get_element("nickname_entry").config(state=NORMAL), rpc_menu.get_element("phrase_entry").config(state=NORMAL)]), {"x": 175, "y": 145})
    rpc_menu.add_element("rpc_mode_btn_3", Radiobutton(text="Собственный ник", bg=BG_COLOR, fg=FONT_COLOR, selectcolor=BG_COLOR, 
        activeforeground=FONT_COLOR, activebackground=BG_COLOR, variable=rpc_mode, value=3, 
        command=lambda: [rpc_menu.get_element("nickname_entry").config(state=NORMAL), rpc_menu.get_element("phrase_entry").config(state=DISABLED)]), {"x": 175, "y": 165})

    rpc_menu.add_element("nickname_label", Label(tk, text="Никнейм", font="Arial 15", bg=BG_COLOR, fg=FONT_COLOR), {"x": 445, "y": 100})
    rpc_menu.add_element("nickname_entry", Entry(tk, font="Arial 10 bold", bg=BG_COLOR, fg=FONT_COLOR, insertbackground=FONT_COLOR, 
        disabledbackground=SIDEPANEL_COLOR), {"x": 415, "y": 135})
    rpc_menu.get_element("nickname_entry").config(state=DISABLED)

    rpc_menu.add_element("phrase_label", Label(tk, text="Фраза", font="Arial 15", bg=BG_COLOR, fg=FONT_COLOR), {"x": 445, "y": 175})
    rpc_menu.add_element("phrase_entry", Entry(tk, font="Arial 10 bold", bg=BG_COLOR, fg=FONT_COLOR, insertbackground=FONT_COLOR, 
        disabledbackground=SIDEPANEL_COLOR), {"x": 415, "y": 210})
    rpc_menu.get_element("phrase_entry").config(state=DISABLED)

    rpc_menu.add_element("start_rpc_btn", Button(tk, text="Запустить", bg=BG_COLOR, fg=FONT_COLOR, width=20, command=None), {"x": 165, "y": 205})


def hide_all_menus() -> None:
    modpacks_menu.hide()
    downloads_menu.hide()
    settings_menu.hide()
    rpc_menu.hide()


tk = Tk()

read_config()
modpacks = get_modpacks_data()

remember = IntVar(value=1)
design = IntVar(value=2)
rpc_mode = IntVar(value=1)

window_size = (650, 450)
screen_size = (tk.winfo_screenwidth(), tk.winfo_screenheight())

tk.title("TerraLauncher")
tk.iconbitmap("icon.ico")
tk.geometry(f"{window_size[0]}x{window_size[1]}+{screen_size[0] // 2 - window_size[0] // 2}+{screen_size[1] // 2 - window_size[1] // 2}")
tk.resizable(False, False)

background = Label(tk, bg=BG_COLOR)
background.place(x=0, y=0, relwidth=1, relheight=1)

version = Label(tk, text=f"Ver. {VERSION}", font="Arial 10", fg=FONT_COLOR, bg=BG_COLOR)
version.place(x=585, y=430)

tk.withdraw()

if not Config["remember"] or Config["access_token"] is None:
    create_auth_menu()
    auth_menu.show()

else:
    create_sidebar_menu()
    sidebar_menu.show()

tk.after(500, lambda: Thread(target=download_needed_files).start())
tk.mainloop()
