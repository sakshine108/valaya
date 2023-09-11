# Nimbus

Nimbus is a low cost, secure, and customizable cloud storage system. Currently, we are giving access to 100 GB of cloud storage free of charge for testing purposes.

# Installation

### Create an Account

To create an account for testing, [email](mailto:sakshine108@gmail.com) us. We will make you an account and reply with the account details.

### Install and Run

You can install Nimbus with pip:
```
pip install nimbus-cloud
```

Run the interface with your account details:
```
nimbus [username] [password] [file path for encryption key e.g. /home/nimbus/key.txt]
```

After running this, the interface will run. It will also create an encryption key file with the file path you specified. **Make sure to backup your encryption key!** Next time you run the interface, you won't need to specify any parameters since it automatically saves them.

# Interface

This system comes with a command line interface.

### List of Commands

| Command                                         | Description                                                                                                                                   |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `b`                                             | Changes to the previous directory.                                                                                                            |
| `cd [directory]`                                | Changes to a different directory.                                                                                                             |
| `dl [source file path] [destination file path]` | Downloads a file. The source is the file path on the cloud and the destination is the file path on the local filesystem once its downloaded.  |
| `ls [directory]`                                | Lists files in a directory.                                                                                                                   |
| `ls -l [directory]`                             | Lists files in a directory along with details (file size and upload date).                                                                    |
| `mv [old file path] [new file path]`            | Moves or renames a file. The source is the file path on the cloud of the file you want to move and the destination is the modified file path. |
| `passwd`                                        | Changes the password.                                                                                                                         |
| `pwd`                                           | Shows the current directory.                                                                                                                  |
| `q`                                             | Quits the interface.                                                                                                                          |
| `quota`                                         | Shows how much storage is left.                                                                                                               |
| `quota -l`                                      | Shows how much storage is left in bytes.                                                                                                      |
| `rm [file path]`                                | Removes a file.                                                                                                                               |
| `ul [source file path] [destination file path]` | Uploads a file. The source is the file path on the local filesystem and the destination is the file path on the cloud once its uploaded.      |

# Privacy & Security

### Encryption

Files uploaded to our servers are encrypted with AES using a 32 byte encryption key. Only you can decrypt your files. **Keep in mind that if you lose your encryption key you will not be able to access your files, so make a backup.**

# Documentation

### Basic Example

This is a basic example of how you can use this module.

```python
import nimbus

# Automatically sets the required parameters (assuming they have been set before)
nimbus.init()

# Uploads a file called 'image.png' from the local filesystem
nimbus.upload('image.png')
print('Upload Complete!')

# Renames 'image.png' to 'logo.png'
nimbus.move('image.png', 'logo.png')

# Lists all files
files = nimbus.list_all()
print(files)

# Downloads 'logo.png' from the cloud to the local filesystem as 'logo_downloaded.png'
nimbus.download('logo.png', 'logo_downloaded.png')

# Removes all files from the cloud
for file in files:
    nimbus.remove(file)
```

### Functions

If a function takes in a path, it can be both absolute and relative.

#### `nimbus.init(user, passwd, key_path)`
Initializes the module. Sets all of the required variables. **This function needs to be called before calling any other function.** If you do not set a parameter, it will be automatically set based on what is in the configuration file. Every time you set a parameter, it will be saved in the configuration file.

* `user` (str): Your Nimbus account username
* `passwd` (str): Your Nimbus account password
* `key_path` (str): File path of your encryption key

#### `nimbus.list(path, stats=False)`
Returns a list of your files and folders in the cloud. If your `path` is absolute (starts with a `/`), it lists relative to the root directory, otherwise it lists relative to your current directory. If `stats=True`, it will also return the file details (date/time of upload, file size).

#### `nimbus.list_all(stats=False)`
Returns a list of the absolute paths of all your files. If `stats=True`, it will also return the file details (date/time of upload, file size).

#### `nimbus.current_dir()`
Returns the path of your current directory.

#### `nimbus.change_dir(path)`
Changes your current directory to `path`. If your path is absolute (starts with a `/`), it will change relative to the root directory, otherwise it will change it relative to your current directory.

#### `nimbus.back()`
Changes your current directory to a directory back.

#### `nimbus.upload(src, dst, show_prog=True)`
Uploads a file to the cloud. `src` is the source path of the file on your local filesystem you want to upload. `dst` is the destination on the cloud. If `show_prog=True`, a progress bar will be shown.

Only `src` is required to be set to successfully upload. If you don't set a destination, the file will be uploaded to your current directory.

#### `nimbus.download(src, dst, show_prog=True)`
Downloads a file to your local filesystem. `src` is the source path of the file on the cloud you want to download. `dst` is the destination on the local filesystem. If `show_prog=True`, a progress bar will be shown.

Only `src` is required to be set to successfully download. If you don't set a destination, the file will be downloaded to your current directory.

#### `nimbus.move(src, dst)`
Moves a file from the source (`src`) to destination (`dst`). Both parameters need to be set.

#### `nimbus.remove(file_path)`
Removes a file from the cloud. `file_path` is the path of the file you want to delete.

#### `nimbus.quota()`
Returns a tuple with the total amount of storage you have used so far in bytes, and the maximum amount of storage you have in bytes.

#### `nimbus.change_pwd(new_pwd)`
Changes your Nimbus account password to `new_pwd`.

# More Info

* There is a maximum quota of 100 GB
* You can only upload and download a total of 100 GB per day

# Feedback

If you have any feedback, please [email](mailto:sakshine108@gmail.com) us.