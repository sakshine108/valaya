# cloud.list(path, stats=False) --> returns a list of the user's files and file details
# cloud.current_dir() --> returns the current direcrory
# cloud.change_dir(path) --> changes the current directory
# cloud.back() --> goes back a directory
# cloud.move(src, dst) --> moves a file
# cloud.remove(path) --> deletes a file
# cloud.download(src, dst, prog=True) --> downloads a file and displays the download progress
# cloud.upload(src, dst, prog=True) --> uploads a file and displays the upload progress
# cloud.quota() --> shows how many bytes of storage you used and the maximum amount you can have
# cloud.change_pwd(new_pwd) --> changes the account password
# cloud.init(usr, pwd) --> initializes the api, setting the username and password (this function must be called before any other function is called)

import cloud
import humanize
import readline

f = open('account.txt', 'r').readlines()

usr, pwd = [sub.replace('\n', '') for sub in f]

def command(inp):
    global pwd
    
    req = inp.split(' ')[0]
    params = inp.split(' ')[1:]

    if req == '':
        pass
    elif req == 'quit' or req == 'q':
        quit()
    elif req == 'ls':
        try:
            if len(params) > 0:
                if params[0] == '-l':
                    if len(params) > 1:
                        l = cloud.list(params[1], stats=True)
                    else:
                        l = cloud.list(stats=True)
                else:
                    l = cloud.list(params[0])
            else:
                l = cloud.list()
            
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
    elif req == 'cd':
        try:
            if len(params) > 0:
                cloud.change_dir(params[0])
            else:
                cloud.change_dir()
        except Exception as e:
            print('Error: ' + str(e))
    elif req == 'back' or req == 'b':
        try:
            cloud.back()
        except Exception as e:
            print('Error: ' + str(e))
    elif req == 'mv':
        try:
            if len(params) > 1:
                cloud.move(params[0], params[1])
            elif len(params) > 0:
                cloud.move(params[0])
            else:
                cloud.move()
        except Exception as e:
            print('Error: ' + str(e))
    elif req == 'rm':
        try:
            if len(params) > 0:
                cloud.remove(params[0])
            else:
                cloud.remove()
        except Exception as e:
            print('Error: ' + str(e))
    elif req == 'dl':
        try:
            if len(params) > 1:
                cloud.download(params[0], params[1])
            elif len(params) > 0:
                cloud.download(params[0])
            else:
                cloud.download()
        except Exception as e:
            print('Error: ' + str(e))
    elif req == 'ul':
        try:
            if len(params) > 1:
                cloud.upload(params[0], params[1])
            elif len(params) > 0:
                cloud.upload(params[0])
            else:
                cloud.upload()
        except Exception as e:
            print('Error: ' + str(e))
    elif req == 'quota':
        q1, q2 = cloud.quota()

        a = humanize.naturalsize(q1)
        b = humanize.naturalsize(q2)

        if len(params) > 0:
            if params[0] == '-l':
                a = str(q1) + ' Bytes'
                b = str(q2) + ' Bytes'

        print(f'{a} of {b} used.')
    elif req == 'passwd':
        try:
            if len(params) > 0:
                c = input('Your password: ')

                if c == pwd:
                    new_pwd = params[0]
                    cloud.change_pwd(new_pwd)

                    cloud.init(usr, new_pwd)

                    f = open("account.txt", "w")
                    f.write(f'{usr}\n{new_pwd}')
                    f.close()

                    pwd = new_pwd

                    print(f"Password changed to '{new_pwd}'.")
                else:
                    print('Incorrect password.')
            else:
                cloud.change_pwd()
        except Exception as e:
            print('Error: ' + str(e))
    else:
        print(f"Error: Command '{req}' does not exist.")

try:
    cloud.init(usr, pwd)
except Exception as e:
    print('Error: ' + str(e))
    quit()

while True:
    inp = input(f'{usr} {cloud.current_dir()} ❯ ')
    command(inp)
