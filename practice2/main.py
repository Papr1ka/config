import asyncio
import aiohttp
import graphviz
import re
from typing import List, Tuple, Union
from time import time

from progress.spinner import Spinner

dependencies_url_pattern = "https://pypi.python.org/pypi/{}/json"  # Адрес для получения информации о пакете

handled = []  # Список пакетов, для которых уже были получены зависимости (для избежания зацикливания)
ONLY_PACKAGE_NAME_PATTERN = r"[\w\._-]+"  # Регулярное выражение для поиска имени пакета (используется 1-е совпадение)

message = "Поиск зависимостей для {:<30} {} с "

def filter_package_name(dirty_dependencies: List[str]):
    """
    Фильтрует зависимости вида 'attrs['...'] extra="..."', а также "attrs(>=<===)..."
    На выходе получаем массив из названий пакетов (attrs)
    """
    clean_dependencies = []
    for dep in dirty_dependencies:
        dep_clean = re.match(ONLY_PACKAGE_NAME_PATTERN, dep)
        if dep_clean is None:
            continue

        if dep.find("extra") == -1:
            dep_clean = dep_clean.group()
            clean_dependencies.append(dep_clean)
    return clean_dependencies


def dependencies_visualizer(g):
    """
    Генератор, который строит нам граф
    """
    lib_name = yield
    g.node(lib_name, style="filled", color="grey")
    while True:
        dep = yield
        if dep is None:
            return
        else:
            g.node(dep[1])
            g.edge(*dep)


async def get_dependencies(lib_name) -> Union[None, Tuple[str, List[str]]]:
    """
    Метод, задача которого заключается в том, чтобы вернуть список зависимостей для определённого имени пакета
    И в случае, если пакет не найден, выбросить исключение
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(dependencies_url_pattern.format(lib_name)) as resp:
            json = await resp.json()
            info = json.get("info")
            if info is not None:
                deps = info.get("requires_dist")
                return lib_name, deps
            elif resp.status == 404 and lib_name == LIB_NAME:
                raise KeyError(f"Пакет {lib_name} не найден")
            elif resp.status == 404:
                print(f"Пакет {lib_name} не найден")


async def get_deps_async(deps_list, graph_generator):
    """
    Асинхронный рекурсивный метод, принимает список зависимостей и генератор графа
    Получает подзависимости для каждой из зависимости и создаёт новую рекурсивную задачу по разрешению
    зависимости уже для каждой из подзависимостей по мере их получения

    База рекурсии: Все запросы выполнены и осталась только 1 асинхронная задача - текущая
    """
    tasks = [asyncio.create_task(get_dependencies(deps_list[i])) for i in range(len(deps_list))]
    for coro in asyncio.as_completed(tasks):
        new_deps = await coro
        if new_deps is not None and new_deps[1] is not None:
            lib_name, new_deps = new_deps
            deps_clean = filter_package_name(new_deps)
            deps_new = []
            for i in deps_clean:
                graph_generator.send((lib_name, i))
                if i not in handled:
                    deps_new.append(i)
                    handled.append(i)

            if deps_new:
                s.message = message.format(deps_new[-1], round(time() - begin, 2))
                s.next()
            # Можно замедлить программу в 3-5 раз, если добавить к.с. await в след. строке
            asyncio.get_running_loop().create_task(get_deps_async(deps_new, graph_generator))
    if len(asyncio.all_tasks()) == 1:
        asyncio.get_running_loop().stop()
        s.message = "Stopping loop"
        s.next()


def start(lib_name):
    """
    Стартовая функция, создаёт граф, запускает задачу по нахождению зависимостей и показывает граф
    """
    g = graphviz.Digraph("Dependencies", filename="test.gv", engine='dot', node_attr={"style": "filled", "color": "lightblue"})
    g.attr(ranksep="3")  # Расстояние между линиями в графе
    graph = dependencies_visualizer(g)
    graph.send(None)
    graph.send(LIB_NAME)

    loop = asyncio.get_event_loop()
    loop.create_task(get_deps_async([lib_name], graph))

    try:
        loop.run_forever()
    except KeyError:
        print("Библиотека не найдена")
    s.message = "Вывод графа "
    s.next()
    g.view()


if __name__ == "__main__":
    print("Введите название пакета:")
    LIB_NAME = input()  # Название пакета
    s = Spinner(message.format(LIB_NAME, 0))
    begin = time()
    start(LIB_NAME)
    s.message = f"Готово за {time() - begin} ms "
    s.next()
    print()
