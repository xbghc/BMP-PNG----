import zlib

class Chunk:
    def __init__(self) -> None:
        self.Length = 0
        self.ChunkType = None
        self.ChunkData = None
        self.CRC = None

    def form_CRC(self):
        if not self.ChunkType:
            print("没有设置块类型!")
            raise Exception
        self.CRC = zlib.crc32(
            self.ChunkType + self.ChunkData).to_bytes(4, byteorder='big')

    def set_data(self, bytes):
        self.ChunkData = bytes
        self.Length = len(bytes)

    def save(self, file):
        file.write(self.Length.to_bytes(4, byteorder='big'))
        file.write(self.ChunkType)
        file.write(self.ChunkData)
        file.write(self.CRC)

