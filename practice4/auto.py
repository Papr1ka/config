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
    color: Colors
    type: Tasks
    requires: List[str]
    name: str
    commands: List[str]

    def __init__(self, t_type: Tasks, name: str = "", requires=None, commands=None):
        self.color = Colors.white
        self.type = t_type
        self.requires = [] if requires is None else requires
        self.name = name
        self.commands = [] if commands is None else commands

    def __str__(self):
        return self.name if self.name != "" else "Undefined"

    def __repr__(self):
        return self.__str__()


class Auto:
    stack: Stack
    targets: Dict[str, Task]
    mock_name = "auto.mock.json"
    mock: dict
    order: List[Task]

    def __init__(self):
        self.targets = {}
        self.stack = Stack()
        if path.exists(self.mock_name):
            with open(self.mock_name) as file:
                self.mock = json.loads("".join(file.readlines()))
        else:
            with open(self.mock_name, "w") as file:
                file.writelines(json.dumps({}))
            self.mock = {}

    def sort_task(self, key: str):
        task = self.targets[key]
        self.compile(key)
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

    def compile(self, task: str):
        task_object = self.targets.get(task)
        if task_object is None:
            if task.find(".") != -1:
                new_hash = self.get_file_hash(task)
                old_hash = self.mock.get(task)
                if not (new_hash == old_hash and new_hash is not None):
                    self.mock[task] = new_hash
                    return True
                return False
            else:
                raise KeyError(f"Задача {task} не определена")

        if task_object.color == Colors.black:
            return False

        is_actual = True
        for i in task_object.requires:
            r = self.compile(i)
            if r is True:
                is_actual = False

        if is_actual is False:
            self.stack.push(task_object)
            return True
        elif is_actual is True and task_object.type == Tasks.file:
            return False


        task_object.color = Colors.gray

        if task_object.type == Tasks.file:
            try:
                new_hash = self.get_file_hash(task_object.name)
            except FileNotFoundError:
                new_hash = None
            old_hash = self.mock.get(task_object.name)
            if new_hash == old_hash and new_hash is not None:
                task_object.color = Colors.black
                return False
            else:
                if new_hash is not None:
                    self.mock[task_object.name] = new_hash
                self.stack.push(task_object)
                return True
        else:
            self.stack.push(task_object)
            return True

    def handle(self, task: Task):
        if task.color == Colors.black:
            return

        task.color = Colors.gray

        is_actual = True

        for req in task.requires:
            req: str
            state = 0
            try:
                req_task = self.targets[req]
            except KeyError:
                state = 1

            if state == 0:
                if req_task.type == Tasks.file:
                    try:
                        new_hash = self.get_file_hash(req_task.name)
                    except FileNotFoundError:
                        new_hash = None
                    old_hash = self.mock.get(req_task.name)
                    if new_hash == old_hash and new_hash is not None:
                        req_task.color = Colors.black
                    else:
                        self.mock[task.name] = new_hash
                        is_actual = False
                        self.handle(req_task)
                else:
                    self.handle(req_task)
            else:
                if req.find(".") != -1:
                    new_hash = self.get_file_hash(req)
                    old_hash = self.mock.get(req)
                    if not (new_hash == old_hash and new_hash is not None):
                        is_actual = False
                        self.mock[task.name] = new_hash
                else:
                    raise KeyError("Задача не определена")

        task.color = Colors.black
        if not is_actual:
            self.stack.push(task)

    def view(self):
        order = []
        while len(self.stack):
            order.append(self.stack.pop())
        order = list(reversed(order))
        self.order = order
        print("\n".join([str(i) for i in order]))

    def create_task(self, task: Task):
        self.targets[task.name] = task

    def save(self):
        with open(self.mock_name, "w") as file:
            file.writelines(json.dumps(self.mock))

    def execute(self, key: str):
        self.sort_task(key)
        self.view()
        for task in self.order:
            pass
