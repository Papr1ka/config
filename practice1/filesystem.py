from fs.zipfs import ZipFS
from fs.tarfs import TarFS
from fs.tarfs import WrapFS

class ArchiveFileSystemFactory():
    @staticmethod
    def getSystem(filename: str) -> WrapFS:

        if filename.endswith(".zip"):
            system = ZipFS(filename)
        elif filename.endswith(".tar"):
            system = TarFS(filename)
        else:
            raise ValueError("Ошибка, формат архива может быть либо zip, либо tar")
        return system
