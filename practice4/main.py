from auto import *

target = Auto()

target.create_task(Script(["g++ -c main.cpp"], ["practice3/main.cpp"], name="main"))
target.create_task(ScriptFile("practice3/main.cpp"))
target.create_task(Script(["g++ -c BinaryUtils.cpp"], ["practice3/BinaryUtils.cpp"], name="binaryutils"))
target.create_task(ScriptFile("practice3/BinaryUtils.cpp"))
target.create_task(Script(["g++ -c HashTable.cpp"], ["practice3/HashTable.cpp"], name="hashtable"))
target.create_task(ScriptFile("practice3/HashTable.cpp"))
target.create_task(Script(["g++ -c HashBinary.cpp"], ["practice3/HashBinary.cpp"], name="hashbinary"))
target.create_task(ScriptFile("practice3/HashBinary.cpp"))
target.create_task(Script(["g++ -o main main.o HashTable.o BinaryUtils.o HashBinary.o"],
                          ["hashbinary", "hashtable", "binaryutils", "main"], name="run"))
target.create_task(Script(["rm -r *.o"], name="clean"))

target.create_task(ScriptFile("test.bin"))

target.sort_task("run")
target.view()
