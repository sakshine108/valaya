import socket
import json
import hashlib
import os
import threading
from tqdm import tqdm
from datetime import datetime

from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

key = ''

IP = '136.243.65.35'
PORT = 4000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

f_list = []
c_dir = ''
usr = ''
pwd = ''

chunk_size = 1048576

def _is_valid_file_name(f):
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-!@#%^&*()_/.'

    if len(f) > 100:
        return False

    if '//' in f:
        return False

    for i in range(len(f)):
        if not f[i] in valid_chars:
            return False

    return True

def list(path='', stats=False):
    d = {'username': usr, 'password': pwd, 'request': 'list', 'parameters': []}

    d = json.dumps(d)
    d = bytes(d + '\n', 'utf-8')
    s.send(d)

    res = s.recv(1024)
    res = res.decode('utf-8')
    res = json.loads(res)

    if 'error' in res:
        raise Exception(res['error'])
        return

    global f_list
    f_list = res['files']
    f_list = sorted(f_list, key=lambda x: x[2], reverse=True)

    f = c_dir + '/' + path

    if path.startswith('/'):
        f = path

    f = f.removeprefix('/').removesuffix('/')

    files = []

    exists = False

    for fi in f_list:
        if f == fi[0]:
            files.append(f.removeprefix(c_dir + '/'))
            return files

        if fi[0].startswith(f):
            if fi[0].removeprefix(f)[0] == '/' or f == '':
                if stats:
                    exists = True

                    l = []

                    fil = (fi[0].removeprefix(f + '/').split('/')[0])
                    l.append(fil)

                    if fi[0] == (f + '/' + fil).removeprefix('/'):
                        l.append(fi[1])
                        l.append(datetime.fromtimestamp(fi[2]).strftime("%Y-%m-%d %H:%M:%S"))

                    if not l in files:
                        files.append(l)
                else:
                    exists = True

                    l = fi[0].removeprefix(f + '/').split('/')[0]

                    if not l in files:
                        files.append(l)

    if len(f_list) == 0:
        if f == '':
            return []
        else:
            exists = False

    if exists == False:
        raise Exception(f"File or directory '/{f}' does not exist.")
        return

    return files

def current_dir():
    return '/' + c_dir

def change_dir(path=''):
    global c_dir

    if path == '':
        c_dir = ''
        return
    else:
        new_dir = c_dir + '/' + path

        if path.startswith('/'):
            new_dir = path

        new_dir = new_dir.removeprefix('/').removesuffix('/')

        for i in range(len(f_list)):
            if f_list[i][0].startswith(new_dir + '/'):
                c_dir = new_dir
                return

        raise Exception(f"Directory '/{new_dir}' does not exist.")
        return

def back():
    global c_dir

    a = c_dir.removesuffix(c_dir.split('/')[-1]).removesuffix('/')

    if c_dir == a:
        raise Exception('Cannot go back any furthur.')
        return
        
    c_dir = a

def move(src='', dst=''):
    if src == '':
        raise Exception('Missing source.')
        return
    elif dst == '':
        raise Exception('Missing destination.')
        return

    if not src.startswith('/'):
        src = c_dir + '/' + src
    if not dst.startswith('/'):
        dst = c_dir + '/' + dst

    if dst.endswith('/'):
        dst += src.split('/')[-1]

    src = src.removeprefix('/')
    dst = dst.removeprefix('/')

    for i in range(len(f_list)):
        if f_list[i][0] == src:
            break
        if i + 1 == len(f_list):
            raise Exception(f"File '/{src}' does not exist.")
            return

    if not _is_valid_file_name(dst):
        raise Exception(f"'/{dst}' is not a valid file name.")
        return

    if src == dst:
        raise Exception(f"Files '/{src}' and '/{dst}' are the same file.")
        return

    d = {'username': usr, 'password': pwd, 'request': 'move', 'parameters': [src, dst]}

    d = json.dumps(d)
    d = bytes(d + '\n', 'utf-8')
    s.send(d)

    res = s.recv(1024)
    res = res.decode('utf-8')
    res = json.loads(res)

    if 'error' in res.keys():
        raise Exception(res['error'])
        return

    if res['success'] == False:
        raise Exception('Move failed.')
        return

def remove(f=''):
    if f == '':
        raise Exception('Missing operand.')
        return

    if not f.startswith('/'):
        f = c_dir + '/' + f

    f = f.removeprefix('/')

    for i in range(len(f_list)):
        if f_list[i][0] == f:
            break
        if i + 1 == len(f_list):
            raise Exception(f"File '/{f}' does not exist.")
            return

    d = {'username': usr, 'password': pwd, 'request': 'remove', 'parameters': [f]}

    d = json.dumps(d)
    d = bytes(d + '\n', 'utf-8')
    s.send(d)

    res = s.recv(1024)
    res = res.decode('utf-8')
    res = json.loads(res)

    if 'error' in res.keys():
        raise Exception(res['error'])
        return

    if res['success'] == False:
        raise Exception('Remove failed.')
        return

def quota():
    list()

    total_bytes = 0

    for i in range(len(f_list)):
        total_bytes += f_list[i][1]

    d = {'username': usr, 'password': pwd, 'request': 'maxbytes', 'parameters': []}

    d = json.dumps(d)
    d = bytes(d + '\n', 'utf-8')
    s.send(d)

    res = s.recv(1024)
    res = res.decode('utf-8')
    res = json.loads(res)

    if 'error' in res.keys():
        raise Exception(res['error'])
        return

    max_bytes = res['maxbytes']

    return (total_bytes, max_bytes)

def download(src='', dst='', prog=True):
    if src == '':
        raise Exception('Missing source.')
        return

    if not src.startswith('/'):
        src = c_dir + '/' + src

    src = src.removeprefix('/')

    if dst.endswith('/'):
        dst += src.split('/')[-1]

    if dst == '':
        dst = os.getcwd() + '/' + src.split('/')[-1]

    for i in range(len(f_list)):
        if f_list[i][0] == src:
            break
        if i + 1 == len(f_list):
            raise Exception(f"File '{src}' does not exist.")
            return

    d = {'username': usr, 'password': pwd, 'request': 'download', 'parameters': [src]}

    d = json.dumps(d)
    d = bytes(d + '\n', 'utf-8')
    s.send(d)

    res = s.recv(1024)
    res = res.decode('utf-8')
    res = json.loads(res)

    if 'error' in res.keys():
        raise Exception(res['error'])
        return

    file_size = res['filesize'] - 16
    current_file_size = 0

    s.send(b'0')

    if prog == True:
        pbar = tqdm(total=int(file_size / 1024 / 1024), desc=dst.split('/')[-1], unit='MB')

    if os.path.exists(dst):
        os.remove(dst)

    iv = s.recv(16)

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    with open(dst, 'wb') as f:
        while True:
            chunk = s.recv(chunk_size)
            decrypted_chunk = decryptor.update(chunk)
            f.write(decrypted_chunk)

            current_file_size += len(chunk)

            if prog == True:
                pbar.n = int(current_file_size / 1024 / 1024)
                pbar.refresh()

            if current_file_size == file_size:
                break
    
    if prog == True:
        pbar.close()

def _send_bytes(s, src):
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    s.send(iv)

    with open(src, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)

            if not chunk:
                break

            encrypted_chunk = encryptor.update(chunk)
            s.send(encrypted_chunk)

        encrypted_chunk = encryptor.finalize()
        s.send(encrypted_chunk)

upload_prog = 0

def upload(src='', dst='', prog=True):
    global upload_prog
    upload_prog = 0

    if src == '':
        raise Exception('Missing source.')
        return

    if not os.path.exists(src):
        raise Exception(f"File '{src}' does not exist.")
        return

    if not dst.startswith('/'):
        dst = c_dir + '/' + dst

    if dst.endswith('/'):
        dst += src.split('/')[-1]

    if dst == '':
        dst = c_dir + '/' + src.split('/')[-1]

    dst = dst.removeprefix('/')

    if not _is_valid_file_name(dst):
        raise Exception(f"'{dst}' is not a valid file name.")
        return

    file_size = os.path.getsize(src) + 16

    q1, q2 = quota()
    if int(q1) + file_size > int(q2):
        raise Exception('File is too large.')
        return

    d = {'username': usr, 'password': pwd, 'request': 'upload', 'parameters': [dst, file_size]}

    d = json.dumps(d)
    d = bytes(d + '\n', 'utf-8')
    s.send(d)

    res = s.recv(1024)
    res = res.decode('utf-8')
    res = json.loads(res)

    if 'error' in res.keys():
        raise Exception(res['error'])
        return

    thread = threading.Thread(target=_send_bytes, args=(s, src))
    thread.start()

    buffer = ''

    if prog == True:
        pbar = tqdm(total=int(file_size / 1024 / 1024), desc=dst.split('/')[-1], unit='MB')

    while True:
        data = s.recv(1024)
        data = data.decode('utf-8')

        buffer += data

        while buffer.find('\n') != -1:
            msg, buffer = buffer.split('\n', 1)
            msg = json.loads(msg)

            if msg['progress'] == True:
                if prog == True:
                    pbar.close()
                return
            elif msg['progress'] == None:
                if prog == True:
                    pbar.close()
                raise Exception('File is too large.')
                return
            elif prog == True:
                p = msg['progress']

                pbar.n = int(p / 1024 / 1024)
                pbar.refresh()
                
                upload_prog = p

def change_pwd(new_pwd=''):
    if new_pwd == '':
        raise Exception('Missing operand.')
        return

    new_pwd = hashlib.md5(bytes(new_pwd, 'utf-8')).hexdigest()

    d = {'username': usr, 'password': pwd, 'request': 'changepwd', 'parameters': [new_pwd]}

    d = json.dumps(d)
    d = bytes(d + '\n', 'utf-8')
    s.send(d)

    res = s.recv(1024)
    res = res.decode('utf-8')
    res = json.loads(res)

    if 'error' in res.keys():
        raise Exception(res['error'])
        return

    success = res['success']

    if success == False:
        raise Exception('Password change failed.')
        return

def init(usr_, pwd_, key_):
    global usr
    global pwd
    global key

    usr = usr_
    pwd = hashlib.md5(bytes(pwd_, 'utf-8')).hexdigest()

    key = key_

    list()
