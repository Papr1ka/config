//
// Created by joe on 20.10.23.
//

#include "HashTable.h"
#include "DebugTools.h"


#ifdef DEBUG
void testHeshT()
{

    HashTable<int>* table = new HashTable<int>(2);
    bool success;

    LINE()
    cout << "Проверка формирования хешей для ключей..." << endl;
    cout << "key | index | bias" << endl;

    int key = 111001;
    cout << key << " | " << table->getKeyHash(key) << " | " << table->getBiasHash(key) << endl;
    key = 112001;
    cout << key << " | " << table->getKeyHash(key) << " | " << table->getBiasHash(key) << endl;
    key = 212001;
    cout << key << " | " << table->getKeyHash(key) << " | " << table->getBiasHash(key) << endl;
    key = 303002;
    cout << key << " | " << table->getKeyHash(key) << " | " << table->getBiasHash(key) << endl;
    key = 304002;
    cout << key << " | " << table->getKeyHash(key) << " | " << table->getBiasHash(key) << endl;
    key = 111007;
    cout << key << " | " << table->getKeyHash(key) << " | " << table->getBiasHash(key) << endl;
    key = 305002;
    cout << key << " | " << table->getKeyHash(key) << " | " << table->getBiasHash(key) << endl;
    key = 111001;
    cout << key << " | " << table->getKeyHash(key) << " | " << table->getBiasHash(key) << endl;
    key = 303010;
    cout << key << " | " << table->getKeyHash(key) << " | " << table->getBiasHash(key) << endl;

    int buff;
    bool testSuccess;
    cout << "Исходная таблица" << endl;
    PRINTTABLE()

    LINE()
    cout << "Тестирование вставки" << endl;
    int test;
    test = 111001;
    cout << "Вставка без коллизии " << test << endl;
    table->insert(test, 1, success);
    PRINTTABLE()
    table->get(test, testSuccess, buff);
    TESTCODEREVERSECONDITION(success, (buff == 1))

    LINE()
    cout << "Вставка дубликата" << endl;
    test = 111001;
    table->insert(test, 2, success);
    PRINTTABLE()
    table->get(test, testSuccess, buff);
    TESTCODECONDITION(success, (buff == 1))

    LINE()
    test = 112001;
    cout << "Вставка с коллизией " << test << endl;
    table->insert(test, 3, success);
    PRINTTABLE()
    table->get(test, testSuccess, buff);
    TESTCODEREVERSECONDITION(success, (buff == 3))

    LINE()
    test = 212001;
    cout << "Вставка с рехэшированием " << test << " и " << " 303002" << endl;
    table->insert(test, 4, success);
    test = 303002;
    table->insert(test, 5, success);
    PRINTTABLE()


    int buff1;
    int buff2;
    int buff3;
    int buff4;
    table->get(111001, testSuccess, buff1);
    table->get(112001, testSuccess, buff2);
    table->get(212001, testSuccess, buff3);
    table->get(303002, testSuccess, buff4);

    TESTCODEREVERSECONDITION(success, (
                    (buff1 == 1) &&
                    (buff2 == 3) &&
                    (buff3 == 4) &&
                    (buff4 == 5) &&
                    (table->getSize() == 8) &&
                    (table->getFilled() == 4))
    )

    LINE()
    test = 111001;
    cout << "Удаление ключа " << test << " из таблицы" << endl;
    int q;
    table->pop(test, success, q);
    if (success)
    {
        cout << "Ключ удалён, значение: " << q << endl;
    }
    else
    {
        cout << "Ошибка, ключ не найден" << endl;
    }
    PRINTTABLE()
    bool temp;
    table->get(test, temp, buff);
    TESTCODEREVERSECONDITION(success, ((!temp) && (table->getDeleted() == 1) && table->getFilled() == 3))

    test = 111001;
    cout << "Вставка нового элемента с значением ключа, идентичному удалённому " << test << endl;
    table->insert(test, -3, success);
    PRINTTABLE()
    table->get(test, testSuccess, buff);
    TESTCODEREVERSECONDITION(success, (buff == -3))

    LINE()
    test = 111001;
    cout << "Поиск ключа, у которого есть свежее значение, но было удалённое " << test << " в таблице" << endl;
    int value;
    table->get(test, success, value);
    if (success)
    {
        cout << "Найден элемент " << test << " значение: " << value << endl;
    }
    else
    {
        cout << "Ошибка, элемент не найден" << endl;
    }
    PRINTTABLE()
    TESTCODEREVERSECONDITION(success, (value == -3))

    LINE()
    test = 112001;
    cout << "Поиск ключа " << test << " в таблице" << endl;
    table->get(test, success, value);
    if (success)
    {
        cout << "Найден элемент " << test << " значение: " << value << endl;
    }
    else
    {
        cout << "Ошибка, элемент не найден" << endl;
    }
    PRINTTABLE()
    TESTCODEREVERSECONDITION(success, (value == 3))
    delete table;

    LINE()
    cout << "Поиск элемента, размещённого после удалённого с одним значением хэша ключей элементов" << endl;
    table = new HashTable<int>(2);
    table->insert(111001, 6, success);
    table->insert(112001, 7, success);
    table->insert(303010, 8, success);
    table->pop(111001);
    PRINTTABLE()
    table->get(303010, success, value);

    if (success)
    {
        cout << "Найден элемент " << 303010 << " значение " << value << endl;
    }
    else
    {
        cout << "Ошибка, элемент не найден" << endl;
    }
    TESTCODEREVERSECONDITION(success, (value == 8))

    LINE()
    cout << "Проверка замены значения элемента, метод udpate" << endl;
    key = 112001;
    table->get(key, testSuccess, buff);
    cout << "Ключ " << key << " значение " << buff << endl;
    int newValue = 58;
    cout << "Изменение значения на " << newValue << endl;
    table->update(key, newValue, success);

    if (success)
    {
        cout << "Значение изменено" << endl;
    }
    else
    {
        cout << "Ошибка, не вышло" << endl;
    }
    table->get(key, testSuccess, buff);
    cout << "Ключ " << key << " значение " << buff << endl;
    TESTCODEREVERSECONDITION(success, (buff == newValue))
    cout << "Тестирование модуля для работы с хэш таблицей завершено" << endl;
}
#endif
