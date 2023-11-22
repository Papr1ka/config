from .auto import Auto
import gettext


def russian(text):
    text = text.replace("usage:",
                        "использование:")
    text = text.replace("show this help message and exit",
                        "показывает это сообщение и выходит")
    text = text.replace("error:",
                        "ошибка:")
    text = text.replace("the following arguments are required",
                        "требуются следующие аргументы")
    text = text.replace("argument ",
                        "аргумент ")
    text = text.replace("invalid choice",
                        "недопустимый вариант")
    text = text.replace("choose from ",
                        "выберите из следующих ")
    return text


gettext.gettext = russian
import argparse

gettext.bindtextdomain("argparse", "")
gettext.textdomain("argparse")

DESCRIPTION = """Система сборки Auto"""


def cli(function):
    """
    Декоратор, создаёт командную утилиту из функции

    :param function: - результат работы декоратора configure

    Использование:
    ~~~~~~~~
    ::

        @cli
        @configure(**kwargs)
        def test():
            ...

    Все цели будут доступны для исполнения

    *python source.py -h*
    """
    manager: Auto = function()
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser._positionals.title = "Позиционные аргументы"
    parser._optionals.title = "Опции"
    choices = manager.targets.keys()
    parser.add_argument("target", type=str, help="цель сборки", choices=choices)
    namespace = parser.parse_args()

    manager.execute(namespace.target)
