from typing import Dict

from fs.wrapfs import WrapFS
from fs import path
from fs.errors import IllegalBackReference
from filesystem import ArchiveFileSystemFactory
import queue
from collections import namedtuple
from os import getlogin, uname

# Командный блок, включает название функции командной строки и аргументы,
# передаваемые в этот метод
# Tuple[func: str, args: List[str]]
command_block = namedtuple("call", ["func", "args"])


# Ошибки уровня команд и всего эмулятора
exceptions = {
    'InvalidPath': "Неверно задан путь",
    'NotAFile': "Путь должен указывать на файл",
    'NotATxt': "Путь должен указывать на текстовый файл",
    'NotADir': "Путь должен указывать на папку",
    'InvalidArgs': "Неверно заданы параметры",
    'CommandNotFound': "Команда не найдена",
    'Error': "Ошибка"
}


class VShell:
    """
    Класс, реализующий эмулятор командной строки

    Список всех доступных функций:
    pwd - выводит путь к текущей директории
    ls - выводит список файлов и каталогов в директории
    cd - переходит в новую директорию по пути
    cat - выводит содержимое файла по пути

    Все методы, реализующие функции возвращают либо str, либо List[str], либо None
    Ошибки функций также выводятся в качестве результата

    Метод handle_input не заботится о корректности пользовательского ввода, это реализуется в методе pipeline

    Команды поддерживают последовательное выполнение, символ && зарезервирован и не может быть передан в качестве параметра
    command1 args1 && command2 args2
    Пример:
    cd system && ls && cd root && ls && cd ../../ && cat ./system/root/test.txt
    """
    filesystem: WrapFS # Объект файловой системы из пакета fs, работающий конкретно для открытого архива
    current_path: str # Текущий путь
    local_path: str # Имя текущей директории (При current_path ='/root/bin', local_path -> '/bin')
    q: queue # Очередь выполнения команд, элемент очереди типа command_block
    commands: Dict[str, callable] # Словарь функций командной строки (методов класса VShell)
    user: str # Имя пользователя командной строки
    node_name: str # Имя машины в сети

    def CorrectPath(func):
        """
        Декоратор, применим к функциям с 1-м фактическим аргументом - именем файла
        В случае, если имя файла неразрешимое, возвращается строка ошибки
        """
        def wrapper(self, *file_name):
            file_name = " ".join(file_name) # Для поддержки имён с пробельными символами
            try:
                new_path = path.join(self.current_path, file_name)
            except IllegalBackReference:
                return exceptions['Error'] + ": " + exceptions['InvalidPath']
            else:
                if (not self.filesystem.exists(new_path)):
                    return exceptions['Error'] + ": " + exceptions['InvalidPath']

            return func(self, new_path)

        return wrapper

    def input(self):
        # Функция ввода
        try:
            return input()
        except KeyboardInterrupt:
            print()
            exit(0)

    def pwd(self):
        # Функция вывода текущего пути
        return self.current_path

    def ls(self):
        # Функция печати всех директорий и файлов в текущем каталоге
        return list(self.filesystem.listdir(self.current_path))

    @CorrectPath
    def cd(self, filename="."):
        # Функция перехода в другую директорию
        if self.filesystem.isdir(filename):
            self.change_path(filename)
        else:
            return exceptions['Error'] + ": " + exceptions['NotADir']

    @CorrectPath
    def cat(self, filename="."):
        # Функция вывода содержимого файла
        if (self.filesystem.isfile(filename)):
            try:
                return self.filesystem.gettext(filename)
            except ValueError:
                return exceptions['Error'] + ": " + exceptions['NotATxt']
        return exceptions['Error'] + ": " + exceptions['NotAFile']

    def handle_input(self, user_input: str):
        """
        Метод обработки пользовательского ввода
        поддерживает последовательное выполнение команд через символ '&&'
        Команды добавляются в очередь

        Метод не является ответственным за проверку названия команды на валидность
        """
        if user_input != "":
            commands = user_input.split("&&")
            for block in commands:
                command_params = block.split()
                if len(command_params) > 0:
                    command = command_params[0]
                    params = command_params[1:]

                    self.q.put_nowait(command_block(
                        command,
                        params
                    ))

    def get_commands(self):
        # Метод, возвращающий словарь команд, поддерживаемых эмулятором командной строки
        return {
            'pwd': self.pwd,
            'ls': self.ls,
            'cd': self.cd,
            'cat': self.cat
        }

    def refresh_shell(self):
        # Метод вывода информационной строки типа '[{пользователь}@{имя_системы_в_сети} {текущая директория}]$ '
        print(f"[{self.user}@{self.node_name} {self.local_path}]$", end=" ")

    def change_path(self, new_path: str):
        # Метод обработки нового пути
        self.current_path = new_path
        last = new_path.split("/")[-1]
        if last == "":
            self.local_path = "/"
        else:
            self.local_path = last

    def pipeline(self):
        # Метод, реализующий цикл выполнения команд для единичного пользовательского ввода
        user_input = self.input()
        self.handle_input(user_input)

        while not self.q.empty():
            command_name, args = self.q.get_nowait()
            func = self.commands.get(command_name) # получаем объект метода, реализующего функцию
            if func is None:
                print(exceptions['Error'] + ":", command_name + ":", exceptions['CommandNotFound'])
                continue

            try:
                result = func(*args)
            except TypeError as E:
                print(exceptions['Error'] + ":", exceptions['InvalidArgs'] + ":", E)
            except Exception as E:
                print(exceptions['Error'] + ":", E)
            else:
                if result is not None:
                    if isinstance(result, list):
                        print("\n".join(result))
                    else:
                        print(result)

        self.refresh_shell()

    def __init__(self, filename: str):
        self.filesystem = ArchiveFileSystemFactory.getSystem(filename)
        self.user = getlogin()
        self.node_name = uname().nodename
        self.filesystem.tree()
        self.change_path("/")
        self.q = queue.SimpleQueue()
        self.commands = self.get_commands()

    def run(self):
        # Метод запуска командной строки
        self.refresh_shell()
        while True:
            self.pipeline()
