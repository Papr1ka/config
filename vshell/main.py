from vshell import VShell
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        shell = VShell(
            sys.argv[1]
        )
        shell.run()
    else:
        print("Ошибка, необходимо указать имя файла")
