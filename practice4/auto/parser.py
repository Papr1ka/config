import ast
import inspect
from functools import partial
from typing import List, Union

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
            tree = ast.parse(src)
            if len(tree.body) == 0:
                raise SyntaxError("Пустая программа", tree.body)

            a = AutoVisitor(src, builder)
            a.visit(tree.body[0])
            a.check_tasks()

            return builder

        return inner

    return wrapper


def checkFunction(src, constants: Union[ast.Tuple, ast.Constant], manager: Manager):
    if isinstance(constants, ast.Constant):
        r = manager.check(constants.value)
        if r is False:
            raise SyntaxError("Цель не определена", get_error_details(src, constants))
    else:
        for i in constants.elts:
            r = manager.check(i.value)
            if r is False:
                raise SyntaxError("Цель не определена", get_error_details(src, i))


class BaseVisitor:
    """
    Базовый визитор
    """
    state: int  # состояние, 0 - цель, 1 - скрипты
    src: str  # исходный код
    builder: Manager  # объект класса системы сборки
    checks: partial

    def __init__(self, src, builder):
        self.state = 0
        self.src = src
        self.builder = builder

    def visit(self, tree):
        method = 'visit_' + type(tree).__name__
        q = getattr(self, method)
        return getattr(self, method)(tree)

    def check(self, tree, tp, msg):
        if not isinstance(tree, tp):
            raise SyntaxError(f"Синтаксическая ошибка, ожидалось {msg}", get_error_details(self.src, tree))


class AutoVisitor(BaseVisitor):
    """
    Парсит исходный код функции, написанный на языке Auto
    """
    checks = []

    def visit_FunctionDef(self, tree):
        name = ""
        requirements = []
        scripts = []

        for i in tree.body:
            self.check(i, ast.Expr, "Выражение")
            if self.state == 0:
                name, requirements = self.visit(i)
            else:
                scripts = self.visit(i)
            self.state = (self.state + 1) % 2
            if self.state == 0:
                task = Task(name, requirements, scripts)
                self.builder.create_task(task)
        if self.state == 1:
            raise SyntaxError("После цели ожидался скрипт", get_error_details(self.src, tree.body[-1]))

    def visit_Expr(self, tree):
        node = tree.value
        if self.state == 0:
            if isinstance(node, ast.Compare):
                self.check(node.left, ast.Constant, "Строка")
                name = self.visit(node.left)
                if len(node.ops) != 1:
                    raise SyntaxError("Ожидался '<=' (1 оператор)", get_error_details(self.src, node.ops[0]))
                self.check(node.ops[0], ast.LtE, "Строка")
                self.visit(node.ops[0])
                if len(node.comparators) > 1:
                    raise SyntaxError("Ожидался кортеж или строка", get_error_details(self.src, node.comparators[0]))
                if not isinstance(node.comparators[0], ast.Tuple) and not isinstance(node.comparators[0], ast.Constant):
                    raise SyntaxError("Ожидалась строка или кортеж", get_error_details(self.src, node.comparators[0]))
                requirements = self.visit(node.comparators[0])
                if isinstance(requirements, str):
                    requirements = [requirements]
                self.checks.append(partial(checkFunction, self.src, node.comparators[0], self.builder))
            elif isinstance(node, ast.Constant):
                name = self.visit(node)
                requirements = []
            else:
                raise SyntaxError("Ожидалась цель (строка)", get_error_details(self.src, node))
            return name, requirements
        else:
            self.check(node, ast.List, "Массив строк")
            return self.visit(node)

    def visit_LtE(self, tree):
        pass

    def visit_Constant(self, tree):
        if isinstance(tree.value, str):
            return tree.value
        raise SyntaxError("Ожидалась строка", get_error_details(self.src, tree))

    def visit_Tuple(self, tree):
        scripts = []
        for i in tree.elts:
            self.check(i, ast.Constant, "Строка")
            scripts.append(self.visit(i))
        return scripts

    def visit_List(self, tree):
        scripts = []
        for i in tree.elts:
            self.check(i, ast.Constant, "Строка")
            scripts.append(self.visit(i))
        return scripts

    def check_tasks(self):
        for i in self.checks:
            i()
