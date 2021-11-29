from BmpReader import BmpReader
from PngReader import *
import zlib


def toPNGcolorPanel(BMPcolorPanel):
    PNGcolorPanel = []
    for color in BMPcolorPanel:
        PNGcolorPanel.append([color[2], color[1], color[0]])


def toBMPcolorPanel(PNGcolorPanel):
    BMPcolorPanel = []
    for color in PNGcolorPanel:
        BMPcolorPanel.append([color[2], color[1], color[0], 0])


def form_bmp(path, width, height, pixelSize, compressType, data, colorPanel=None):
    dataSize = len(data)
    fileSize = dataSize + 4*len(colorPanel) + 54
    dataAddr = fileSize-dataSize
    infoLength = 40

    def write_number(file, number, bytesNum=4, order='little'):
        file.write(number.to_bytes(bytesNum, byteorder=order))
    with open(path, 'wb') as f:
        f.write(b'BM')
        write_number(f, fileSize)
        write_number(f, 0)
        write_number(f, dataAddr)
        write_number(f, infoLength)
        write_number(f, width)
        write_number(f, height)
        write_number(f, 1, 2)
        write_number(f, pixelSize, 2)
        write_number(f, compressType)
        write_number(f, dataSize)
        write_number(f, 0)  # 水平像素
        write_number(f, 0)  # 垂直像素
        write_number(f, len(colorPanel))
        write_number(f, 0)
        if colorPanel:
            for color in colorPanel:
                for i in color:
                    write_number(f, i, 1)
        f.write(data)


def png_to_bmp(png_path, bmp_path):
    png = PngReader()
    png.load(png_path)

    filtered_data = b''
    for chunk in png.get_all_chunks(b'IDAT'):
        filtered_data += zlib.decompress(chunk.ChunkData)
    scanlines = []
    lineNum = 0
    if len(filtered_data) % png.height != 0:
        raise Exception
    lineRealLength = len(filtered_data)//png.height - 1
    lineExpectedLength = ((png.pixelSize*png.width+31)//32)*4
    fill_zero = b'\x00' * (lineExpectedLength - lineRealLength)

    while lineNum < png.height:
        line_data = filtered_data[lineNum*(lineRealLength+1) +
                                  1:(lineNum+1)*(lineRealLength+1)] + fill_zero
        scanlines.append(line_data)
        lineNum += 1
    data = b''
    i = 1
    while i <= len(scanlines):
        data += scanlines[len(scanlines)-i]
        i += 1

    colorPanel = []

    if png.pixelSize == 1:
        colorPanel.append([0, 0, 0, 0])
        colorPanel.append([255, 255, 255, 0])
    else:
        for color in PngReader.format_PLTE(png.get_chunk(b'PLTE').ChunkData):
            colorPanel.append([color[2], color[1], color[0], 0])

    form_bmp(bmp_path, png.width, png.height,
             png.pixelSize, 0, data, colorPanel)


def form_png(path, width, height, bitDepth, BGRcolorPanel, filtered_data_scanlines):
    ihdr = form_IHDR(width, height, bitDepth)
    plte = form_PLTE(BGRcolorPanel)
    idat = form_IDAT(filtered_data_scanlines)
    iend = form_IEND()

    png = PngReader()
    png.chunks = [ihdr, plte, idat, iend]
    png.save(path)


def bmp_to_png(bmp_path, png_path):
    bmp = BmpReader()
    bmp.load(bmp_path)

    BGRcolorPanel = []
    for color in bmp.colors:
        BGRcolorPanel.append([color[2], color[1], color[0]])

    scanlines = []
    lineExpectedLength = ((bmp.pixelSize*bmp.width+31)//32)*4
    for relineNum in range(bmp.height):
        lineNum = bmp.height - relineNum - 1
        scanlines.append(
            b'0' + bmp.data[lineNum*lineExpectedLength:lineNum*lineExpectedLength+bmp.width*bmp.pixelSize//8])

    form_png(png_path, bmp.width, bmp.height,
             bmp.pixelSize, BGRcolorPanel, scanlines)


if __name__ == "__main__":

    # png_to_bmp('small/1608195700280181.png', "small/transBmp.bmp")
    bmp_to_png("small/transBmp.bmp", "small/tansPng.png")
