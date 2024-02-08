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
import toml
import base64
import hashlib
from munch import DefaultMunch

config_path = pkg_resources.resource_filename('valaya', 'config.toml')

def _set_config(new_config):
    del new_config['set']
    
    with open(config_path, 'w') as f:
        toml.dump(new_config, f)

with open(config_path, 'r') as f:
    config = DefaultMunch.fromDict(toml.load(f))
    
config.set = _set_config
    
__version__ = config.version
    
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
    context = ssl.create_default_context()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    conn = context.wrap_socket(sock, server_hostname=ip)
    conn.connect((ip, port))

    _send(conn, '', '', 'create_account', [user, pw])
    _recv(conn)

def verify_account(ip, port, code):
    context = ssl.create_default_context()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    conn = context.wrap_socket(sock, server_hostname=ip)
    conn.connect((ip, port))

    _send(conn, '', '', 'verify', code)
    _recv(conn)
    
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
    
    def __init__(self, ip: str, port: int, user: str, pw: str, key_pw: str = None, max_threads = 6):
        self.user = user

        self.pw = pw

        self.c_dir = ''
        
        self.max_threads = max_threads

        self.key = base64.urlsafe_b64encode(hashlib.sha256(key_pw.encode('utf-8')).digest())
        self.key_fernet = Fernet(self.key)

        context = ssl.create_default_context()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.conn = context.wrap_socket(sock, server_hostname=ip)
        self.conn.connect((ip, port))
        
        self.ip, self.port = ip, port
        
        self._send('list')
        
        f_list = self._recv()
        
        if len(f_list) >= 1:
            try:
                self.key_fernet.decrypt(f_list[0][0]).decode()
            except:
                raise Exception(f"Incorrect encryption password.")

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
    
    def _download_thread(self, conn, file):
        self.threads += 1
        
        _send(conn, self.user, self.pw, 'download', file[2])
        file_size = _recv(conn)
        file_size -= 16
        current_file_size = 0

        conn.send(b'\x10')
        
        if os.path.dirname(file[1]):
            os.makedirs(os.path.dirname(file[1]), exist_ok=True)

        if os.path.isfile(file[1]):
            os.remove(file[1])

        iv = conn.recv(16)

        cipher = Cipher(algorithms.AES(base64.urlsafe_b64decode(self.key)), modes.GCM(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        with open(file[1], 'wb') as file:
            while True:
                chunk = conn.recv(chunk_size)
                decrypted_chunk = decryptor.update(chunk)
                file.write(decrypted_chunk)

                current_file_size += len(chunk)
                self.prog += len(chunk)

                if current_file_size == file_size:
                    break
            
        self.threads -= 1
            
    def _dl_prog_thread(self, total_size, name):
        self.prog = 0
        
        pbar = tqdm(total=int(total_size / 1024 / 1024), desc=name, unit='MB')
        
        while self.prog < total_size:
            pbar.n = int(self.prog / 1024 / 1024)
            pbar.refresh()
                
        pbar.close()

    def download(self, src, dst=None, show_prog=True):
        if not src.startswith('/'):
            src = os.path.join(self.c_dir, src.lstrip('/')).strip('/')
        else:
            src = src.lstrip('/')

        src = src.strip('/')

        if dst == None:
            dst = os.path.join(os.getcwd(), os.path.basename(src))
        elif dst.endswith('/'):
            dst = os.path.join(dst, os.path.basename(src))
            
        files = []
        filenames = []
        
        total_size = 0
        
        self._send('list')
        f_list = self._recv()

        for f in f_list:
            f.append(self.key_fernet.decrypt(f[0]).decode().strip('/'))
            filenames.append(f[3])

            if os.path.commonpath([f[3], src]) == src:
                validate_filepath(dst, platform='auto')
                files.append([f[3], dst, f[0]])
                total_size += f[1] - 16
                
        if files == []:
            raise Exception(f"File or directory '/{src}' does not exist.")
            
        self.threads = 0

        if len(files) == 1:
            if src not in filenames:
                files[0][1] = os.path.join(dst, files[0][0].removeprefix(src).lstrip('/'))
                    
            if os.access(os.path.dirname(os.path.join(os.getcwd(), files[0][1])), os.W_OK):
                threading.Thread(target=self._download_thread, args=(self.conn, files[0])).start()
            else:
                raise Exception(f"Permission denied: '{os.path.join(os.getcwd(), files[0][1])}'")
        else:
            for file in files:
                while self.threads >= self.max_threads:
                    pass
                
                if src not in filenames:
                    file[1] = os.path.join(dst, file[0].removeprefix(src).lstrip('/'))
                    
                if os.access(os.path.dirname(os.path.join(os.getcwd(), file[1])), os.W_OK):
                    context = ssl.create_default_context()

                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    conn = context.wrap_socket(s, server_hostname=self.ip)
                    conn.connect((self.ip, self.port))

                    threading.Thread(target=self._download_thread, args=(conn, file)).start()
                else:
                    raise Exception(f"Permission denied: '{os.path.join(os.getcwd(), file[1])}'")
                
        if show_prog:
            threading.Thread(target=self._dl_prog_thread, args=(total_size, os.path.basename(dst))).start()
            
        while self.prog < total_size:
            pass

    def _send_bytes(self, conn, src):
        iv = os.urandom(16)

        cipher = Cipher(algorithms.AES(base64.urlsafe_b64decode(self.key)), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        conn.send(iv)

        with open(src, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)

                if not chunk:
                    break

                encrypted_chunk = encryptor.update(chunk)
                conn.send(encrypted_chunk)
                
    def _upload_thread(self, conn, file):
        self.threads += 1
        
        filename = file[1]

        file[1] = self.key_fernet.encrypt(filename.encode()).decode()

        _send(conn, self.user, self.pw, 'upload', file[1:])

        conn.recv(1)

        threading.Thread(target=self._send_bytes, args=(conn, file[0])).start()

        total_prog = 0
        buffer = ''

        while total_prog != 'done':
            data = conn.recv(20)
            data = data.decode('utf-8')

            buffer += data

            while buffer.find('\n') != -1:
                msg, buffer = buffer.split('\n', 1)
                
                if not msg == 'done':
                    msg = int(msg)
                    self.prog += msg - total_prog
                    
                total_prog = msg
                
        self.threads -= 1
        
    def _ul_prog_thread(self, total_size, name):
        self.prog = 0
        
        pbar = tqdm(total=int(total_size / 1024 / 1024), desc=name, unit='MB')
        
        while self.prog < total_size:
            pbar.n = int(self.prog / 1024 / 1024)
            pbar.refresh()
                    
        pbar.close()

    def upload(self, src, dst, show_prog=True):
        if not os.path.exists(src):
            raise Exception(f"File or directory '{src}' does not exist.")
        
        if not dst:
            dst = os.path.join(self.c_dir, os.path.basename(src)).lstrip('/')
        elif not dst.startswith('/'):
            dst = os.path.join(self.c_dir, dst).lstrip('/')
        elif dst.endswith('/'):
            dst = os.path.join(dst, os.path.basename(src)).lstrip('/')

        q1, q2, _ = self.get_quota()
        
        files = []
        
        total_size = 0
        
        if os.path.isdir(src):
            for foldername, _, filenames in os.walk(src):
                for f in filenames:
                    filepath = os.path.join(foldername, f)
                    filesize = os.path.getsize(filepath) + 16
                    total_size += filesize
                    
                    relative_path = filepath.removeprefix(os.path.commonpath([src, filepath])).lstrip('/')
                    dst_path = os.path.join(dst, relative_path)

                    files.append([filepath, dst_path, filesize])

            if q1 + total_size > q2:
                raise Exception('Directory is too large.')
        else:
            total_size = filesize = os.path.getsize(src) + 16

            if q1 + filesize > q2:
                raise Exception('File is too large.')
            
            files = [[src, dst, filesize]]
            
        self._send('list')
        f_list = self._recv()
                    
        files_set = {file[1] for file in files}

        for f in f_list:
            decoded = self.key_fernet.decrypt(f[0]).decode()

            if decoded in files_set:
                self._send('remove', f[0])
                self._recv()

        if show_prog:
            threading.Thread(target=self._ul_prog_thread, args=(total_size, os.path.basename(dst))).start()
            
        self.threads = 0
        
        if len(files) == 1:
            threading.Thread(target=self._upload_thread, args=(self.conn, files[0])).start()
        else:
            for file in files:
                while self.threads >= self.max_threads:
                    pass
            
                context = ssl.create_default_context()

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                conn = context.wrap_socket(s, server_hostname=self.ip)
                conn.connect((self.ip, self.port))
            
                threading.Thread(target=self._upload_thread, args=(conn, file)).start()
                
        while not self.threads == 0:
            pass

    def change_pw(self, new_pw):
        self._send('change_pw', new_pw)
        self._recv()