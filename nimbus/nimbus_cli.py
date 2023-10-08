import nimbus
import humanize
import readline
import sys
import pwinput
import pkg_resources
import yaml
from yaml.loader import SafeLoader
from argparse import ArgumentParser
from pathvalidate import validate_filepath
import hashlib

config_path = pkg_resources.resource_filename('nimbus', 'config.yaml')

with open(config_path) as f:
    config = yaml.load(f, Loader=SafeLoader)

usr = config['username']
pwd = config['password']

def sign_in():
    usr = input('Email: ')

    if not nimbus.is_valid_email(usr):
        print('Invalid email.')
        quit()

    pwd = pwinput.pwinput(prompt = 'Password: ')

    if not nimbus.is_valid_passwd(pwd):
        print('Invalid password.')
        quit()

    key_path = input('Encryption key filepath: ')

    pwd = hashlib.md5(bytes(pwd, 'utf-8')).hexdigest()

    try:
        validate_filepath(key_path, platform='auto')
        nimbus.init(usr, pwd, key_path)
    except Exception as e:
        print('Error: ' + str(e))

    quit()

def sign_up():
    user = input('Email: ')

    if not nimbus.is_valid_email(user):
        print('Invalid email.')
        quit()

    passwd = pwinput.pwinput(prompt = 'Password: ')

    if not nimbus.is_valid_passwd(passwd):
        print('Invalid password.')
        quit()

    passwd2 = pwinput.pwinput(prompt = 'Retype password: ')

    if passwd != passwd2:
        print('Passwords do not match.')
        quit()
    
    key_path = input('Encryption key filepath: ')

    passwd = hashlib.md5(bytes(passwd, 'utf-8')).hexdigest()

    try:
        validate_filepath(key_path, platform='auto')

        nimbus.init(user='')
        nimbus.create_account(user, passwd)

        code = input('Verification code: ')

        nimbus.verify(code)
        nimbus.init(user, passwd, key_path)

        print('Account created.')
    except Exception as e:
        print('Error: ' + str(e))

    quit()

if len(sys.argv) == 2:
    if sys.argv[1] == 'signin':
        sign_in()
    elif sys.argv[1] == 'signup':
        sign_up()

try:
    nimbus.init()
except Exception as e:
    print('Error: ' + str(e))
    quit()

def main():
    global pwd

    while True:
        args = input(f'{usr} {nimbus.current_dir()} ❯ ').split()
        
        cmd = ''
        
        if len(args) > 0:
            cmd = args[0]
            args = args[1:]

        if cmd == '':
            pass
        elif cmd == 'q':
            parser = ArgumentParser(description='Quit the interface', prog='q')
            parser.parse_args(args)

            quit()
        elif cmd == 'ls':
            parser = ArgumentParser(description='List files in a directory', prog='ls')
            parser.add_argument('path', nargs='?', default='')
            parser.add_argument('-l', '--long', action='store_true', help='use a long listing format (show file size and time of upload)')

            try:
                args = parser.parse_args(args)

                l = nimbus.list(args.path, stats=args.long)
                
                for i in range(len(l)):
                    if type(l[i]) is list:
                        if len(l[i]) > 1:
                            b = l[i][1]
                            size = humanize.naturalsize(b) + f', {b} Bytes'
                            print(f'{l[i][0]} ({size}) ({l[i][2]})')
                        else:
                            print(l[i][0])
                    else:
                        print(l[i])
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'cd':
            parser = ArgumentParser(description='Change the working directory', prog='cd')
            parser.add_argument('path', nargs='?', default='/')

            try:
                args = parser.parse_args(args)
                nimbus.change_dir(args.path)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'back' or cmd == 'b':
            parser = ArgumentParser(description='Change to the previous directory', prog='b')

            try:
                parser.parse_args(args)
                nimbus.back()
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'mv':
            parser = ArgumentParser(description='Move or rename a file or directory', prog='mv')
            parser.add_argument('source')
            parser.add_argument('dest')

            try:
                args = parser.parse_args(args)
                nimbus.move(args.source, args.dest)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'rm':
            parser = ArgumentParser(description='Move a file or directory into the trash folder', prog='rm')
            parser.add_argument('-f', '--force', action='store_false', help='permanently delete a file or directory')
            parser.add_argument('file')

            try:
                args = parser.parse_args(args)
                nimbus.remove(args.file, args.force)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'dl':
            parser = ArgumentParser(description='Download a file or directory', prog='dl')
            parser.add_argument('source')
            parser.add_argument('dest', nargs='?')

            try:
                args = parser.parse_args(args)
                nimbus.download(args.source, args.dest)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'ul':
            parser = ArgumentParser(description='Upload a file or directory', prog='ul')
            parser.add_argument('source')
            parser.add_argument('dest', nargs='?')

            try:
                args = parser.parse_args(args)
                nimbus.upload(args.source, args.dest)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'quota':
            parser = ArgumentParser(description='Show how much total and daily storage is left', prog='quota')
        
            parser.add_argument('-l', '--long', action='store_true', help='use a long format (shows storage in bytes)')

            try:
                args = parser.parse_args(args)

                a, b, c = nimbus.quota()

                unit = 'Bytes'

                if not args.long:
                    unit = 'GB'
                    cv = 1000**3

                    a = round(a/cv, 2)
                    b = round(b/cv, 2)
                    c = round(c/cv, 2)

                print(f'Total: {a}/{b} {unit}\nDaily: {c}/{b} {unit}')
            except SystemExit as e:
                print(e)
        elif cmd == 'passwd':
            parser = ArgumentParser(description='Change your password', prog='passwd')

            try:
                parser.parse_args(args)

                inp = pwinput.pwinput(prompt = 'Current password: ')
                inp = hashlib.md5(bytes(inp, 'utf-8')).hexdigest()

                if inp == pwd:
                    n1 = pwinput.pwinput(prompt = 'New password: ')

                    if nimbus.is_valid_passwd(n1):
                        n2 = pwinput.pwinput(prompt = 'Retype new password: ')

                        if n1 == n2:
                            pwd = hashlib.md5(bytes(n1, 'utf-8')).hexdigest()
                            nimbus.change_pwd(pwd)
                            nimbus.init(passwd=pwd)

                            print(f'Password changed.')
                        else:
                            print('Passwords do not match.')
                    else:
                        print('Invalid password.')
                else:
                    print('Incorrect password.')
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'pwd':
            parser = ArgumentParser(description='Show the current directory', prog='pwd')

            try:
                parser.parse_args(args)
                print(nimbus.current_dir())
            except SystemExit as e:
                print(e)
        else:
            print(f"Error: Command '{cmd}' does not exist.")