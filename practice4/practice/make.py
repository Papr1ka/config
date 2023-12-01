import os.path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import auto


# noinspection PyStatementEffect
@auto.cli
#auto.view
@auto.configure(print_tasks=True)
def config():
    "run" <= "main"
    [
        "chmod +x ./main",
        "./main"
    ]

    "main" <= ("HashBinary.o", "HashTable.o", "BinaryUtils.o", "main.o")
    [
        "g++ -o main main.o HashTable.o BinaryUtils.o HashBinary.o",
    ]

    "HashBinary.o" <= ("HashBinary.cpp")
    [
        "g++ -c HashBinary.cpp"
    ]

    "HashTable.o" <= ("HashTable.cpp")
    [
        "g++ -c HashTable.cpp"
    ]

    "BinaryUtils.o" <= ("BinaryUtils.cpp")
    [
        "g++ -c BinaryUtils.cpp"
    ]

    "main.o" <= ("main.cpp")
    [
        "g++ -c main.cpp"
    ]

    "clean"
    [
        "rm -r *.o",
        "rm ./main"
    ]
