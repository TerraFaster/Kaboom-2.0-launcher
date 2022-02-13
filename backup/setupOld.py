import random, string

key = "".join([random.choice(string.ascii_letters + string.digits) for i in range(256)])

print(key)

# pyinstaller -F -w --clean -i icon.ico --key aMO9HjjAIn9jipJg89bYRwwK8JiM9XrrvCc main.py
# pyinstaller -F -w -i icon.ico --key aMO9HjjAIn9jipJg89bYRwwK8JiM9XrrvCc test.py

# from cx_Freeze import setup, Executable

# setup(
#     name="TerraLauncher",
#     version="1.0",
#     description="Launcher for Kaboom written by TerraFaster.",
#     executables=[Executable("main.py", base="Win32GUI", icon="icon.ico")]
# )
