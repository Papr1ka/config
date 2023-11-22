import ast
import inspect
from enum import Enum
from typing import List

from auto.auto import Auto as Manager, Task, AutoGraph as ViewManager

def get_error_details(src, node, filename=''):
    """
    Подсвечивает синтаксичексую ошибку
    """
    return (filename,
            node.lineno,
            node.col_offset + 1,
            ast.get_source_segment(src, node),
            node.end_lineno,
            node.end_col_offset + 1)


class States(Enum):
    Target = 0  # Цель
    Scripts = 1  # Список команд


class Parser:
    """
    Парсит исходный код функции, написанный на языке Auto
    """
    source: str  # Исходный код
    builder: Manager  # Класс Менеджер задач
    state: States  # Текущий блок

    def __init__(self, source: str, builder: Manager):
        self.source = source
        self.builder = builder
        self.state = States.Target

    def parse_target_name(self, node) -> str:
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            raise SyntaxError("Ожидалась цель (строка)", get_error_details(self.source, node))
        return node.value

    def parse_lte(self, node):
        if len(node) != 1:
            raise SyntaxError("Список зависимостей должен один (оператор)", get_error_details(self.source, node))
        if not isinstance(node[0], ast.LtE):
            raise SyntaxError("Ожидалось '<='", get_error_details(self.source, node[0]))

    def parse_tuple(self, node) -> List[str]:
        if len(node) != 1:
            raise SyntaxError("Список зависимостей должен один (операнды)",
                              get_error_details(self.source, node))
        if not isinstance(node[0], ast.Tuple) and (
                not isinstance(node[0], ast.Constant) or not isinstance(node[0].value, str)):
            raise SyntaxError("Список зависимостей должен быть кортежем из строк или строкой",
                              get_error_details(self.source, node.comparators[0]))

        requirements = []

        if isinstance(node[0], ast.Constant):
            requirements = [node[0].value]
        else:
            for i in node[0].elts:
                if not isinstance(i, ast.Constant) or not isinstance(i.value, str):
                    raise SyntaxError("Зависимость должна быть строкой",
                                      get_error_details(self.source, i))
                requirements.append(i.value)
        return requirements

    def parse_target(self, node):
        if isinstance(node, ast.Compare):
            name = self.parse_target_name(node.left)
            self.parse_lte(node.ops)
            requirements = self.parse_tuple(node.comparators)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            name = node.value
            requirements = []
        else:
            raise SyntaxError("Цель должна быть либо строкой, либо строкой с зависимостями")

        return name, requirements

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

        task = Task(name, requirements, scripts)
        self.builder.create_task(task)


def configure(**kwargs):
    """
    :keyword print_tasks: bool, если True, будет выводиться порядок выполнения задач
    :keyword mock_name: str, имя файла json для хранения хэш-значений файлов
    :return: возвращает декоратор, функция возвращает объект Auto, готорый к использованию

    Примеры использования:
    ~~~~
    * внутри программы:
    ::

        @configure(**kwargs)
        def config():
            run <= ()
            ['echo "Побежал, но после вызова функции"']

        manager = config()
        manager.execute("run")

    * из командной строки:
    ::

        @cli
        @configure(**kwargs)
        def config():
            run <= ()
            ['echo "Побежал, если вызвали из командной строки"']

    *python source.py run*
    """
    def wrapper(func):
        def inner(view=False) -> Manager:
            if view is True:
                builder = ViewManager(**kwargs)
            else:
                builder = Manager(**kwargs)
            src = inspect.getsource(func)
            cls = Parser(src, builder)
            tree = ast.parse(src)

            body = tree.body[0].body

            i = iter(body)
            if len(body) % 2 == 1:
                raise SyntaxError("После цели ожидался скрипт", get_error_details(src, tree.body[0].body[-1]))

            for node in i:
                node2 = next(i)
                cls.create_target([node, node2])

            return builder
        return inner

    return wrapper
