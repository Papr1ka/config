//
// Created by joe on 20.10.23.
//

#ifndef SIAOD3_HASHTABLE_H
#define SIAOD3_HASHTABLE_H

#include <cmath>
#include <iomanip>
#include <iostream>

using namespace std;

#define DEBUG

#ifdef DEBUG
#include <vector>
#endif

#define A 0.6180339887498948482045868343656381177203091798057628621354486227

template<typename T>
class HashTable;

template<typename T>
class TableItem {
private:
    int key;
    T value;
    char flags;
public:

#ifdef DEBUG
    vector<int> debugPrimaryIndexes;
#endif

    enum Flags {
        opened = 1,
        deleted = 2,
    };

    TableItem()
    {
        this->flags = Flags::opened;
    }

    TableItem(int key, T value)
    {
        this->key = key;
        this->value = value;
        this->flags = 0;
    }

    bool isOpened()
    {
        return this->flags & Flags::opened;
    }


    bool isDeleted()
    {
        return this->flags & Flags::deleted;
    }

    void remove()
    {
        this->flags = Flags::opened | Flags::deleted;
    }

    int getKey(bool &success)
    {
        if (!isOpened())
        {
            success = true;
            return this->key;
        }
        success = false;
        return 0;
    }

    void getValue(bool &success, T& toWrite)
    {
        if (!isOpened() || isDeleted())
        {
            success = true;
            toWrite = this->value;
        }
        else
        {
            success = false;
        }
    }

    void setValue(T newValue)
    {
        this->value = newValue;
        this->flags = 0;
    }


    void clearDeleted()
    {
        this->flags = 0;
    }

#ifdef DEBUG
    void print()
    {
        bool success;
        int keyValue = this->getKey(success);
        cout << std::setw(12);
        if (this->isDeleted())
        {
            cout << this->key;
        }
        else if (!success)
        {
            cout << "~";
        }
        else
        {
            cout << keyValue;
        }
        cout << setw(3) << this->isOpened() << setw(3) << this->isDeleted();
        for (int i = 0; i < this->debugPrimaryIndexes.size(); i++)
        {
            cout << setw(3) << this->debugPrimaryIndexes[i];
        }
        cout << endl;
    }

    friend void testHeshT();
    friend void test();
#endif
};

template<typename T>
class HashTable
{
private:
    int m;
    int n;
    int deleted;
    TableItem<T>* items;

    int getKeyHash(int key)
    {
        double b = key * A;
        double c = fmod(b, 1);
        c *= this->m;
        int index = floor(c);
        return index;
    }

    int getBiasHash(int key)
    {
        int r = ((2 * key + 1) % m);
        return (r > 0 ? r : -r);
    }

    //возвращает индекс элемента в массиве таблицы
    int findItem(int key, bool& success)
    {
        int index = this->getKeyHash(key);
        int bias = this->getBiasHash(key);
        TableItem<T> tmp = this->items[index];
        bool unused;
        while ((!tmp.isOpened() || tmp.isDeleted()) && tmp.getKey(unused) != key)
        {
            index = (index + bias) % this->m;
            tmp = this->items[index];
        }
        if (tmp.isOpened())
        {
            success = false;
            return 0;
        }
        success = true;
        return index;
    }

    //возвращает индекс элемента в массиве таблицы
    int popItem(int key, bool& success)
    {
        int index = this->findItem(key, success);
        if (!success)
        {
            return 0;
        }
        this->items[index].remove();
        this->deleted++;
        this->n--;
        return index;
    }

public:
    HashTable()
    {
        this->m = 16;
        this->n = 0;
        this->deleted = 0;
        this->items = new TableItem<T>[16];
        for (int i = 0; i < 16; ++i)
        {
            this->items[i] = TableItem<T>();
        }
    }

    //size - степень числа 2
    HashTable(unsigned int size)
    {
        this->m = 1 << size;
        if (this->m <= 2)
        {
            this->m = 4;
        }
        this->n = 0;
        this->deleted = 0;
        this->items = new TableItem<T>[this->m];
        for (int i = 0; i < this->m; ++i)
        {
            this->items[i] = TableItem<T>();
        }
    }

    ~HashTable()
    {
        delete[] this->items;
    }

    //возвращает текущий размер таблицы
    int getSize()
    {
        return this->m;
    }

    //возвращает количество занятых и неудалённых ячеек
    int getFilled()
    {
        return this->n;
    }

    //возвращает количество удалённых ячеек
    int getDeleted()
    {
        return this->deleted;
    }

    //возвращает отношение количества занятых к размеру таблицы в процентах (0-100)
    int getFilledPercent()
    {
        return (this->n + this->deleted) * 100 / this->m;
    }

    bool needRehash()
    {
        if (((this->n + this->deleted) * 100 / this->m) > 75)
        {
            return true;
        }
        return false;
    }


    void reHash()
    {
        int oldSize = this->m;
        this->m *= 2;
        this->deleted = 0;
        this->n = 0;
        TableItem<T>* oldItems = this->items;
        this->items = new TableItem<T>[this->m];
        bool unused;

        for (int i = 0; i < oldSize; i++)
        {
            TableItem<T> buffer = oldItems[i];
            if (!buffer.isOpened())
            {
                buffer.clearDeleted();
                T val;
                buffer.getValue(unused, val);
                this->insert(buffer.getKey(unused), val, unused);
            }
        }

        delete[] oldItems;
    }

    void insert(int key, T value, bool& success)
    {
        bool unused;
        TableItem<T> item(key, value);
        int index = this->getKeyHash(item.getKey(unused));
#ifdef DEBUG
        item.debugPrimaryIndexes.push_back(index);
#endif
        int bias = this->getBiasHash(item.getKey(unused));
        TableItem buffer = this->items[index];
        while (!(buffer.isOpened()))
        {
            //Проверка на вставку элемента с дублированием ключа
            if (buffer.getKey(unused) == key && !buffer.isDeleted())
            {
                success = false;
                return;
            }
            index = (index + bias) % this->m;
#ifdef DEBUG
            item.debugPrimaryIndexes.push_back(index);
#endif
            buffer = this->items[index];
        }
        this->items[index] = item;
        this->n++;
        if (buffer.isDeleted())
        {
            this->deleted--;
        }

        if (this->needRehash())
        {
            this->reHash();
        }
        success = true;
    }

    void get(int key, bool& success, T& toWrite)
    {
        int index = this->findItem(key, success);
        if (success)
        {
            this->items[index].getValue(success, toWrite);
        };
    }

    void update(int key, T value, bool& success)
    {
        int index = this->findItem(key, success);
        if (success)
        {
            this->items[index].setValue(value);
        }
    }

    void update(int key, T value)
    {
        bool success;
        int index = this->findItem(key, success);
        if (success)
        {
            this->items[index].setValue(value);
        }
    }

    void pop(int key, bool& success, T& toWrite)
    {
        int index = this->popItem(key, success);
        if (success)
        {
            this->items[index].getValue(success, toWrite);
        }
    }

    void pop(int key)
    {
        bool success;
        this->popItem(key, success);
    }

#ifdef DEBUG
    friend void testHeshT();
    friend void test();
    friend int main();
#endif
};

#ifdef DEBUG
void testHeshT();
#endif

#endif //SIAOD3_HASHTABLE_H
