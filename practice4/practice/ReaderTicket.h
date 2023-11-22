//
// Created by joe on 19.10.23.
//

#ifndef SIAOD3_READERTICKET_H
#define SIAOD3_READERTICKET_H

#include <iostream>
#include <cstring>

using namespace std;

struct ReaderTicket
{
    int key; //ключ
    char fio[30];
    char phoneNumber[15];

    void print() const
    {
        cout << "Читательский билет: " << endl;
        cout << "Номер билета: " << this->key << endl;
        cout << "Фио: " << this->fio << endl;
        cout << "Номер телефона: " << this->phoneNumber << endl;
    }

    ReaderTicket() {}

    ReaderTicket(const ReaderTicket& other)
    {
        this->key = other.key;
        memcpy(this->fio, other.fio,  30);
        memcpy(this->phoneNumber, other.phoneNumber, 15);
    }
};

typedef struct ReaderTicket Ticket;

#endif //SIAOD3_READERTICKET_H
