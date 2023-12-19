import socket
import ssl
import json
import os
import threading
from tqdm import tqdm
from datetime import datetime
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import pkg_resources
from pathvalidate import validate_filepath
import yaml
import base64
import hashlib

config_path = pkg_resources.resource_filename('valaya', 'config.yaml')

def get_config():
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
    
def set_config(new_config):
    with open(config_path, 'w') as f:
        yaml.dump(new_config, f, sort_keys=False)
    
chunk_size = 1048576

def _send(s, user, pw, cmd, args = None):
    id = uuid.uuid4().hex

    msg = {'id': id, 'acct': [user, pw], cmd: args}

    msg = json.dumps(msg)
    msg = bytes(msg + '\n', 'utf-8')

    s.send(msg)

def _recv(s):
    res = s.recv(4096)

    res = res.decode('utf-8')
    res = json.loads(res)

    if 'error' in res:
        raise Exception(res['error'])

    return res['res']

def create_account(ip, port, user, pw):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    _send(s, '', '', 'create_account', [user, pw])
    _recv(s)

def verify_account(ip, port, code):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    _send(s, '', '', 'verify', code)
    _recv(s)
    
class User:
    def _send(self, cmd, args = None):
        id = uuid.uuid4().hex

        msg = {'id': id, 'acct': [self.user, self.pw], cmd: args}

        msg = json.dumps(msg)
        msg = bytes(msg + '\n', 'utf-8')

        self.conn.send(msg)

    def _recv(self):
        res = self.conn.recv(4096)

        res = res.decode('utf-8')
        res = json.loads(res)

        if 'error' in res:
            raise Exception(res['error'])

        return res['res']
    
    def __init__(self, ip: str, port: int, user: str, pw: str, key_pw: str = None):
        self.user = user

        self.pw = pw

        self.c_dir = ''

        self.key = base64.urlsafe_b64encode(hashlib.sha256(key_pw.encode('utf-8')).digest())
        self.key_fernet = Fernet(self.key)

        context = ssl.create_default_context()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.conn = context.wrap_socket(sock, server_hostname=ip)
        self.conn.connect((ip, port))

    def list_all(self, stats=False):
        self._send('list')
        f_list = self._recv()

        for f in f_list:
            f.append(self.key_fernet.decrypt(f[0]).decode())

        f_list = sorted(f_list, key=lambda x: x[2], reverse=True)

        files = []

        if not stats:
            files = [f[3] for f in f_list]
        else:
            files = f_list

        return files
    
    def list(self, path='', stats=False):
        if not path.startswith('/'):
            path = os.path.join(self.c_dir, path)

        path = os.path.normpath(path)

        if path.split('/')[0] == '.':
            path = path.removeprefix('.')

        path = path.strip('/')

        files = []

        exists = False

        self._send('list')
        f_list = self._recv()

        for f in f_list:
            f.append(self.key_fernet.decrypt(f[0]).decode())

        f_list = sorted(f_list, key=lambda x: x[2], reverse=True)

        for f in f_list:
            if path == f[3]:
                return [[os.path.basename(path)]]
            
            if f[3].startswith(path):
                if f[3].removeprefix(path).startswith('/') or not path:
                    exists = True

                    dirname = f[3].removeprefix(path + '/').split('/')[0]

                    if stats:
                        l = []
                        l.append(dirname)

                        if f[3] == os.path.join(path, l[0]).lstrip('/'):
                            l.append(f[1])
                            l.append(datetime.fromtimestamp(f[2]).strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        l = dirname

                    if not l in files:
                        files.append(l)

        if not f_list and not path:
            return []

        if exists == False:
            raise Exception(f"File or directory '/{path}' does not exist.")
        
        return files
    
    def change_dir(self, path):
        if not path or path == '/':
            self.c_dir = ''
            return
        
        if path.startswith('/'):
            new_dir = path.strip('/')
        else:
            new_dir = os.path.join(self.c_dir, path).strip('/')

        new_dir = os.path.normpath(new_dir)

        if new_dir.split('/')[0] == '.':
            self.c_dir = ''
            return

        self._send('list')
        f_list = self._recv()

        for f in f_list:
            decrypted_path = self.key_fernet.decrypt(f[0]).decode()

            if decrypted_path.startswith(new_dir + '/'):
                self.c_dir = new_dir
                return

        raise Exception(f"Directory '/{new_dir}' does not exist.")
        
    def move(self, src, dst):
        if not src.startswith('/'):
            src = os.path.join(self.c_dir, src)

        if not dst.startswith('/'):
            dst = os.path.join(self.c_dir, dst)

        if dst.endswith('/') and not src.endswith('/'):
            dst = os.path.join(dst, os.path.basename(src))

        src = src.lstrip('/')
        dst = dst.lstrip('/')

        if src == dst:
            raise Exception(f"'/{src}' and '/{dst}' are the same file.")

        self._send('list')
        f_list = self._recv()

        files = []
        filenames = []

        for f in f_list:
            f.append(self.key_fernet.decrypt(f[0]).decode())
            filenames.append(f[3])

            if os.path.commonpath([f[3], src]) == src.strip('/'):
                if src not in filenames:
                    dst = os.path.join(dst, os.path.basename(f[3]))
                
                files.append([f[0], self.key_fernet.encrypt(dst.encode()).decode()])

        if not files:
            raise Exception(f"File or directory '/{src}' does not exist.")

        for file in files:
            self._send('move', file)
            self._recv()

    def remove(self, path, trash=True):
        if not path.startswith('/'):
            path = os.path.join(self.c_dir, path)

        path = os.path.normpath(path)

        if path.split('/')[0] == '.':
            path = ''

        path = path.lstrip('/')

        if trash and not path.split('/')[0] == 'trash':
            self.move(path, '/trash/')
            return

        files = []

        self._send('list')
        f_list = self._recv()

        for f in f_list:
            f.append(self.key_fernet.decrypt(f[0]).decode())

            if os.path.commonpath([f[3], path]) == path:
                files.append(f[0])

        if files == []:
            raise Exception(f"File or directory '/{path}' does not exist.")

        for file in files:
            self._send('remove', file)
            self._recv()

    def get_quota(self):
        total_bytes = 0

        self._send('list')
        f_list = self._recv()

        total_bytes = sum(file_info[1] for file_info in f_list)

        self._send('maxbytes')

        max_bytes, daily_bytes = self._recv()

        return total_bytes, max_bytes, daily_bytes
    
    def download(self, src, dst=None, prog=True):
        if not src.startswith('/'):
            src = os.path.join(self.c_dir, src.lstrip('/')).strip('/')
        else:
            src = src.lstrip('/')

        src = src.strip('/')

        if dst == None:
            dst = os.path.join(os.getcwd(), os.path.basename(src))
        elif dst.endswith('/'):
            dst = os.path.join(dst, os.path.basename(src))

        self._send('list')
        f_list = self._recv()

        files = []
        filenames = []

        for f in f_list:
            f.append(self.key_fernet.decrypt(f[0]).decode().strip('/'))
            filenames.append(f[3])

            if os.path.commonpath([f[3], src]) == src:
                validate_filepath(dst, platform='auto')
                files.append([f[3], dst, f[0]])

        if files == []:
            raise Exception(f"File or directory '/{src}' does not exist.")

        for f in files:
            if src not in filenames:
                f[1] = os.path.join(dst, f[0].removeprefix(src).lstrip('/'))

            self._send('download', f[2])
            file_size = self._recv()
            file_size -= 16
            current_file_size = 0

            self.conn.send(b'0')

            if prog:
                pbar = tqdm(total=int(file_size / 1024 / 1024), desc=f[1].split('/')[-1], unit='MB')

            os.makedirs(os.path.dirname(f[1]), exist_ok=True)

            if os.path.isfile(f[1]):
                os.remove(f[1])

            iv = self.conn.recv(16)

            cipher = Cipher(algorithms.AES(base64.urlsafe_b64decode(self.key)), modes.GCM(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            with open(f[1], 'wb') as file:
                while True:
                    chunk = self.conn.recv(chunk_size)
                    decrypted_chunk = decryptor.update(chunk)
                    file.write(decrypted_chunk)

                    current_file_size += len(chunk)

                    if prog:
                        pbar.n = int(current_file_size / 1024 / 1024)
                        pbar.refresh()

                    if current_file_size == file_size:
                        break
            
                if prog:
                    pbar.close()

    def _send_bytes(self, src):
        iv = os.urandom(16)

        cipher = Cipher(algorithms.AES(base64.urlsafe_b64decode(self.key)), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        self.conn.send(iv)

        with open(src, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)

                if not chunk:
                    break

                encrypted_chunk = encryptor.update(chunk)
                self.conn.send(encrypted_chunk)

    def upload(self, src, dst, show_prog=True):
        if not os.path.exists(src):
            raise Exception(f"File or directory '{src}' does not exist.")
        
        if not dst:
            dst = os.path.join(self.c_dir, os.path.basename(src)).lstrip('/')
        elif not dst.startswith('/'):
            dst = os.path.join(self.c_dir, dst).lstrip('/')
        elif dst.endswith('/'):
            dst = os.path.join(dst, os.path.basename(src)).lstrip('/')

        q1, q2, q3 = self.get_quota()
        
        files = []
        
        if os.path.isdir(src):
            size = 0
            
            for foldername, subfolders, filenames in os.walk(src):
                for f in filenames:
                    filepath = os.path.join(foldername, f)
                    filesize = os.path.getsize(filepath) + 16
                    size += filesize
                    
                    relative_path = filepath.removeprefix(os.path.commonpath([src, filepath])).lstrip('/')
                    dst_path = os.path.join(dst, relative_path)

                    files.append([filepath, dst_path, filesize])

            if q1 + size > q2:
                raise Exception('Directory is too large.')
        else:
            filesize = os.path.getsize(src) + 16

            if q1 + filesize > q2:
                raise Exception('File is too large.')
            
            files = [[src, dst, filesize]]
        
        for file in files:
            filename = file[1]

            file[1] = self.key_fernet.encrypt(filename.encode()).decode()

            self._send('upload', file[1:])

            self.conn.recv(1)

            thread = threading.Thread(target=self._send_bytes, args=(file[0],))
            thread.start()

            if show_prog:
                pbar = tqdm(total=int(file[2] / 1024 / 1024), desc=filename.split('/')[-1], unit='MB')

            prog = None
            buffer = ''

            while prog != 'done':
                data = self.conn.recv(20)
                data = data.decode('utf-8')

                buffer += data

                while buffer.find('\n') != -1:
                    msg, buffer = buffer.split('\n', 1)

                    prog = msg

                    if show_prog:
                        if prog == 'done':
                            pbar.close()
                        else:
                            p = int(prog)
                            pbar.n = int(p / 1024 / 1024)
                            pbar.refresh()

    def change_pw(self, new_pw):
        self._send('change_pw', new_pw)
        self._recv()