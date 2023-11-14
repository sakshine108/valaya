
- [Summary](#summary)
- [Install and Run](#install-and-run)
- [Nimbus Command Line Interface (NCLI)](#nimbus-command-line-interface-ncli)
    - [CLI Commands](#cli-commands)
    - [NCLI Commands](#ncli-commands)
- [Data Encryption and Security Information](#data-encryption-and-security-information)
    - [Encryption](#encryption)
    - [Configuration File](#configuration-file)
- [Documentation](#documentation)
    - [Module Usage Example](#module-usage-example)
    - [Functions](#functions)
- [Feedback](#feedback)

---

# Summary

Nimbus is aimed to be a low cost, secure, and customizable cloud storage system. Currently, we are giving free access to 15 GB of cloud storage for testing purposes.

---

# Install and Run

1. You can install Nimbus with pip:
```
pip install nimbus-cloud
```

2. Create an account:
```
nimbus -su
```

You will be prompted to provide an email, password, and a file path for your encryption key (e.g., /home/nimbus/key.txt). The information you provide will be stored in your [configuration file](#configuration-file) and used to create your account.

3. Run the Nimbus command line interface (NCLI):
```
nimbus
```

---

# Nimbus Command Line Interface (NCLI)

To access the NCLI, simply run `nimbus` in your command line. The NCLI is designed to function like a standard CLI.

### CLI Commands

| Command       | Description                |
| ------------- | -------------------------- |
| `nimbus`      | Launch the NCLI.           |
| `nimbus -si`  | Sign in.                   |
| `nimbus -su`  | Sign up.                   |
| `nimbus -sub` | Subscribe to a plan.       |
| `nimbus -man` | Manage your subscriptions. |
| `nimbus -pw`  | Change your password.      |
| `nimbus -h`   | Show a help message.       |

### NCLI Commands

| Command                               | Description                                                                                                                                    |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `b`                                   | Change to the previous directory.                                                                                                              |
| `cd [directory]`                      | Change to a different directory.                                                                                                               |
| `dl [source path] [destination path]` | Download a file or directory. The source is the path on the cloud and the destination is the path on the local filesystem once its downloaded. |
| `ls [-l] [directory]`                 | List files in a directory. <ul><li>`-l` Use a long listing format. (Additionally shows file size and time of upload.) </li></ul>               |
| `mv [old path] [new path]`            | Move or rename a file. The source is the path on the cloud of the file you want to move and the destination is the modified path.              |
| `pwd`                                 | Show the current directory.                                                                                                                    |
| `q`                                   | Quit the interface.                                                                                                                            |
| `quota [-l]`                          | Show how much total and daily storage is left. <ul><li>`-l` Use a long format. (Shows storage in bytes.) </li></ul>                            |
| `rm [-f] [path]`                      | Move a file or directory into the trash folder. <ul><li>`-f` Permanently delete a file or directory. </li></ul>                                |
| `ul [source path] [destination path]` | Upload a file or directory. The source is the path on the local filesystem and the destination is the path on the cloud once its uploaded.     |

---

# Data Encryption and Security Information

### Encryption

Files uploaded to the cloud are secured with 256 bit AES encryption. Only you have the ability to decrypt your files. It's crucial to note that in the event of an encryption key loss, accessing your files will be impossible. Therefore, it's highly advisable to create a backup of your encryption key to safeguard your access. Additionally, all communication between the user and the server is also encryted, ensuring end-to-end security for all interactions with the cloud.

### Configuration File

Your username, password, and encryption key file path are stored securely in the `config.yaml` file, located in the `nimbus` folder in your [site-packages](https://www.geeksforgeeks.org/get-location-of-python-site-packages-directory/) directory.

---

# Documentation

### Module Usage Example

Here's a basic example of how you can use this module:

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

# Permanently deletes all files
for file in files:
    nimbus.remove(file, False)
```

### Functions

#### `nimbus.init(user=None, passwd=None, key_path=None)` <!-- omit from toc -->
This function initializes the module and sets all the required variables. **It is essential to call this function before using any other function in this module.** If you don't provide a parameter, the function will automatically use the values from the configuration file. Any parameter you set will be saved in the configuration file for future use.

* `user` (str): Your Nimbus account username.
* `passwd` (str): Your Nimbus account password.
* `key_path` (str): File path of your encryption key.

#### `nimbus.list(path='', stats=False)` <!-- omit from toc -->
This function returns a list of your files and folders in the specified `path` on the cloud. If `stats=True`, it will also include additional file details such as the date and time of upload, as well as the file size. If no `path` is provided, it will list the files and folders in your current directory.

#### `nimbus.list_all(stats=False)` <!-- omit from toc -->
This function returns a list of absolute paths for all your files stored on the cloud. If `stats=True`, it will also include additional file details such as the date and time of upload, as well as the file size.

#### `nimbus.current_dir()` <!-- omit from toc -->
This function returns the path of your current directory on the cloud.

#### `nimbus.change_dir(path)` <!-- omit from toc -->
This function changes your current directory on the cloud to the specified `path` (a string representing the new directory location).

#### `nimbus.back()` <!-- omit from toc -->
This function changes your current directory on the cloud to the parent directory.

#### `nimbus.upload(src, dst=None, show_prog=True)` <!-- omit from toc -->
This function allows you to upload a file or directory from your local filesystem to your cloud storage.

* `src` (str): Specifies the source path of the fle or directory on your local filesystem that you want to upload.
* `dst` (str): Specifies the destination path where the file or directory will be uploaded to on your cloud storage. If this parameter is not set, the file or directory will be uploaded into your current directory on the cloud.
* `show_prog` (bool): If set to `True`, a progress bar indicating the upload progress will be displayed during the upload process.

#### `nimbus.download(src, dst=None, show_prog=True)` <!-- omit from toc -->
This function allows you to download a file or directory from your cloud storage to your local filesystem.

* `src` (str): Specifies the source path of the fle or directory on the cloud that you want to download.
* `dst` (str): Specifies the destination path where the file or directory will be downloaded to on your local filesystem. If this parameter is not set, the file or directory will be downloaded into your current directory.
* `show_prog` (bool): If set to `True`, a progress bar indicating the download progress will be displayed during the download process.

#### `nimbus.move(src, dst)` <!-- omit from toc -->
This function moves a file or directory from a source location (`src`) to a destination location (`dst`). Both parameters are required to be set.

#### `nimbus.remove(path, trash=True)` <!-- omit from toc -->
This function allows you to delete a file or directory from the cloud.

* `path` (str): Specifies the path of the file or directory you wish to remove.
* `trash` (bool): Determines whether the file or directory will be moved to the trash (`True`) or permanently deleted (`False`). By default, the item will be moved to the trash.

#### `nimbus.quota()` <!-- omit from toc -->
This function provides information about your storage usage. It returns a tuple with three integers:

1. The total amount of storage you have used so far in bytes.
2. The maximum amount of storage you have in bytes.
3. The total amount of storage you have used so far in the day.

---

# Feedback

If you have any feedback, please [email](mailto:sakshine108@gmail.com) us.