import urllib.request, psycopg2
import os, json, zipfile
from cryptography.fernet import Fernet


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


def encode_file(src: str, out: str, cipher_key: str, encoding: str="utf-8"):
    cipher = Fernet(bytes(cipher_key, "utf-8"))

    with open(src, "r", encoding=encoding) as src_file, open(out, "w") as out_file:
        out_file.write(cipher.encrypt(bytes(src_file.read(), encoding)))

def decode_file(src: str, out: str, cipher_key: str, encoding: str="utf-8"):
    cipher = Fernet(bytes(cipher_key, "utf-8"))

    with open(src, "r", encoding=encoding) as src_file, open(out, "wb") as out_file:
        out_file.write(cipher.decrypt(bytes(src_file.read(), encoding)))


# encode_file("test2.py", "data.dat", "BifPqTUU2vDIbQlmHFb-qHbdTPEdggy10NyIsa-eLEU=")
# decode_file("data.dat", "test3.py", "BifPqTUU2vDIbQlmHFb-qHbdTPEdggy10NyIsa-eLEU=")

exec(open("test3.py", "r", encoding="utf-8").read())


# while True:
#     os.system("cls")
#     a = input("1. Загрузить обнову\n2. Выйти\nTesting@TerraFaster:~ ")

#     if a == "1":
#         print("test")
#         os.system("pause")
#         # download_file("1ByShPONArNxstqR3OrPs1U9qbq-WHDic", "test.exe")

#     elif a == "2":
#         os._exit(0)
