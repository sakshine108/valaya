import valaya
from valaya import config
import humanize
import readline
from argparse import ArgumentParser
import pwinput
from outdated import check_outdated

is_outdated, latest_version = check_outdated('valaya', valaya.__version__)

if is_outdated:
    print(f"Your current version of Valaya ({valaya.__version__}) is outdated. Run 'pip install valaya -U' to update to the latest version ({latest_version}).")
    quit()

parser = ArgumentParser()
g = parser.add_mutually_exclusive_group()

g.add_argument('-su', '--signup', nargs=1, metavar=('email'), help='sign up')
g.add_argument('-si', '--signin', nargs=1, metavar=('email'), help='sign in')
g.add_argument('-pw', '--password', action='store_true', help='change your password')
g.add_argument('-v', '--version', action='store_true', help='show the current installed version')

args = parser.parse_args()

if args.signup is not None:
    pw = pwinput.pwinput(prompt='Set password: ')

    if pwinput.pwinput(prompt='Retype password: ') == pw:
        try:
            valaya.create_account(config.server.ip, config.server.port, args.signup[0], pw)

            code = input('Verification code: ')
            valaya.verify_account(config.server.ip, config.server.port, code)
        except Exception as e:
            print('Error: ' + str(e))
            quit()

        config.account.username = args.signup[0]
        config.set(config)
    else:
        print('Passwords do not match.')

    quit()
elif args.signin is not None:
    config.account.username = args.signin[0]
    config.set(config)
    
    quit()
elif args.password:
    pw = pwinput.pwinput(prompt='Current password: ')

    user = valaya.User(config.server.ip, config.server.port, config.account.username, pw)

    new_pw = pwinput.pwinput(prompt='New password: ')

    if pwinput.pwinput(prompt='Retype new password: ') == new_pw:
        user.change_pw(new_pw)
    else:
        print('Passwords do not match.')

    quit()
elif args.version:
    print(valaya.__version__)

if config.account.username:
    print(f"Signed in as '{config.account.username}'.")

    pw = pwinput.pwinput(prompt='Password: ')
    
    if not pw:
        print('Error: You must provide a password.')
        quit()
        
    key_pw = pwinput.pwinput(prompt='Encryption password: ')
        
    if not key_pw:
        print('Error: You must provide an encryption key password.')
        quit()

    try:
        user = valaya.User(config.server.ip, config.server.port, config.account.username, pw, key_pw)
    except Exception as e:
        print('Error: ' + str(e))
        quit()
else:
    print("Not signed in. Run 'valaya -si <your_username>' to sign in.")
    quit()

def main():
    while True:
        args = input(f'{config.account.username} /{user.c_dir} ❯ ').split()
        
        cmd = None
        
        if args:
            cmd, *args = args

        if not cmd:
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

                files = user.list(args.path, stats=args.long)
                
                for f in files:
                    if isinstance(f, list):
                        if len(f) > 1:
                            name, size, extra_info = f
                            size = humanize.naturalsize(size) + f', {size} Bytes'
                            print(f'{name} ({size}) ({extra_info})')
                        else:
                            print(f[0])
                    else:
                        print(f)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'cd':
            parser = ArgumentParser(description='Change the working directory', prog='cd')
            parser.add_argument('path', nargs='?', default='/')

            try:
                args = parser.parse_args(args)
                user.change_dir(args.path)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'mv':
            parser = ArgumentParser(description='Move or rename a file or directory', prog='mv')
            parser.add_argument('source')
            parser.add_argument('dest')

            try:
                args = parser.parse_args(args)
                user.move(args.source, args.dest)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'rm':
            parser = ArgumentParser(description='Move a file or directory into the trash folder', prog='rm')
            parser.add_argument('-f', '--force', action='store_false', help='permanently delete a file or directory')
            parser.add_argument('file')

            try:
                args = parser.parse_args(args)
                user.remove(args.file, args.force)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'dl':
            parser = ArgumentParser(description='Download a file or directory', prog='dl')
            parser.add_argument('source')
            parser.add_argument('dest', nargs='?')

            try:
                args = parser.parse_args(args)
                user.download(args.source, args.dest)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'ul':
            parser = ArgumentParser(description='Upload a file or directory', prog='ul')
            parser.add_argument('source')
            parser.add_argument('dest', nargs='?')

            try:
                args = parser.parse_args(args)
                user.upload(args.source, args.dest)
            except Exception as e:
                print('Error: ' + str(e))
        elif cmd == 'quota':
            parser = ArgumentParser(description='Show how much total and daily storage is left', prog='quota')
        
            parser.add_argument('-l', '--long', action='store_true', help='use a long format (shows storage in bytes)')

            args = parser.parse_args(args)

            a, b, c = user.get_quota()

            unit = 'Bytes'

            if not args.long:
                unit = 'GB'
                cv = 1000**3

                a = round(a/cv, 2)
                b = round(b/cv, 2)
                c = round(c/cv, 2)

            print(f'Total: {a}/{b} {unit}\nDaily: {c}/{b} {unit}')
        elif cmd == 'pwd':
            parser = ArgumentParser(description='Show the current directory', prog='pwd')

            parser.parse_args(args)
            print('/' + user.c_dir)
        else:
            print(f"Error: Command '{cmd}' does not exist.")