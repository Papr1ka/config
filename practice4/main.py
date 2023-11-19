from auto import *

target = Auto()

target.add_task(Script(["g++ -c main.cpp"],["practice3/main.cpp"], name="main"))
target.add_task(File("practice3/main.cpp"))
target.add_task(Script(["g++ -c BinaryUtils.cpp"], ["practice3/BinaryUtils.cpp"], name="binaryutils"))
target.add_task(File("practice3/BinaryUtils.cpp"))
target.add_task(Script(["g++ -c HashTable.cpp"], ["practice3/HashTable.cpp"], name="hashtable"))
target.add_task(File("practice3/HashTable.cpp"))
target.add_task(Script(["g++ -c HashBinary.cpp"], ["practice3/HashBinary.cpp"], name="hashbinary"))
target.add_task(File("practice3/HashBinary.cpp"))
target.add_task(Script(["g++ -o main main.o HashTable.o BinaryUtils.o HashBinary.o"], ["hashbinary", "hashtable", "binaryutils", "main"], name="run"))
target.add_task(Script(["rm -r *.o"], name="clean"))

target.add_task(File("test.bin"))

target.sort("run")
target.view()
