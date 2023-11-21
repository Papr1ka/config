import ast
import inspect
from enum import Enum
from typing import List

from auto import Auto as Builder, Task, Tasks


def get_error_details(src, node, filename=''):
    return (filename,
            node.lineno,
            node.col_offset + 1,
            ast.get_source_segment(src, node),
            node.end_lineno,
            node.end_col_offset + 1)


class States(Enum):
    Target = 0
    Scripts = 1


class Auto:
    def __init__(self, source, builder):
        self.source = source
        self.builder: Builder = builder
        self.state = States.Target

    def parse_target(self, node):
        if not isinstance(node.left, ast.Constant) or not isinstance(node.left.value, str):
            raise SyntaxError("Ожидалась цель (строка)", get_error_details(self.source, node.left))

        if len(node.ops) != 1:
            raise SyntaxError("Список зависимостей должен один (оператор)", get_error_details(self.source, node.ops))
        if not isinstance(node.ops[0], ast.LtE):
            raise SyntaxError("Ожидалось '<='", get_error_details(self.source, node.ops[0]))

        if len(node.comparators) != 1:
            raise SyntaxError("Список зависимостей должен один (операнды)",
                              get_error_details(self.source, node.comparators))
        if not isinstance(node.comparators[0], ast.Tuple) and (
                not isinstance(node.comparators[0], ast.Constant) or not isinstance(node.comparators[0].value, str)):
            raise SyntaxError("Список зависимостей должен быть кортежем из строк или строкой",
                              get_error_details(self.source, node.comparators[0]))

        requirements = []

        if isinstance(node.comparators[0], ast.Constant):
            requirements = [node.comparators[0].value]
        else:
            for i in node.comparators[0].elts:
                if not isinstance(i, ast.Constant) or not isinstance(i.value, str):
                    raise SyntaxError("Зависимость должна быть строкой",
                                      get_error_details(self.source, i))
                requirements.append(i.value)

        return node.left.value, requirements

    def parse_scripts(self, node):
        scripts = []
        if not isinstance(node, ast.List):
            raise SyntaxError("Скрипты должны быть массивом", get_error_details(self.source, node))
        for i in node.elts:
            if not isinstance(i, ast.Constant) or not isinstance(i.value, str):
                raise SyntaxError("Зависимость должна быть строкой",
                                  get_error_details(self.source, i))
            scripts.append(i.value)
        return scripts

    def parse(self, node):
        if not isinstance(node, ast.Expr):
            raise SyntaxError("Ожидалась цель или скрипт", get_error_details(self.source, node))

        if self.state == States.Target:
            name, requirements = self.parse_target(node.value)
            self.state = States.Scripts
            return name, requirements
        else:
            scripts = self.parse_scripts(node.value)
            self.state = States.Target
            return scripts

    def create_target(self, nodes: List[ast.AST]):
        if len(nodes) < 2:
            raise SyntaxError("После цели ожидался скрипт", get_error_details(self.source, nodes[0]))
        name, requirements = self.parse(nodes[0])
        scripts = self.parse(nodes[1])

        t = Tasks.script

        if name.find(".") != -1:
            t = Tasks.file

        task = Task(t, name, requirements, scripts)
        self.builder.create_task(task)

def auto(func):
    def wrapper():
        builder = Builder()
        src = inspect.getsource(func)
        cls = Auto(src, builder)
        tree = ast.parse(src)

        i = iter(tree.body[0].body)

        for node in i:
            try:
                node2 = next(i)
            except StopIteration:
                cls.create_target([node])
            cls.create_target([node, node2])

        return builder
    return wrapper


# noinspection PyStatementEffect
@auto
def test():
    "run" <= ("HashBinary.o", "HashTable.o", "BinaryUtils.o", "main.o")
    [
        "g++ -o main practice3/main.o practice3/HashTable.o practice3/BinaryUtils.o practice3/HashBinary.o",
        "chmod +x ./main",
        "./main"
    ]

    "HashBinary.o" <= ("practice3/HashBinary.cpp")
    [
        "g++ -c practice3/HashBinary.cpp"
    ]

    "HashTable.o" <= ("practice3/HashTable.cpp")
    [
        "g++ -c practice3/HashTable.cpp"
    ]

    "BinaryUtils.o" <= ("practice3/BinaryUtils.cpp")
    [
        "g++ -c practice3/BinaryUtils.cpp"
    ]

    "main.o" <= ("practice3/main.cpp")
    [
        "g++ -c practice3/main.cpp"
    ]

    "test.o" <= ("main.o")
    [
        "..."
    ]

    "test" <= ("test.o")
    []

builder = test()
builder.execute("test")
