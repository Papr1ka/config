Программа реализует:

- Task

Task:
    имеет список подзадач
    имеет список команд для выполнения
    имеет служебную информацию

Пример:
Task0:
    mkdir "build"
    cd "build"

Task2 Task0:
    cat "print('Hello world') > hello.py"

Task1: Task0 Task2:
    python "build/hello.py"

Граф:
        Task0
Task1
        Task2
                Task0

После топологической:
    Task0 Task2 Task1

API

объект Make

a = Make.Task(..., require=Task0[])




