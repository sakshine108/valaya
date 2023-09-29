import nimbus
import humanize
import readline
import sys
import pwinput
import pkg_resources
import yaml
from yaml.loader import SafeLoader
import argparse

config_path = pkg_resources.resource_filename('nimbus', 'config.yaml')

with open(config_path) as f:
    config = yaml.load(f, Loader=SafeLoader)

usr = config['username']
pwd = config['password']

def sign_in():
    usr = input('Username: ')
    pwd = pwinput.pwinput(prompt = 'Password: ')
    key_path = input('Encryption key filepath: ')

    try:
        nimbus.init(usr, pwd, key_path)
    except Exception as e:
        print('Error: ' + str(e))

    quit()

def sign_up():
    user = input('Email: ')
    passwd = pwinput.pwinput(prompt = 'Password: ')
    passwd2 = pwinput.pwinput(prompt = 'Retype password: ')

    if passwd != passwd2:
        print('Passwords do not match.')
        quit()
    
    key_path = input('Encryption key filepath: ')

    try:
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
        
        cmd = args[0]
        args = args[1:]

        if cmd == '':
            pass
        elif cmd == 'q':
            parser = argparse.ArgumentParser(description='Quits the interface', prog='q')
            parser.parse_args(args)

            quit()
        elif cmd == 'ls':
            parser = argparse.ArgumentParser(description='Lists files in a directory', prog='ls')
            parser.add_argument("path", nargs='?', default='')
            parser.add_argument("-l", "--long", action="store_true")

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
            parser = argparse.ArgumentParser(description='Changes the working directory', prog='cd')
            parser.add_argument("path", nargs='?', default='/')

            try:
                args = parser.parse_args(args)
                nimbus.change_dir(args.path)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'back' or cmd == 'b':
            parser = argparse.ArgumentParser(description='Changes to the previous directory', prog='b')

            try:
                parser.parse_args(args)
                nimbus.back()
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'mv':
            parser = argparse.ArgumentParser(description='Moves or renames a file', prog='mv')
            parser.add_argument("source")
            parser.add_argument("dest")

            try:
                args = parser.parse_args(args)
                nimbus.move(args.source, args.dest)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'rm':
            parser = argparse.ArgumentParser(description='Removes a file', prog='rm')
            parser.add_argument("file")

            try:
                args = parser.parse_args(args)
                nimbus.remove(args.file)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'dl':
            parser = argparse.ArgumentParser(description='Downloads a file', prog='dl')
            parser.add_argument("source")
            parser.add_argument("dest", nargs='?', default='')

            try:
                args = parser.parse_args(args)
                nimbus.download(args.source, args.dest)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'ul':
            parser = argparse.ArgumentParser(description='Uploads a file', prog='ul')
            parser.add_argument("source")
            parser.add_argument("dest", nargs='?', default='')

            try:
                args = parser.parse_args(args)
                nimbus.upload(args.source, args.dest)
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'quota':
            parser = argparse.ArgumentParser(description='Shows how much storage is left', prog='quota')
        
            parser.add_argument("-l", "--long", action="store_true")

            try:
                args = parser.parse_args(args)

                q1, q2 = nimbus.quota()

                a = humanize.naturalsize(q1)
                b = humanize.naturalsize(q2)

                if args.long:
                    a = str(q1) + ' Bytes'
                    b = str(q2) + ' Bytes'

                print(f'{a} of {b} used.')
            except SystemExit as e:
                print(e)
        elif cmd == 'passwd':
            parser = argparse.ArgumentParser(description='Changes the password', prog='passwd')

            try:
                parser.parse_args(args)

                inp = pwinput.pwinput(prompt = "Current password: ")

                if inp == pwd:
                    n1 = pwinput.pwinput(prompt = 'New password: ')
                    n2 = pwinput.pwinput(prompt = 'Retype new password: ')

                    if n1 == n2:
                        pwd = n1
                        nimbus.change_pwd(pwd)
                        nimbus.init(passwd=pwd)

                        print(f"Password changed to '{'*' * len(n1)}'.")
                    else:
                        print('Passwords do not match.')
                else:
                    print('Incorrect password.')
            except SystemExit as e:
                print(e)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'pwd':
            parser = argparse.ArgumentParser(description='Shows the current directory', prog='pwd')

            try:
                parser.parse_args(args)
                print(nimbus.current_dir())
            except SystemExit as e:
                print(e)
        else:
            print(f"Error: Command '{cmd}' does not exist.")