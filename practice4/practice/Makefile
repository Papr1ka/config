.PHONY: clean

main.o : main.cpp
	g++ -c main.cpp
binaryutils.o: BinaryUtils.cpp
	g++ -c BinaryUtils.cpp
hashtable.o: HashTable.cpp
	g++ -c HashTable.cpp
hashbinary.o: HashBinary.cpp
	g++ -c HashBinary.cpp
run: hashbinary.o hashtable.o binaryutils.o main.o
	g++ -o main main.o HashTable.o BinaryUtils.o HashBinary.o
	chmod +x ./main
	./main
clean:
	rm -r *.o

