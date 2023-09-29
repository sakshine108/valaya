import socket
import json
import hashlib
import os
import threading
from tqdm import tqdm
from datetime import datetime
import uuid
import rsa
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import pkg_resources
import yaml
from yaml.loader import SafeLoader

msg_key = Fernet.generate_key()
fernet = Fernet(msg_key)

chunk_size = 1048576

s = None
f_list = []
c_dir = ''
usr = ''
pwd = ''
server_public_key = ''
file_key = ''

with open(pkg_resources.resource_filename('nimbus', 'server_public_key.txt'), 'rb') as key_file:
    key_data = key_file.read()
    server_public_key = rsa.PublicKey.load_pkcs1(key_data)

def _send(cmd, args = None):
    id = uuid.uuid4().hex

    msg = {'id': id, 'acct': [usr, pwd], cmd: args}

    msg = json.dumps(msg)
    msg = bytes(msg + '\n', 'utf-8')

    enc_msg = fernet.encrypt(msg)

    s.send(enc_msg)

def _recv():
    res = s.recv(1024)

    res = fernet.decrypt(res)

    res = res.decode('utf-8')
    res = json.loads(res)

    if 'error' in res:
        raise Exception(res['error'])

    return res['res']

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

def _is_valid_passwd(passwd):
    l, u, s, d = 0, 0, 0, 0

    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    symbols = '~`!@#$%^&*()_-+={[}]|\:;"<,>.?/'
    digits = '0123456789'

    if (len(passwd) >= 8):
        for i in passwd:
            if (i in lowercase):
                l+=1           
            if (i in uppercase):
                u+=1           
            if (i in digits):
                d+=1           
            if(i in symbols):
                s+=1    

    if (l>=1 and u>=1 and s>=1 and d>=1 and l+s+u+d==len(passwd)):
        return True
    else:
        return False

def list_all(stats=False):
    global f_list

    _send('list')

    f_list = _recv()
    f_list = sorted(f_list, key=lambda x: x[2], reverse=True)

    files = []

    if not stats:
        for f in f_list:
            files.append(f[0])
    else: files = f_list

    return files

def list(path='', stats=False):
    global f_list

    _send('list')

    f_list = _recv()
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

    return files

def current_dir():
    return '/' + c_dir

def change_dir(path):
    global c_dir

    if path == '' or path == '/':
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
    
def back():
    global c_dir

    a = c_dir.removesuffix(c_dir.split('/')[-1]).removesuffix('/')

    if c_dir == a:
        raise Exception('Cannot go back any furthur.')

    c_dir = a

def move(src, dst):
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

    if not _is_valid_file_name(dst):
        raise Exception(f"'/{dst}' is not a valid file name.")

    if src == dst:
        raise Exception(f"Files '/{src}' and '/{dst}' are the same file.")

    _send('move', [src, dst])

    if _recv() == False:
        raise Exception('Move failed.')

def remove(file_path):
    if not file_path.startswith('/'):
        file_path = c_dir + '/' + file_path

    file_path = file_path.removeprefix('/')

    for i in range(len(f_list)):
        if f_list[i][0] == file_path:
            break
        if i + 1 == len(f_list):
            raise Exception(f"File '/{file_path}' does not exist.")

    _send('remove', file_path)

    if _recv() == False:
        raise Exception('Remove failed.')

def quota():
    list()

    total_bytes = 0

    for i in range(len(f_list)):
        total_bytes += f_list[i][1]

    _send('maxbytes')

    max_bytes = _recv()

    return (total_bytes, max_bytes)

def download(src, dst=None, prog=True):
    if not src.startswith('/'):
        src = c_dir + '/' + src

    src = src.removeprefix('/')

    if dst == None:
        dst = os.getcwd() + '/' + src.split('/')[-1]
    else:
        if dst.endswith('/'):
            dst += src.split('/')[-1]

    if len(f_list) == 0:
        raise Exception(f"File '{src}' does not exist.")

    for i in range(len(f_list)):
        if f_list[i][0] == src:
            break
        if i + 1 == len(f_list):
            raise Exception(f"File '{src}' does not exist.")

    _send('download', src)

    file_size = _recv()
    file_size -= 16
    current_file_size = 0

    s.send(b'0')

    if prog == True:
        pbar = tqdm(total=int(file_size / 1024 / 1024), desc=dst.split('/')[-1], unit='MB')

    if os.path.exists(dst):
        os.remove(dst)

    iv = s.recv(16)

    cipher = Cipher(algorithms.AES(file_key), modes.GCM(iv), backend=default_backend())
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

    cipher = Cipher(algorithms.AES(file_key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    s.send(iv)

    with open(src, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)

            if not chunk:
                break

            encrypted_chunk = encryptor.update(chunk)
            s.send(encrypted_chunk)

upload_prog = 0

def upload(src, dst=None, show_prog=True):
    global upload_prog
    upload_prog = 0

    if not os.path.exists(src):
        raise Exception(f"File '{src}' does not exist.")

    if dst == None:
        dst = c_dir + '/' + src.split('/')[-1]
    else:
        if not dst.startswith('/'):
            dst = c_dir + '/' + dst

        if dst.endswith('/'):
            dst += src.split('/')[-1]

    dst = dst.removeprefix('/')

    if not _is_valid_file_name(dst):
        raise Exception(f"'{dst}' is not a valid file name.")

    file_size = os.path.getsize(src) + 16

    q1, q2 = quota()
    if int(q1) + file_size > int(q2):
        raise Exception('File is too large.')

    _send('upload', [dst, file_size])

    s.recv(1)

    thread = threading.Thread(target=_send_bytes, args=(s, src))
    thread.start()

    buffer = ''

    if show_prog:
        pbar = tqdm(total=int(file_size / 1024 / 1024), desc=dst.split('/')[-1], unit='MB')

    while True:
        data = s.recv(20)
        data = data.decode('utf-8')

        buffer += data

        while buffer.find('\n') != -1:
            msg, buffer = buffer.split('\n', 1)

            prog = msg

            if prog == 'done':
                if show_prog:
                    pbar.close()
                return
            elif show_prog:
                p = int(prog)
                pbar.n = int(p / 1024 / 1024)
                pbar.refresh()
                
                upload_prog = p

def change_pwd(new_pwd):
    if not _is_valid_passwd(new_pwd):
        raise Exception('Invalid password.')

    new_pwd = hashlib.md5(bytes(new_pwd, 'utf-8')).hexdigest()

    _send('change_pwd', new_pwd)

    if _recv() == False:
        raise Exception('Password change failed.')

def create_account(usr, pwd):
    if not _is_valid_passwd(pwd):
        raise Exception('Invalid password.')

    pwd = hashlib.md5(bytes(pwd, 'utf-8')).hexdigest()

    _send('create_account', [usr, pwd])
    _recv()

def verify(code):
    _send('verify', code)
    _recv()

def init(user=None, passwd=None, key_path=None):
    global s
    global usr
    global pwd
    global file_key
    global f_list

    config_path = pkg_resources.resource_filename('nimbus', 'config.yaml')

    with open(config_path) as f:
        config = yaml.load(f, Loader=SafeLoader)

    usr_c = config['username']
    pwd_c = config['password']
    ip = config['ip']
    port = config['port']   
    key_path_c = config['key_path']

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    enc_msg_key = rsa.encrypt(msg_key, server_public_key)
    s.send(enc_msg_key)

    if user == '':
        return

    if user != None or passwd != None or key_path != None:
        if user != None:
            config['username'] = user

        if passwd != None:
            config['password'] = passwd

        if key_path != None:
            config['key_path'] = key_path

        with open(config_path, 'w') as f:
            yaml.dump(config, f, sort_keys=False)

    if user == None:
        user = usr_c

    if passwd == None:
        passwd = pwd_c

    if key_path == None:
        key_path = key_path_c

    key = None

    if key_path != None:
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                key = f.read()
        else:
            key = os.urandom(32)
            with open(key_path, "wb") as f:
                f.write(key)

    usr = user
    pwd = hashlib.md5(bytes(passwd, 'utf-8')).hexdigest()

    file_key = key

    _send('list')

    f_list = _recv()
    f_list = sorted(f_list, key=lambda x: x[2], reverse=True)