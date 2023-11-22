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
    def wrapper(*args, **kwargs):
        manager: AutoGraph = function(*args, **kwargs, view=True)
        manager.view()
        return manager
    return wrapper


