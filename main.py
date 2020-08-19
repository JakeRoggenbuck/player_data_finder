from position_reader import PositionReader
from config import Config
from ftplib import FTP
import inquirer
import json
import os


class FTPConnection:
    def __init__(self):
        self.server = FTP()

    def connect(self):
        self.server.connect(Config.host, Config.port)

    def login(self):
        self.server.login(Config.username, Config.password)

    def start(self):
        self.connect()
        self.login()


class UsernameCache:
    def __init__(self):
        self.ftp = FTPConnection()
        self.ftp.start()
        self.path = "/"
        self.name = "usernamecache.json"
        self.data = []

    def handle_binary(self, more_data):
        self.data.append(more_data.decode('utf-8'))

    def get_usernames(self):
        self.ftp.server.cwd(self.path)
        self.ftp.server.retrbinary(f"RETR {self.name}",
                                   callback=self.handle_binary)

    def return_file(self):
        return "".join(self.data)

    def get_json(self):
        return json.loads(self.return_file())


class Username:
    def __init__(self):
        self.usernamecache = UsernameCache()
        self.usernamecache.get_usernames()
        self.json = self.usernamecache.get_json()
        self.usernames = []
        self.new_json = self.get_new_json()

    def get_new_json(self):
        return dict((y, x) for x, y in self.json.items())


class AskUsername:
    def __init__(self):
        self.username = Username()
        self.json = self.username.new_json

    def get_username(self):
        usernames = self.json.keys()
        questions = [inquirer.Checkbox(
            "Username",
            message="Select username",
            choices=usernames
        )]
        answers = inquirer.prompt(questions)
        return answers

    def get_uuid(self):
        username = self.get_username()["Username"][0]
        return self.json[username]


class GetDataFile:
    def __init__(self):
        self.ftp = FTPConnection()
        self.ftp.start()
        self.path = "/RAT STANDO/playerdata/"
        self.username = AskUsername()
        self.uuid = self.username.get_uuid()
        self.filename = f"{self.uuid}.dat"
        self.full_path = os.path.join("data/", self.filename)

    def save_file(self):
        self.ftp.server.cwd(self.path)
        self.ftp.server.retrbinary(f"RETR {self.filename}",
                                   open(self.full_path, 'wb').write)


if __name__ == "__main__":
    datafile = GetDataFile()
    datafile.save_file()
    path = datafile.full_path
    pr = PositionReader(path)
    pos = pr.get_pos()
    print(pos)
