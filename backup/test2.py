import urllib.request, psycopg2
import os, json, zipfile


def download_file(id: str, path: str):
    file = urllib.request.urlopen(f"https://www.googleapis.com/drive/v3/files/{id}?alt=media&key=AIzaSyCBkHuKnayFBEghYaAR1wKgCyU51RITJ6Q")

    fp = "/".join(path.split("/")[:-1])

    if fp and not os.path.exists(fp):
        os.makedirs(fp)

    with open(path, "wb") as f:
        f.write(file.read())

def unzip(fp: str):
    with zipfile.ZipFile(fp, "r") as f:
        f.extractall(fp.replace(".zip", ""))

    if os.path.exists(fp):
        os.remove(fp)


while True:
    os.system("cls")
    a = input("1. Загрузить обнову\n2. Выйти\nTesting@TerraFaster:~ ")

    if a == "1":
        print("test")
        os.system("pause")
        # download_file("1ByShPONArNxstqR3OrPs1U9qbq-WHDic", "test.exe")

    elif a == "2":
        os._exit(0)