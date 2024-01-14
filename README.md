## Valaya

Valaya is a secure and customizable cloud storage system built with an open source client. We currently offer free 15 GB of cloud storage, with more monthly plans coming later.

![](https://github.com/sakshine108/valaya/blob/main/demo.gif)

---

## Install and Run

To install Valaya, open a terminal and complete the following steps.

1. Install with pip:
```
pip install valaya
```

2. Create an account. (Replace `your_email` with your email address):
```
valaya -su your_email
```

3. Launch the Valaya command line interface:
```
valaya
```

---

## Valaya Command Line Interface

The Valaya command line interface (VCLI) provides a simple and efficient way to interact with Valaya directly from a terminal.

### Launch

To launch the VCLI, open a terminal and run the following command:

```
valaya
```

All other commands and options:

| Command (from terminal) | Description           |
| ----------------------- | --------------------- |
| `valaya`                | Launch the VCLI.      |
| `valaya -si`            | Sign in.              |
| `valaya -su`            | Sign up.              |
| `valaya -pw`            | Change your password. |

### VCLI Commands

All commands availible in the VCLI:

| Command (from VCLI)                 | Description                                                                                                                                    |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `ul source_path [destination_path]` | Upload a file or directory. The source is the path on the local filesystem and the destination is the path on the cloud once its uploaded.     |
| `dl source_path [destination_path]` | Download a file or directory. The source is the path on the cloud and the destination is the path on the local filesystem once its downloaded. |
| `ls [-l] [directory]`               | List files in a directory. <ul><li>`-l` Use a long listing format. (Additionally shows file size and time of upload.) </li></ul>               |
| `cd [directory]`                    | Change to a different directory.                                                                                                               |
| `mv old_path new_path`              | Move or rename a file. The source is the path on the cloud of the file you want to move and the destination is the modified path.              |
| `rm [-f] path`                      | Move a file or directory into the trash folder. <ul><li>`-f` Permanently delete a file or directory. </li></ul>                                |
| `quota [-l]`                        | Show how much total and daily storage is left. <ul><li>`-l` Use a long format. (Shows storage in bytes.) </li></ul>                            |
| `pwd`                               | Show the current directory.                                                                                                                    |
| `q`                                 | Quit the interface.                                                                                                                            |

---

## Privacy and Security

### Encryption
All files uploaded to Valaya are encrypted with AES-256. Only those who know your encryption password can decrypt your files. Your encryption password is not stored anywhere. Additionally, this system uses TLS to secure all communications between the client and server.

### Password Storage
We store your account passwords on our server using bcrypt. For security reasons, your passwords are not stored on your systems.

---

## Module Documentation

### Usage Example

Here's a basic example of how you can use the `valaya` module:

```python
import valaya

pw = 'your_password'
key_pw = 'your_encryption_password'

# Gets values from the configuration file
ip, port, usr = valaya.get_config().values()

# Creates a user object
user = valaya.User(ip, port, usr, pw, key_pw)

# Uploads a file called 'image.png'
user.upload('image.png')
print('Upload Complete!')

# Renames 'image.png' to 'logo.png'
user.move('image.png', 'logo.png')

# Lists all files
files = user.list_all()
print(files)

# Downloads 'logo.png' as 'logo_downloaded.png'
user.download('logo.png', 'logo_downloaded.png')

# Permanently deletes all files
for file in files:
    user.remove(file, False)
```

### Getting Started

To get started with the `valaya` module, import and create a user object:

```python
import valaya

ip = 'valaya.io'
port = 4000
user = 'your_username'
pw = 'your_password'
key_pw = 'your_encryption_password'

user = valaya.User(ip, port, user, pw, key_pw)
```

### Functions

#### `User.list(path='', stats=False)`
Returns a list of your files and folders in the specified `path` on the cloud. If `stats` is set to `True`, it will also include additional file details such as the date and time of upload, as well as the file size. If no `path` is provided, it will list the files and folders in your current directory.

#### `User.list_all(stats=False)`
Returns a list of absolute paths for all your files stored on the cloud. If `stats` is set to `True`, it will also include additional file details such as the date and time of upload, as well as the file size.

#### `User.current_dir()`
Returns the path of your current directory on the cloud.

#### `User.change_dir(path)`
Changes your current directory on the cloud to the specified `path` (a string representing the new directory location).

#### `User.upload(src, dst=None, show_prog=True)`
Uploads a file or directory from your local filesystem to your cloud storage.

* `src` (str): The source path of the fle or directory on your local filesystem that you want to upload.
* `dst` (str): The destination path where the file or directory will be uploaded to on your cloud storage. If this parameter is not set, the file or directory will be uploaded into your current directory on the cloud.
* `show_prog` (bool): If set to `True`, a progress bar indicating the upload progress will be displayed during the upload process.

#### `User.download(src, dst=None, show_prog=True)`
Downloads a file or directory from your cloud storage to your local filesystem.

* `src` (str): The source path of the fle or directory on the cloud that you want to download.
* `dst` (str): The destination path where the file or directory will be downloaded to on your local filesystem. If this parameter is not set, the file or directory will be downloaded into your current directory.
* `show_prog` (bool): If set to `True`, a progress bar indicating the download progress will be displayed during the download process.

#### `User.move(src, dst)`
Moves a file or directory from a source location (`src`) to a destination location (`dst`). Both parameters are required to be set.

#### `User.remove(path, trash=True)`
Deletes a file or directory from the cloud.

* `path` (str): The path of the file or directory you wish to remove.
* `trash` (bool): Determines whether the file or directory will be moved to the trash (`True`) or permanently deleted (`False`). By default, the item will be moved to the trash.

#### `User.get_quota()`
Provides information about your storage usage. It returns a tuple with three integers:

1. The total amount of storage you have used so far in bytes.
2. The maximum amount of storage you have in bytes.
3. The total amount of storage you have used so far in the day.

#### `valaya.get_config()`
Returns a dictionary with the contents of your configuration file.

#### `valaya.set_config(new_config)`
Sets the contents of your configuration file to the values of `new_config` (dict).

---

## Contributing

* **GitHub Discussions**: [Discussions](https://github.com/sakshine108/valaya/discussions) are a great way to talk about features you want added or things that need clarification.
* **GitHub Issues**: [Issues](https://github.com/sakshine108/valaya/issues) are an excellent way to report bugs.