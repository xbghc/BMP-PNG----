import zlib


def analyze_number_big(file, bytes:int = 4)->int:
    return int.from_bytes(file.read(bytes), byteorder='big')


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
        self.CRC = zlib.crc32(self.ChunkType + self.ChunkData).to_bytes(4, byteorder='big')

    def set_data(self, bytes):
        self.ChunkData = bytes
        self.Length = len(bytes)

    def save(self, file):
        file.write(self.Length.to_bytes(4,byteorder='big'))
        file.write(self.ChunkType)
        file.write(self.ChunkData)
        file.write(self.CRC)


def form_IHDR(width, height, bitDepth):
    chunk = Chunk()
    chunk.ChunkType = b'IHDR'
    data = width.to_bytes(4, byteorder='big')
    data += height.to_bytes(4, byteorder='big')
    data += bitDepth.to_bytes(1, byteorder='big')
    data += (3).to_bytes(1, byteorder='big')
    data += (0).to_bytes(1, byteorder='big')
    data += (0).to_bytes(1, byteorder='big')
    data += (0).to_bytes(1, byteorder='big')
    chunk.set_data(data)
    chunk.form_CRC()
    return chunk


def form_PLTE(GBRcolorPanel):
    chunk = Chunk()
    chunk.ChunkType = b'PLTE'
    data = b''
    for color in GBRcolorPanel:
        data += color[0].to_bytes(1, byteorder='big')
        data += color[1].to_bytes(1, byteorder='big')
        data += color[2].to_bytes(1, byteorder='big')
    chunk.set_data(data)
    chunk.form_CRC()
    return chunk


def form_IEND():
    chunk = Chunk()
    chunk.ChunkType = b'IEND'
    chunk.set_data(b'')
    chunk.form_CRC()
    return chunk


def form_IDAT(filtered_data_scanlines):
    chunk = Chunk()
    chunk.ChunkType = b'IDAT'
    data = b''
    data = b''.join(filtered_data_scanlines)
    data = zlib.compress(data)
    chunk.set_data(data)
    chunk.form_CRC()
    return chunk


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
    i=0
    while i < len(PLTE_bytes):
        BGRcoloPanel.append([PLTE_bytes[i], PLTE_bytes[i+1], PLTE_bytes[i+2]])
        i+=3
    return BGRcoloPanel


def read_IDAT(idat_bytes, width, height, bitDepth):
    decompressed_bytes = zlib.decompress(idat_bytes)
    if len(decompressed_bytes) != height*(width*bitDepth//8+1):
        print("数据与图片宽、高、位深不符合")
        raise Exception

    line_length = len(decompressed_bytes)//height
    filtered_data_scanlines = []
    for lineNum in range(height):
        filtered_data_scanlines.append(decompressed_bytes[lineNum*line_length:(lineNum+1)*line_length])

    return filtered_data_scanlines


def read_tEXt(tEXt_bytes):
    key = b''
    value = b''
    i = 0
    while tEXt_bytes[i]!=0:
        key += tEXt_bytes[i].to_bytes(1,byteorder="big")
        i+=1
    i+=1
    while i<len(tEXt_bytes):
        value+=tEXt_bytes[i].to_bytes(1,byteorder='big')
        i+=1
    return key,value


class PngReader:
    def load(self, path) -> None:
        # 检查文件是否合法
        file = open(path, 'rb')
        if int.from_bytes(file.read(8), byteorder='big') != 0x89504E470D0A1A0A:
            print("文件格式有误")
            return
            
        # 初始化成员变量
        self.chunks = []
        self.datas = []

        # 读取块结构
        chunk = Chunk()
        chunk.ChunkType = 1
        while chunk.ChunkType!=b'IEND':
            chunk = Chunk()
            chunk.Length = analyze_number_big(file)
            chunk.ChunkType = file.read(4)
            chunk.ChunkData = file.read(chunk.Length)
            chunk.CRC = file.read(4)
            self.chunks.append(chunk)
        file.close()

        # 初始化读取到的数据
        ihdr_info = read_IHDR(self.get_chunk(b'IHDR').ChunkData)
        self.width = ihdr_info['width']
        self.height = ihdr_info['height']
        self.pixelSize = ihdr_info['bitDepth']


    def get_chunk(self, name)->Chunk:
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
            f.write((0x89504E470D0A1A0A).to_bytes(8,byteorder='big'))
            for chunk in self.chunks:
                if chunk.ChunkType != b'IEND':
                    chunk.save(f)
            self.get_chunk(b'IEND').save(f)


if __name__ == '__main__':
    png = PngReader()
    png.load('small/1608195700280181.png')

    ihdr = png.get_chunk(b'IHDR')
    plte = png.get_chunk(b'PLTE')
    idat = png.get_chunk(b'IDAT')
    iend = png.get_chunk(b'IEND')

    ihdr1 = form_IHDR(png.width,png.height,png.pixelSize)
    plte1 = form_PLTE(read_PLTE(plte.ChunkData))
    realData = idat.ChunkData
    
    scanlines = read_IDAT(idat.ChunkData, png.width, png.height,png.pixelSize)
    idat1 = form_IDAT(scanlines)
    
    png1 = PngReader()
    png1.chunks = [ihdr1,plte1,idat1,iend]
    png1.save("small/test_save_png.png")
    def compare(c1,c2):
        print(c1.Length == c2.Length)
        print(c1.ChunkType == c2.ChunkType)
        print(c1.ChunkData == c2.ChunkData)
        print(c1.CRC == c2.CRC)

    def compare_detail(c1,c2):
        if c1.Length != c2.Length:
            print("Length:")
            print(c1.Length)
            print(c2.Length)
        if c1.ChunkType != c2.ChunkType:
            print("ChunkType:")
            print(c1.ChunkType)
            print(c2.ChunkType)
        if c1.ChunkData != c2.ChunkData:
            print("ChunkData：")
            print(c1.ChunkData)
            print(c2.ChunkData)
    compare_detail(idat,idat1)
