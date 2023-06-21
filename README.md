# Cloud Storage Testing

This is a cloud storage system aimed to be cheap and customizable. Right now, we are giving access to 100 GB of cloud storage free of charge for testing purposes. Later, we are planning to launch with a $5 monthly plan for 2 TB.

# Installation

## Create an account

To create an account for testing, email us at [sakshine108@gmail.com](mailto:sakshine108@gmail.com). We will make you an account and reply with the account details.

## Download and Run

Make sure you have [python](https://www.python.org/downloads/) and [git](https://git-scm.com/) installed and up to date.

1. Open a terminal and run ```git clone https://github.com/sakshine108/cloud.git```.

2. Change your directory into the cloud folder by running ```cd cloud```.

3. To install all the needed requirements, run ```pip install -r requirements.txt```.

4. Open ```account.txt``` and replace the first and second line with your account email and password.

5. Back in the terminal, run ```python3 cloud_interface.py```.

## Interface

This system comes with a command line interface.

| Command | Description |
|---------|-------------|
| ls [directory] | List files in a directory |
| cd [directory] | Change to a different directory |
| b | Change to the previous directory |
| ul [source] [destination] | Upload a file |
| dl [source] [destination] | Download a file |
| mv [source] [destination] | Move or rename a file |
| rm [file path] | Remove a file |
| quota | Show how much storage is left |
| passwd [new password] | Change password |
| q | Exit |

* All paths are relative to the current directory unless a "/" is placed before the path making it absolute
* For uploading a file, the source is the file path on the computer and the destination is the desired file path on the cloud
* For downloading a file, the source is the file path on the cloud and the destination is the desired file path on the computer
* For moving a file, the source is the file path on the cloud you want to move and the destination is the modified file path

Here are examples of how you can use these commands:

| Command | Description |
|---------|-------------|
| ul file1.txt | Uploads file1.txt to the current directory |
| ul file2.txt file_2.txt | Uploads file2.txt to the current directory as file_2.txt |
| ul file3.txt /documents/ | Uploads file3.txt to the documents folder located in the root directory. Automatically creates the documents folder if it does not already exist |
| ul file4.txt /documents/file_4.txt | Uploads file4.txt to the documents folder as file_4.txt |
| dl file1.txt | Downloads file1.txt to the current directory |
| dl file2.txt file_2.txt | Downloads file2.txt to the current directory as file_2.txt |
| dl file3.txt /home/sakshine108/Downloads/ | Downloads file3.txt to the Downloads folder in the computer |
| dl file4.txt /home/sakshine108/Downloads/file_4.txt | Downloads file4.txt to the Downloads folder as file_4.txt |
| mv file1.txt file_1.txt | Renames file1.txt to file_1.txt |
| mv file2.txt /documents/ | Moves file2.txt to the documents folder |
| mv file3.txt /documents/file_3.txt | Moves file3.txt to the documents folder as file_3.txt |

# Reporting Issues

If you encounter any issues, find a bug, or have any suggestions, please [email](mailto:sakshine108@gmail.com) us. We will try our best to find a solution.
