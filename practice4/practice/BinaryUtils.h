//
// Created by joe on 19.10.23.
//

#ifndef SIAOD3_BINARYUTILS_H
#define SIAOD3_BINARYUTILS_H

#pragma once

#include <string>
#include <fstream>
#include "DebugTools.h"
#include "ReaderTicket.h"

#define CHECK(filestream, error_code) \
{                      \
    if (!filestream.good()) \
    {                     \
        return error_code;                      \
    }\
};


#define ENDSTREAM(fstream) \
{                       \
    fstream.close(); \
    return fstream.bad(); \
};

using namespace std;
 
//конвертация из текстового формата в двоичный
int convertTextToBin(const string& filename1, const string& filename2);

//добавление записи в конец файла
int addRecordToBin(const string& filename, const Ticket* record);

//удаление записи по порядковому номеру
int deleteRecordFromBinByNumber(const string& filename, int number);

//получение записи по порядковому номеру
int getRecordFromBin(const string& filename, int number, Ticket*& toWrite);

//поиск записи в двоичном файле по ключу
int searchRecordFromBin(const string& filename, int key, Ticket*& toWrite, int& number);

//вывод файла
int printFromBin(const string& filename1);

//тестирование модуля
void testBinF(const string& filename);

#endif //SIAOD3_BINARYUTILS_H
