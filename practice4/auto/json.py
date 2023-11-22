from .parser import *


def json(**kwargs):
    """
    :keyword print_tasks: bool, если True, будет выводиться порядок выполнения задач
    :keyword mock_name: str, имя файла json для хранения хэш-значений файлов
    :return: возвращает декоратор, функция возвращает объект Auto, готорый к использованию

    Пример использования:
    ~~~~
    ::

        @view
        @json("test.json, "**kwargs)
        def config():
            with open("source.json") as file:
                return json.loads(file.read())
    """

    def wrapper(func):
        def inner(view=False, *f_args, **f_kwargs) -> Manager:
            if view is True:
                builder = ViewManager(**kwargs)
            else:
                builder = Manager(**kwargs)

            data = func(*f_args, **f_kwargs)

            for i in data.keys():
                builder.create_task(Task(i, requires=data[i], commands=[
                    f"echo {i} > {i}",
                    f"echo {i}"
                ]))

            return builder

        return inner

    return wrapper
