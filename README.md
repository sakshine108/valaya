# Nimbus

Nimbus is a low cost, secure, and customizable cloud storage system. Currently, we are giving free access to 15 GB of cloud storage for testing purposes.

# Install and Run

1. You can install Nimbus with pip:
```
pip install nimbus-cloud
```

2. Create an account:
```
nimbus signup
```

This command will ask you for an email, password, and encryption key filepath (e.g., /home/nimbus/key.txt), and create you an account. It will save your account details and encryption key filepath to the `config.yaml` file located in the package directory. It will create an encryption key file with the filepath you specified. If an existing encryption key file already exists with the same filepath, it will not be overwritten. **Make sure to backup your encryption key!**

Sign in to Nimbus:
```
nimbus signin
```

3. Run the interface:
```
nimbus
```

# Interface

This system comes with a command line interface.

### List of Commands

| Command                                         | Description                                                                                                                                            |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `b`                                             | Change to the previous directory.                                                                                                                      |
| `cd [directory]`                                | Change to a different directory.                                                                                                                       |
| `dl [source file path] [destination file path]` | Download a file or directory. The source is the path on the cloud and the destination is the path on the local filesystem once its downloaded.         |
| `ls [-l] [directory]`                           | List files in a directory. <ul><li>`-l` Use a long listing format. (Additionally shows file size and time of upload.) </li></ul>                       |
| `mv [old file path] [new file path]`            | Move or rename a file. The source is the path on the cloud of the file you want to move and the destination is the modified path.                      |
| `passwd`                                        | Change your password.                                                                                                                                  |
| `pwd`                                           | Show the current directory.                                                                                                                            |
| `q`                                             | Quit the interface.                                                                                                                                    |
| `quota [-l]`                                    | Show how much total and daily storage is left. <ul><li>`-l` Use a long format. (Shows storage in bytes.) </li></ul> |
| `rm [-f] [file path]`                           | Move a file or directory into the trash folder. <ul><li>`-f` Permanently delete a file or directory. </li></ul>                                     |
| `ul [source file path] [destination file path]` | Upload a file or directory. The source is the path on the local filesystem and the destination is the path on the cloud once its uploaded.             |

# Privacy & Security

### Encryption

Files uploaded to our servers are encrypted with 256 bit AES encryption. Only you can decrypt your files. **Keep in mind that if you lose your encryption key you will not be able to access your files, so make a backup.**

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

#### `nimbus.init(user=None, passwd=None, key_path=None)`
Initializes the module. Sets all of the required variables. **This function needs to be called before calling any other function.** If you do not set a parameter, it will be automatically set based on what is in the configuration file. Every time you set a parameter, it will be saved in the configuration file.

* `user` (str): Your Nimbus account username
* `passwd` (str): Your Nimbus account password
* `key_path` (str): File path of your encryption key

#### `nimbus.list(path, stats=False)`
Returns a list of your files and folders in the cloud. If `stats=True`, it will also return the file details (date/time of upload, file size).

#### `nimbus.list_all(stats=False)`
Returns a list of the absolute paths of all your files. If `stats=True`, it will also return the file details (date/time of upload, file size).

#### `nimbus.current_dir()`
Returns the path of your current directory.

#### `nimbus.change_dir(path)`
Changes your current directory to `path`.

#### `nimbus.back()`
Changes your current directory to a directory back.

#### `nimbus.upload(src, dst=None, show_prog=True)`
Uploads a file or directory to the cloud. `src` is the source path on your local filesystem you want to upload. `dst` is the destination on the cloud. If `show_prog=True`, a progress bar will be shown.

If you don't set a destination, the file or directory will be uploaded to your current directory.

#### `nimbus.download(src, dst=None, show_prog=True)`
Downloads a file or directory to your local filesystem. `src` is the source path on the cloud you want to download. `dst` is the destination on the local filesystem. If `show_prog=True`, a progress bar will be shown.

If you don't set a destination, the file or directory will be downloaded to your current directory.

#### `nimbus.move(src, dst)`
Moves a file or directory from the source (`src`) to destination (`dst`). Both parameters are required to be set.

#### `nimbus.remove(path, trash=True)`
Removes a file or directory from the cloud. `path` is the path of the file or directory you want to delete.

#### `nimbus.quota()`
Returns a tuple with the total amount of storage you have used so far in bytes, the maximum amount of storage you have in bytes, and the total amount of storage you have used so far in the day.

#### `nimbus.change_pwd(new_pwd)`
Changes your Nimbus account password to `new_pwd`.

# More Info

* There is a maximum quota of 15 GB
* You can only upload and download the amount of your maximum quota per day

# Feedback

If you have any feedback, please [email](mailto:sakshine108@gmail.com) us.