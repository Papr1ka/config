//
// Created by joe on 19.10.23.
//

#ifndef SIAOD3_HASHBINARY_H
#define SIAOD3_HASHBINARY_H

#include "BinaryUtils.h"
#include "HashTable.h"
#include "ReaderTicket.h"

//Поиск записи в файле по ключу, записывает номер записи в хэш таблицу
int searchInsert(const string& filename, int key, HashTable<int>* table, Ticket*& toWrite);

//удаляет запись
int deleteRemove(const string& filename, int key, HashTable<int>* table);

//получение записи из файла по ключу с использованием хэш таблицы, если в хэш таблице значение не найдено, вызывается searchInsert
int readGet(const string& filename, int key,  HashTable<int>* table, Ticket*& toWrite);

void test();

#endif //SIAOD3_HASHBINARY_H
