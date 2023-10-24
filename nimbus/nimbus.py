import socket
import json
import os
import threading
from tqdm import tqdm
from datetime import datetime
import uuid
import rsa
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import pkg_resources
import yaml
from yaml.loader import SafeLoader
import re
from pathvalidate import validate_filepath

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

def is_valid_email(email):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email)

def is_valid_passwd(passwd):
    l, u, s, d = 0, 0, 0, 0

    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    symbols = '~`!@#$%^&*()_-+={[}]|\:;"<,>.?/'
    digits = '0123456789'

    if len(passwd) >= 8:
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
    
def is_valid_hash(s):
    return re.fullmatch(r"([a-fA-F\d]{32})", s)

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

    f = os.path.join(c_dir, path)

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
        new_dir = os.path.join(c_dir, path)

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
    global f_list

    if not src.startswith('/'):
        src = c_dir + '/' + src
    if not dst.startswith('/'):
        dst = c_dir + '/' + dst

    if dst.endswith('/'):
        dst += src.split('/')[-1]

    src = src.removeprefix('/')
    dst = dst.removeprefix('/')

    files = []

    for f in f_list:
        if os.path.commonpath([f[0], src]) == src.removesuffix('/').removeprefix('/'):
            if not _is_valid_file_name(dst):
                raise Exception(f"'/{dst}' is not a valid file name.")
            files.append([f[0], dst])

    if len(files) == 0:
        raise Exception(f"File or directory '/{src}' does not exist.")

    fl = []

    for f in f_list:
        fl.append(f[0])

    if src not in fl:
        for file in files:
            file[1] = os.path.join(dst, os.path.basename(file[0]))

    for file in files:
        _send('move', file)
        _recv()

    _send('list')
    f_list = _recv()
    
def remove(path, trash=True):
    global f_list

    if trash and path.split('/')[0] != 'trash':
        move(path, 'trash/')
        return
    
    if not path.startswith('/'):
        path = os.path.join(c_dir, path)

    path = path.removeprefix('/')

    files = []

    for f in f_list:
        if os.path.commonpath([f[0], path]) == path:
            files.append(f[0])

    if files == []:
        raise Exception(f"File or directory '/{path}' does not exist.")

    for file in files:
        _send('remove', file)
        _recv()

    _send('list')
    f_list = _recv()

def quota():
    list()

    total_bytes = 0

    for i in range(len(f_list)):
        total_bytes += f_list[i][1]

    _send('maxbytes')

    max_bytes, daily_bytes = _recv()

    return (total_bytes, max_bytes, daily_bytes)

def download(src, dst=None, prog=True):
    if not src.startswith('/'):
        src = c_dir + '/' + src

    src = src.removeprefix('/')

    if dst == None:
        dst = os.getcwd() + '/' + src.split('/')[-1]
    else:
        if dst.endswith('/'):
            dst += src.split('/')[-1]

    files = []

    for f in f_list:
        if os.path.commonpath([f[0], src]) == src.removesuffix('/').removeprefix('/'):
            validate_filepath(dst, platform='auto')
            files.append([f[0], dst])

    if files == []:
        raise Exception(f"File or directory '/{src}' does not exist.")

    fl = []
    
    for f in f_list:
        fl.append(f[0])

    if src not in fl:
        for file in files:
            file[1] = os.path.join(dst, os.path.basename(file[0]))

    for file in files:
        _send('download', file[0])

        file_size = _recv()
        file_size -= 16
        current_file_size = 0

        s.send(b'0')

        if prog == True:
            pbar = tqdm(total=int(file_size / 1024 / 1024), desc=file[1].split('/')[-1], unit='MB')

        dirname = os.path.dirname(file[1])

        if dirname != '':
            os.makedirs(dirname, exist_ok=True)

        if os.path.exists(file[1]) and os.path.isfile(file[1]):
            os.remove(file[1])

        iv = s.recv(16)

        cipher = Cipher(algorithms.AES(file_key), modes.GCM(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        with open(file[1], 'wb') as f:
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

def upload(src, dst=None, show_prog=True):
    global f_list

    if not os.path.exists(src):
        raise Exception(f"File or directory '{src}' does not exist.")
    
    if dst == None:
        dst = os.path.join(c_dir, os.path.basename(src))
    else:
        if not dst.startswith('/'):
            dst = os.path.join(c_dir, dst)

        if dst.endswith('/'):
            dst += os.path.basename(src)

    dst = dst.removeprefix('/')

    q1, q2, q3 = quota()
    
    files = []
    
    if os.path.isdir(src):
        size = 0
        
        for foldername, subfolders, filenames in os.walk(src):
            for f in filenames:
                filepath = os.path.join(foldername, f)
                filesize = os.path.getsize(filepath) + 16
                size += filesize

                dest = os.path.join(dst, f)

                if not _is_valid_file_name(dest):
                    raise Exception(f"'{dest}' is not a valid file name.")
                
                files.append([filepath, dest, filesize])

        if q1 + size > q2:
            raise Exception('Directory is too large.')
    else:
        filesize = os.path.getsize(src) + 16

        if q1 + filesize > q2:
            raise Exception('File is too large.')
        
        files = [[src, dst, filesize]]
    
    for file in files:
        _send('upload', file[1:])

        s.recv(1)

        thread = threading.Thread(target=_send_bytes, args=(s, file[0]))
        thread.start()

        buffer = ''

        if show_prog:
            pbar = tqdm(total=int(file[2] / 1024 / 1024), desc=file[1].split('/')[-1], unit='MB')

        prog = None

        while prog != 'done':
            data = s.recv(20)
            data = data.decode('utf-8')

            buffer += data

            while buffer.find('\n') != -1:
                msg, buffer = buffer.split('\n', 1)

                prog = msg

                if prog == 'done':
                    if show_prog:
                        pbar.close()
                elif show_prog:
                    p = int(prog)
                    pbar.n = int(p / 1024 / 1024)
                    pbar.refresh()

    _send('list')
    f_list = _recv()

def change_pwd(new_pwd):
    if not is_valid_hash(new_pwd):
        raise Exception('Invalid hash.')

    _send('change_pwd', new_pwd)
    _recv()

def create_account(usr, pwd):
    if not is_valid_email(usr):
        raise Exception('Invalid email.')
    if not is_valid_hash(pwd):
        raise Exception('Invalid hash.')

    _send('create_account', [usr, pwd])
    _recv()

def verify(code):
    _send('verify', code)
    _recv()

def get_plans():
    _send('plans')
    plans = _recv()

    for plan in plans:
        plans[plan]['url'] += f'?prefilled_email={usr.replace("@", "%40")}'

    return plans

def get_customer_portal():
    _send('customer_portal')
    return _recv()

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
    else:
        if usr_c == None:
            raise Exception('Not signed in.')

    if user == None:
        user = usr_c

    if passwd == None:
        passwd = pwd_c

    if key_path == None:
        key_path = key_path_c

    key = None

    if key_path != None:
        if key_path.endswith('/'):
            key_path += 'key.txt'
            
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                key = f.read()
        else:
            key = os.urandom(32)
            with open(key_path, "wb") as f:
                f.write(key)

    usr = user
    pwd = passwd

    file_key = key

    _send('list')

    f_list = _recv()
    f_list = sorted(f_list, key=lambda x: x[2], reverse=True)