from .Chunk import Chunk
import zlib


def create_IHDR(width, height, bitDepth, colourType):
    chunk = Chunk()
    chunk.ChunkType = b'IHDR'
    data = width.to_bytes(4, byteorder='big')
    data += height.to_bytes(4, byteorder='big')
    data += bitDepth.to_bytes(1, byteorder='big')
    data += colourType.to_bytes(1, byteorder='big')
    data += (0).to_bytes(1, byteorder='big') # 压缩方法
    data += (0).to_bytes(1, byteorder='big') # 过滤方法
    data += (0).to_bytes(1, byteorder='big') # 混合方式
    chunk.set_data(data)
    chunk.form_CRC()
    return chunk


def create_PLTE(GBRcolorPanel):
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


def create_IEND():
    chunk = Chunk()
    chunk.ChunkType = b'IEND'
    chunk.set_data(b'')
    chunk.form_CRC()
    return chunk


def create_IDAT(filt_lines):
    chunk = Chunk()
    chunk.ChunkType = b'IDAT'
    data = b''
    data = b''.join(filt_lines)
    data = zlib.compress(data)
    chunk.set_data(data)
    chunk.form_CRC()
    return chunk


def create_png(path, width, height, bitDepth, colourType, filt_lines, BGRcolorPanel=None):
    ihdr = create_IHDR(width, height, bitDepth, colourType)
    idat = create_IDAT(filt_lines)
    iend = create_IEND()

    if colourType == 3:
        plte = create_PLTE(BGRcolorPanel)
        chunks = [ihdr, plte, idat, iend]
    else:
        chunks = [ihdr, idat, iend]

    with open(path, 'wb') as f:
        f.write((0x89504E470D0A1A0A).to_bytes(8, byteorder='big'))
        for chunk in chunks:
            chunk.save(f)

