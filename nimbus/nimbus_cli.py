import nimbus as nimbus
import humanize
import readline
import os
import sys
import pwinput
import pkg_resources

config_path = pkg_resources.resource_filename('nimbus', 'config.txt')

usr = ''
pwd = ''

def command(inp):
    global pwd
    
    cmd = inp.split(' ')[0]
    args = inp.split(' ')[1:]

    if cmd == '':
        pass
    elif cmd == 'quit' or cmd == 'q':
        quit()
    elif cmd == 'ls':
        try:
            if len(args) > 0:
                if args[0] == '-l':
                    if len(args) > 1:
                        l = nimbus.list(args[1], stats=True)
                    else:
                        l = nimbus.list(stats=True)
                else:
                    l = nimbus.list(args[0])
            else:
                l = nimbus.list()
            
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
        except Exception as e:
            print('Error: ' + str(e))
    elif cmd == 'cd':
        try:
            if len(args) > 0:
                nimbus.change_dir(args[0])
            else:
                nimbus.change_dir()
        except Exception as e:
            print('Error: ' + str(e))
    elif cmd == 'back' or cmd == 'b':
        try:
            nimbus.back()
        except Exception as e:
            print('Error: ' + str(e))
    elif cmd == 'mv':
        try:
            if len(args) > 1:
                nimbus.move(args[0], args[1])
            elif len(args) > 0:
                nimbus.move(args[0])
            else:
                nimbus.move()
        except Exception as e:
            print('Error: ' + str(e))
    elif cmd == 'rm':
        try:
            if len(args) > 0:
                nimbus.remove(args[0])
            else:
                nimbus.remove()
        except Exception as e:
            print('Error: ' + str(e))
    elif cmd == 'dl':
        try:
            if len(args) > 1:
                nimbus.download(args[0], args[1])
            elif len(args) > 0:
                nimbus.download(args[0])
            else:
                nimbus.download()
        except Exception as e:
            print('Error: ' + str(e))
    elif cmd == 'ul':
        try:
            if len(args) > 1:
                nimbus.upload(args[0], args[1])
            elif len(args) > 0:
                nimbus.upload(args[0])
            else:
                nimbus.upload()
        except Exception as e:
            print('Error: ' + str(e))
    elif cmd == 'quota':
        q1, q2 = nimbus.quota()

        a = humanize.naturalsize(q1)
        b = humanize.naturalsize(q2)

        if len(args) > 0:
            if args[0] == '-l':
                a = str(q1) + ' Bytes'
                b = str(q2) + ' Bytes'

        print(f'{a} of {b} used.')
    elif cmd == 'passwd':
        try:
            inp = pwinput.pwinput(prompt = "Current password: ")

            if inp == pwd:
                n1 = pwinput.pwinput(prompt = 'New password: ')
                n2 = pwinput.pwinput(prompt = 'Retype new password: ')

                if n1 == n2:
                    nimbus.change_pwd(n1)
                    nimbus.init(ip, port, usr, n1, key)

                    with open(config_path, 'r') as f:
                        lines = f.readlines()
                    
                    lines[1] = f'{n1}\n'
                    
                    with open(config_path, 'w') as f:
                        f.writelines(lines)

                    pwd = n1

                    print(f"Password changed to '{'*' * len(n1)}'.")
                else:
                    print('Passwords do not match.')
            else:
                print('Incorrect password.')
        except Exception as e:
            print('Error: ' + str(e))
    elif cmd == 'pwd':
        print(nimbus.current_dir())
    else:
        print(f"Error: Command '{cmd}' does not exist.")

if len(sys.argv) >= 4:
    usr = sys.argv[1]
    pwd = sys.argv[2]
    key_path = sys.argv[3]
    
    nimbus.init(user=usr, passwd=pwd, key_path=key_path)
else:
    nimbus.init()

    with open(config_path, 'r') as f:
        lines = f.readlines()

        usr = lines[0].replace('\n', '')
        pwd = lines[1].replace('\n', '')

def main():
    while True:
        inp = input(f'{usr} {nimbus.current_dir()} ❯ ')
        command(inp)