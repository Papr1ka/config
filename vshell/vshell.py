from fs.wrapfs import WrapFS
from fs import path
from fs.errors import IllegalBackReference
from filesystem import ArchiveFileSystemFactory
import queue
from collections import namedtuple
from os import getlogin, uname

call = namedtuple("call", ["func", "args"])

exceptions = {
    'InvalidPath': "Неверно задан путь",
    'Error': "Ошибка",
    'NotAFile': "Путь должен указывать на файл",
    'NotATxt': "Путь должен указывать на текстовый файл",
    'NotADir': "Путь должен указывать на папку",
    'InvalidArgs': "Неверно заданы параметры"
}

class VShell():
    filesystem: WrapFS
    current_path: str
    local_path: str
    q: queue
    commands: dict
    user: str
    nodename: str

    def CorrectPath(func):
        def wrapper(self, *fname):
            fname = " ".join(fname)
            try:
                new_path = path.join(self.current_path, fname)
            except IllegalBackReference:
                return exceptions['Error'] + ": " + exceptions['InvalidPath']
            else:
                if (not self.filesystem.exists(new_path)):
                    return exceptions['Error'] + ": " + exceptions['InvalidPath']

            return func(self, new_path)
        return wrapper

    def input(self):
        try:
            return input()
        except KeyboardInterrupt:
            exit(0)

    def pwd(self):
        return self.current_path

    def ls(self):
        for name in self.filesystem.listdir(self.current_path):
            print(name)

    @CorrectPath
    def cd(self, filename="."):
        if self.filesystem.isdir(filename):
            self.changePath(filename)
        else:
            return exceptions['Error'] + ": " + exceptions['NotADir']

    @CorrectPath
    def cat(self, filename="."):
        if (self.filesystem.isfile(filename)):
            try:
                return self.filesystem.gettext(filename)
            except ValueError:
                return exceptions['Error'] + ": " + exceptions['NotATxt']
        return exceptions['Error'] + ": " + exceptions['NotAFile']

    def handleInput(self, input: str):
        if (input != ""):
            values = input.split()
            command = values[0]
            params = values[1:]
            if command in self.commands.keys():
                self.q.put_nowait(call(
                    self.commands.get(command),
                    params
                ))

    def getCommands(self):
        return {
            'pwd': self.pwd,
            'ls': self.ls,
            'cd': self.cd,
            'cat': self.cat
        }

    def refreshShell(self):
        print(f"[{self.user}@{self.nodename} {self.local_path}]$", end=" ")

    def changePath(self, path: str):
        self.current_path = path
        last = path.split("/")[-1]
        if (last == ""):
            self.local_path = "/"
        else:
            self.local_path = last


    def pipeline(self):
        user_input = self.input()
        self.handleInput(user_input)
        if not self.q.empty():
            func, args = self.q.get_nowait()
            try:
                result = func(*args)
            except exceptions as E:
                print(exceptions['Error'] + ": " + E)
            else:
                if (result != None):
                    print(result)
        self.refreshShell()

    def __init__(self, filename: str):
        self.filesystem = ArchiveFileSystemFactory.getSystem(filename)
        self.user = getlogin()
        self.nodename = uname().nodename
        self.filesystem.tree()
        self.changePath("/")
        self.q = queue.SimpleQueue()
        self.commands = self.getCommands()

    def run(self):
        self.refreshShell()
        while True:
            self.pipeline()
