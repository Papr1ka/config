#include "BinaryUtils.h"
#include <filesystem>

int addRecordToBin(const string& filename, const Ticket* record)
{
    ofstream wNewStream;
    wNewStream.open(filename, (ios::ios_base::binary | ios::ios_base::app));
    CHECK(wNewStream, -1)

    wNewStream.write((char*)record, sizeof(Ticket));

    ENDSTREAM(wNewStream)
}


int convertTextToBin(const string& filename1, const string& filename2)
{
    ifstream rOldStream;
    ofstream wNewStream;
    rOldStream.open(filename1);
    wNewStream.open(filename2, ios::ios_base::binary);
    CHECK(rOldStream, -1)
    CHECK(wNewStream, -2)

    while (rOldStream.peek() != EOF)
    {
        Ticket buffer;
        rOldStream >> buffer.key;
        rOldStream >> buffer.fio;
        rOldStream >> buffer.phoneNumber;
        wNewStream.write((char*)&buffer, sizeof(Ticket));
        rOldStream.get();
    }

    rOldStream.close();
    wNewStream.close();
    return rOldStream.bad() || wNewStream.bad();
}

int printFromBin(const string& filename)
{
    ifstream rOldStream;
    rOldStream.open(filename, ios::ios_base::binary);
    CHECK(rOldStream, -1)

    Ticket buffer;

    while (rOldStream.peek() != EOF)
    {
        rOldStream.read((char*)&buffer, sizeof(buffer));
        buffer.print();
    }

    ENDSTREAM(rOldStream)
}

int getRecordFromBin(const string& filename, int number, Ticket*& toWrite)
{
    if (number < 0)
    {
        return -2;
    }

    ifstream rOldStream;
    rOldStream.open(filename, ios::ios_base::binary);
    CHECK(rOldStream, -1)


    rOldStream.seekg(0, std::ifstream::end);
    int fileLength = rOldStream.tellg();

    if ((number + 1) * sizeof(Ticket) > fileLength)
    {
        rOldStream.close();
        return -2;
    }

    rOldStream.seekg(0, std::ifstream::beg);
    rOldStream.seekg(number * sizeof(Ticket));
    Ticket buffer;
    rOldStream.read((char*)&buffer, sizeof(Ticket));
    toWrite = new Ticket(buffer);

    ENDSTREAM(rOldStream)
}

int searchRecordFromBin(const string& filename, int key, Ticket*& toWrite, int& number)
{
    ifstream rOldStream;
    rOldStream.open(filename, ios::ios_base::binary);
    CHECK(rOldStream, -1)

    Ticket buffer;
    int i = 0;

    while (rOldStream.peek() != EOF)
    {
        rOldStream.read((char*)&buffer, sizeof(Ticket));
        if (buffer.key == key)
        {
            toWrite = new Ticket(buffer);
            number = i;
            ENDSTREAM(rOldStream)
        }
        i++;
    }

    rOldStream.close();
    return -2;
}

int deleteRecordFromBinByNumber(const string& filename, int number)
{
    if (number < 0)
    {
        return -2;
    }
    fstream rwStream;
    rwStream.open(filename, ios::ios_base::binary | ios::ios_base::in | ios::ios_base::out);
    CHECK(rwStream, -1)


    rwStream.seekg(0, std::ifstream::end);
    int fileLength = rwStream.tellg();

    if ((number + 1) * sizeof(Ticket) > fileLength)
    {
        rwStream.close();
        return -2;
    }

    Ticket last;
    int offset = number * sizeof(Ticket);

    rwStream.seekg(0, std::fstream::end);
    int lastOffset = rwStream.tellg();
    lastOffset -= sizeof(Ticket);

    rwStream.seekg(lastOffset);

    rwStream.read((char*)&last, sizeof(Ticket));

    rwStream.seekg(offset);

    rwStream.write((char*)&last, sizeof(Ticket));

    rwStream.close();

    filesystem::resize_file(filename, lastOffset);
    return rwStream.bad();
}


void testBinF(const string& txtFilename)
{
    cout << "Начало тестирования" << "binary module" << endl;
    int result;
    string binFilename = "testbin.bin";
    LINE()
    cout << "Конвертация из " << txtFilename << " в " << binFilename << "..." << endl;
    result = convertTextToBin(txtFilename, binFilename);
    TESTCODE(result)

    LINE()
    cout << "Вывод содержимого из " << binFilename << endl;
    result = printFromBin(binFilename);
    TESTCODE(result)

    int recordNumber = 1;
    Ticket* record = nullptr;
    LINE()
    cout << "Получение записи под номером " << recordNumber << " из файла " << binFilename << "..." << endl;
    result = getRecordFromBin(binFilename, recordNumber, record);
    TESTCODECONDITION(result, (record->key == 2123))
    if (result == 0)
    {
        if (record == nullptr)
        {
            cout << "Ошибка, функция вернула успех, но запись nullptr" << endl;
        }
        else
        {
            record->print();
            CLEAR(record)
        }
    }

    LINE()
    cout << "Поиск записи по ключу " << 2123 << " из файла " << binFilename << "..." << endl;
    int n;
    result = searchRecordFromBin(binFilename, 2123, record, n);
    TESTCODECONDITION(result, (record->phoneNumber[1] == '4')) //+432523423433
    if (result == 0)
    {
        if (record == nullptr)
        {
            cout << "Ошибка, функция вернула успех, но запись nullptr" << endl;
        }
        else
        {
            record->print();
            cout << "Порядковый номер записи: " << n << endl;
            CLEAR(record)
        }
    }

    recordNumber = 1;
    LINE()
    cout << "Удаление записи под номером " << recordNumber << " из файла " << binFilename << "..." << endl;
    cout << "Файл до: " << endl;
    printFromBin(binFilename);
    cout << "Начало операции" << endl;
    result = deleteRecordFromBinByNumber(binFilename, recordNumber);
    cout << endl << "Файл после:" << endl;
    printFromBin(binFilename);
    TESTCODECONDITION(result, (searchRecordFromBin(binFilename, 2123, record, recordNumber) == -2))

    LINE()
    cout << "Добавление записи:" << endl;
    printFromBin(binFilename);

    cout << "Запись:" << endl;
    record = new Ticket();
    record->key = 1235;
    strcpy(record->fio, "Павлов К.С.");
    strcpy(record->phoneNumber, "+923545341123");
    record->print();
    result = addRecordToBin(binFilename, record);
    cout << endl << "Файл после добавления" << endl;
    printFromBin(binFilename);
    TESTCODECONDITION(result, (searchRecordFromBin(binFilename, record->key, record, recordNumber) == 0))

    cout << "Тестирование модуля для работы с бинарными файлами завершено" << endl;
}
