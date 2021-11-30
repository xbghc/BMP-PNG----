import zlib
from .Chunk import Chunk


def read_number_big(file, bytes: int = 4) -> int:
    return int.from_bytes(file.read(bytes), byteorder='big', signed=True)


def read_IHDR(IHDR_bytes):
    info = {}
    info['width'] = int.from_bytes(IHDR_bytes[0:4], byteorder='big')
    info['height'] = int.from_bytes(IHDR_bytes[4:8], byteorder='big')
    info['bitDepth'] = IHDR_bytes[8]
    info['colorType'] = IHDR_bytes[9]
    info['compressionMethod'] = IHDR_bytes[10]
    info['filterMethod'] = IHDR_bytes[11]
    info['interlaceMethod'] = IHDR_bytes[12]
    return info


def read_PLTE(PLTE_bytes):
    BGRcoloPanel = []
    i = 0
    while i < len(PLTE_bytes):
        BGRcoloPanel.append([PLTE_bytes[i], PLTE_bytes[i+1], PLTE_bytes[i+2]])
        i += 3
    return BGRcoloPanel


def read_IDAT(idat_bytes, width, height, bitDepth):
    decompressed_bytes = zlib.decompress(idat_bytes)

    line_length = len(decompressed_bytes)//height
    filt_scanlines = []
    for lineNum in range(height):
        filt_scanlines.append(
            decompressed_bytes[lineNum*line_length:(lineNum+1)*line_length])

    return filt_scanlines


def read_tEXt(tEXt_bytes):
    key = b''
    value = b''
    i = 0
    while tEXt_bytes[i] != 0:
        key += tEXt_bytes[i].to_bytes(1, byteorder="big")
        i += 1
    i += 1
    while i < len(tEXt_bytes):
        value += tEXt_bytes[i].to_bytes(1, byteorder='big')
        i += 1
    return key, value


class PngReader:
    def load(self, path) -> None:
        # 检查文件是否合法
        file = open(path, 'rb')
        if int.from_bytes(file.read(8), byteorder='big') != 0x89504E470D0A1A0A:
            print("文件格式有误")
            raise Exception
        # 初始化成员变量
        self.chunks = []
        self.datas = []
        # 读取块结构
        chunk = Chunk()
        chunk.ChunkType = 1
        while chunk.ChunkType != b'IEND':
            chunk = Chunk()
            chunk.Length = read_number_big(file)
            chunk.ChunkType = file.read(4)
            chunk.ChunkData = file.read(chunk.Length)
            chunk.CRC = file.read(4)
            self.chunks.append(chunk)
        file.close()

        # 初始化读取到的数据
        ihdr_info = read_IHDR(self.get_chunk(b'IHDR').ChunkData)
        self.width = ihdr_info['width']
        self.height = ihdr_info['height']
        self.bitDepth = ihdr_info['bitDepth']
        self.colorType = ihdr_info['colorType']

    def get_chunk(self, name) -> Chunk:
        for chunk in self.chunks:
            if name == chunk.ChunkType:
                return chunk
        return None

    def get_all_chunks(self, name):
        chunks = []
        for chunk in self.chunks:
            if name == chunk.ChunkType:
                chunks.append(chunk)
        return chunks

    def save(self, path):
        with open(path, 'wb') as f:
            f.write((0x89504E470D0A1A0A).to_bytes(8, byteorder='big'))
            for chunk in self.chunks:
                if chunk.ChunkType != b'IEND':
                    chunk.save(f)
            self.get_chunk(b'IEND').save(f)


if __name__ == '__main__':
    pass
