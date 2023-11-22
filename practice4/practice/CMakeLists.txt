cmake_minimum_required(VERSION 3.26)
project(siaod3)

set(CMAKE_CXX_STANDARD 20)

add_executable(siaod3 main.cpp
        BinaryUtils.h
        BinaryUtils.cpp
        HashBinary.h
        HashBinary.cpp
        DebugTools.h
        ReaderTicket.h
        HashTable.cpp
        HashTable.h)
