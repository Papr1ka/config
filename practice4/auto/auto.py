import subprocess
from enum import Enum
from typing import List, Dict
from sstack import Stack
import json
from os import path
from hashlib import sha256


class Colors(Enum):
    """
    Цвета для топологической сортировки
    """
    white = 0  # Не обработана
    gray = 1  # В обработке
    black = 2  # Обработана


class Task:
    """
    Задача
    """
    color: Colors  # Цвет для топологической сортировки
    requires: List[str]  # Список требуемых выполненных задач
    name: str  # Имя задачи
    commands: List[str]  # Список команд

    def __init__(self, name: str = "", requires=None, commands=None):
        self.color = Colors.white
        self.requires = [] if requires is None else requires
        self.name = name
        self.commands = [] if commands is None else commands

    def __str__(self):
        return self.name if self.name != "" else "Undefined"

    def __repr__(self):
        return self.__str__()


class Auto:
    """
    Класс, хранящий, сортирующий и выполняющий задачи
    """
    stack: Stack
    targets: Dict[str, Task]
    mock_name: str
    mock: dict
    order: List[Task]
    print_tasks: bool

    def __init__(self, print_tasks=False, mock_name="auto.mock.json"):
        # гарантирует наличие файла mock_name
        self.targets = {}
        self.stack = Stack()
        self.mock_name = mock_name
        if path.exists(self.mock_name):
            with open(self.mock_name) as file:
                self.mock = json.loads("".join(file.readlines()))
        else:
            with open(self.mock_name, "w") as file:
                file.writelines(json.dumps({}))
            self.mock = {}
        self.print_tasks = print_tasks

    @staticmethod
    def get_file_hash(filename) -> str:
        """
        Хэширует файл
        filename - имя файла
        """
        hash_builder = sha256()
        with open(filename, "rb") as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                hash_builder.update(data)
            return hash_builder.hexdigest()

    def compile(self, task: str):
        """
        Рекурсивный метод для топологической
        task - задача
        """
        task_object = self.targets.get(task)
        # Проверка на существование файла
        if task_object is None and path.exists(task) and path.isfile(task):
            new_hash = self.get_file_hash(task)
            old_hash = self.mock.get(task)
            if not (new_hash == old_hash and new_hash is not None):
                self.mock[task] = new_hash
                return True
            return False

        # получение объекта задачи
        task_object = self.targets.get(task)
        if task_object is None:
            raise KeyError(f"Задача {task} не определена")

        # если уже обработана
        if task_object.color == Colors.black:
            return False

        # если есть ссылка не обрабатываемую (цикл)
        if task_object.color == Colors.gray:
            raise ValueError(f"Обнаружен цикл зависимостей {task}")

        # начало обработки
        task_object.color = Colors.gray

        # зависимости
        is_actual = True
        for i in task_object.requires:
            try:
                r = self.compile(i)
            except ValueError:
                print(f"Циклическая зависимость {task_object.name} -> {i} пропущена")
            else:
                # если r True, то i нужно обновить, значит и сама задача нуждается в обновлении
                if r is True:
                    is_actual = False

        # если нужно обновить
        if is_actual is False:
            task_object.color = Colors.black
            try:
                new_hash = self.get_file_hash(task_object.name)
            except (FileNotFoundError, IsADirectoryError):
                pass
            else:
                self.mock[task_object.name] = new_hash
            self.stack.push(task_object)
            task_object.color = Colors.black
            return True

        try:
            new_hash = self.get_file_hash(task_object.name)
        except (FileNotFoundError, IsADirectoryError):
            new_hash = None
        old_hash = self.mock.get(task_object.name)
        if new_hash == old_hash and new_hash is not None:
            task_object.color = Colors.black
            return False
        else:
            if new_hash is not None:
                self.mock[task_object.name] = new_hash
            self.stack.push(task_object)
            task_object.color = Colors.black
            return True

    def reverse(self):
        """
        Переводит список задач из стека в список
        """
        order = []
        while len(self.stack):
            order.append(self.stack.pop())
        order = list(reversed(order))
        self.order = order
        if self.print_tasks:
            print("\n".join([str(i) for i in order]))
            print()

    def create_task(self, task: Task):
        """
        Добавляет задачу
        """
        if self.targets.get(task.name) is not None:
            raise ValueError(f"Задача уже {task.name} уже определена")
        self.targets[task.name] = task

    def save(self):
        """
        Перезаписывает файл с хэш-значениями файлов
        """
        with open(self.mock_name, "w") as file:
            file.writelines(json.dumps(self.mock))

    def execute(self, key: str):
        """
        Выполняет задачу
        key - имя задачи
        """
        self.compile(key)
        self.save()
        self.reverse()

        f = lambda x: path.exists(x) and path.isfile(x)

        for task in self.order:
            if self.print_tasks:
                print(task.name)

            exists = f(task.name)
            for command in task.commands:
                print(command)
                subprocess.run(command, shell=True)
            exists_after = f(task.name)
            if exists is False and exists_after is True:
                hash = self.get_file_hash(task.name)
                self.mock[task.name] = hash
        self.save()


class AutoGraph(Auto):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import graphviz
        self.graph = graphviz.Digraph("Зависимости", filename="deps.gv", engine="dot")
        self.graph.attr(ranksep="3")

    def create_task(self, task: Task):
        """
        Добавляет задачу и рисует граф
        """
        super().create_task(task)
        self.graph.node(task.name)
        for i in task.requires:
            self.graph.edge(task.name, i)

    def view(self):
        self.graph.view()
