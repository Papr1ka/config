//
// Created by joe on 19.10.23.
//

#ifndef SIAOD3_DEBUGTOOLS_H
#define SIAOD3_DEBUGTOOLS_H

#define TESTCODE(code) \
{                      \
    if (code == 0)     \
    {                  \
        cout << "+ Успешно" << endl << endl;                   \
    }                  \
    else               \
    {                  \
        cout << "- Ошибка, код " << code << endl << endl;      \
        return;\
    }\
}

#define TESTCODECONDITION(code, condition) \
{                      \
    if (code == 0 && condition)     \
    {                  \
        cout << "+ Успешно" << endl << endl;                   \
    }                  \
    else               \
    {                  \
        cout << "- Ошибка, код " << code << " условие " << condition << endl << endl;      \
        return;\
    }\
}

#define TESTCODEREVERSE(code) \
{                      \
    if (code != 0)     \
    {                  \
        cout << "+ Успешно" << endl << endl;                   \
    }                  \
    else               \
    {                  \
        cout << "- Ошибка, код " << code << endl << endl;      \
        return;\
    }\
}

#define TESTCODEREVERSECONDITION(code, condition) \
{                      \
    if (code != 0 && condition)     \
    {                  \
        cout << "+ Успешно" << endl << endl;                   \
    }                  \
    else               \
    {                  \
        cout << "- Ошибка, код " << code << " условие " << condition << endl << endl;      \
        return;\
    }\
}

#define LINE() \
{              \
    cout << endl << "#----------------------------------------------------#" << endl;\
}

#define CLEAR(allocated) \
{               \
    delete allocated;    \
    allocated = nullptr;\
}

#define PRINTTABLE() \
{                    \
cout << "Таблица:" << endl; \
cout << setw(3) << "i" << setw(16) << "Ключ" << setw(4) << "O?" << setw(3) << "D?" << setw(13) << "indexes[...]" << endl;                  \
for (int i = 0; i < table->m; i++) \
{ \
    cout << setw(3) << i; \
    table->items[i].print(); \
}                    \
cout << "Размер " << table->m << endl;\
}

#define PRINTEXECTIME(function) \
{ \
	auto begin = std::chrono::steady_clock::now(); \
	function \
	auto end = std::chrono::steady_clock::now(); \
  	auto elapsed_ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - begin); \
	cout << "Выполнение операции заняло " << elapsed_ms.count() << " ms" << endl; \
}

#endif //SIAOD3_DEBUGTOOLS_H
