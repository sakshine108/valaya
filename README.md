# Nimbus

Nimbus is a cloud storage system aimed to be low cost, secure, and customizable. Currently, we are giving access to 100 GB of cloud storage free of charge for testing purposes.

# Installation

## Create an Account

To create an account for testing, email us at [sakshine108@gmail.com](mailto:sakshine108@gmail.com). We will make you an account and reply with the account details.

## Install and Run

Make sure you have **python** and **git** installed and up to date.

1. Clone this repository:
```
git clone https://github.com/sakshine108/nimbus.git
```

2. Change your directory into the cloud folder:
```
cd nimbus
```

3. Install the requirements:
```
pip install -r requirements.txt
```

4. Open the `config` file and replace the first and second line with your account username and password.

5. Run the interface:
```
python3 nimbus_cli.py
```

6. Backup your `key` file.

> **Warning**
> If you lose your file encryption key, you won't be able to access any of your uploaded files!

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

# More Info

* There is a maximum quota of 100 GB
* You can only upload and download a total of 100 GB per day

# Feedback

If you have any feedback, please [email](mailto:sakshine108@gmail.com) us.
