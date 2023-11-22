from .auto import AutoGraph


def view(function):
    """
    Декоратор, показывает граф зависимостей

    :param function: - результат работы декоратора configure

    Использование:
    ~~~~~~~~
    ::

        @view
        @configure(**kwargs)
        def test():
            ...
    """

    manager: AutoGraph = function(view=True)
    manager.view()


