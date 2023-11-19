from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Any, Tuple, Dict
from sstack import Stack
import json
from os import path
from hashlib import sha256

class Tasks(Enum):
    script = 0
    file = 1


class Colors(Enum):
    white = 0
    gray = 1
    black = 2

@dataclass
class TC:
    task: Any  # Task
    color: Colors

class Task(ABC):
    type: Tasks
    requires: List[str]
    name: str

    def __init__(self, type: Tasks, requires=None, name: str = ""):
        self.type = type
        self.requires = [] if requires is None else requires
        self.name = name

    def __str__(self):
        return self.name if self.name != "" else "Undefined"

    def __repr__(self):
        return self.__str__()


class Script(Task):
    commands: List[str]

    def __init__(self, commands: List[str], requires=None, **kwargs):
        super().__init__(Tasks.script, requires, **kwargs)
        self.commands = commands


class File(Task):

    def __init__(self, filename: str,):
        super().__init__(Tasks.file, name=filename)


class Auto:
    stack: Stack
    tasks: Dict[str, TC]
    mock_name = "auto.mock.json"
    mock: dict
    order: List[Task]

    def __init__(self):
        # self.tasks = [TC(task, Colors.white)]
        self.tasks = {}
        self.stack = Stack()
        if path.exists(self.mock_name):
            with open(self.mock_name) as file:
                self.mock = json.loads("".join(file.readlines()))
        else:
            with open(self.mock_name, "w") as file:
                file.writelines(json.dumps({}))
            self.mock = {}

    def sort(self, key: str):
        task = self.tasks[key]
        self.handle(task)
        self.save()

    def get_file_hash(self, filename):
        hash = sha256()
        with open(filename, "rb") as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                hash.update(data)
            return hash.hexdigest()

    def handle(self, task: TC):
        if task.color == Colors.black:
            return

        task.color = Colors.gray

        is_actual = True

        for req in task.task.requires:
            req: str
            req_task = self.tasks[req]

            if req_task.task.type == Tasks.file:
                new_hash = self.get_file_hash(req_task.task.name)
                old_hash = self.mock.get(req_task.task.name)
                if new_hash == old_hash:
                    req_task.color = Colors.black
                    is_actual = True
                    continue
                else:
                    self.mock[task.task.name] = new_hash
                    is_actual = False
                    break
            else:
                self.handle(req_task)

        task.color = Colors.black
        if not is_actual:
            self.stack.push(task.task)

    def view(self):
        order = []
        while len(self.stack):
            order.append(self.stack.pop())
        order = reversed(order)
        self.order = order
        print("\n".join([str(i) for i in order]))

    def add_require(self, key: str, task: Task):
        self.add_task(task)
        self.tasks[key].task.requires.append(task.name)

    def add_task(self, task: Task):
        self.tasks[task.name] = (TC(task, Colors.white))

    def save(self):
        with open(self.mock_name, "w") as file:
            file.writelines(json.dumps(self.mock))

    def execute(self, key: str):
        self.sort(key)
        self.view()
        for task in self.order:
            pass
