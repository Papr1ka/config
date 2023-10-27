from vshell import VShell
import sys

# Для корректной работы программы необходимо передать путь к архиву с расширением .zip или .tar

if __name__ == "__main__":
    if len(sys.argv) > 1:
        shell = VShell(
            sys.argv[1]
        )
        shell.run()
    else:
        print("Ошибка, необходимо указать имя файла")
