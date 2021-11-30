from PNG.PngReader import PngReader, read_IDAT, read_PLTE
import zlib
from BMP.BmpCreator import create_bmp


def png_to_bmp(png_path, bmp_path):
    png = PngReader()
    png.load(png_path)

    if png.colorType == 3:
        color3Png_to_bmp(png, bmp_path)
        return
    elif png.colorType == 6:
        color6depth8Png_to_bmp(png, bmp_path)
        return


def color6depth8Png_to_bmp(pngReader, bmp_path):
    filtered_data = b''
    for chunk in pngReader.get_all_chunks(b'IDAT'):
        filtered_data += zlib.decompress(chunk.ChunkData)
    if len(filtered_data) % pngReader.height != 0:
        raise Exception
    filt_scanlines = read_IDAT(pngReader.get_chunk(b'IDAT').ChunkData, pngReader.width,pngReader.height,pngReader.bitDepth)
    scanlines = []
    for filt_line in filt_scanlines:
        tmpDatas = []
        i = 1
        while i < len(filt_line):
            tmpDatas.append(filt_line[i+2])
            tmpDatas.append(filt_line[i+1])
            tmpDatas.append(filt_line[i])
            tmpDatas.append(filt_line[i+3])
            i+=4
        scanlines.append(b''.join(map(lambda a:a.to_bytes(1,byteorder='big'),tmpDatas)))
    create_bmp(bmp_path, pngReader.width, 0-pngReader.height,
               32,0,scanlines)


def color3Png_to_bmp(pngReader, bmp_path):
    filt_lines = read_IDAT(pngReader.get_chunk(b'IDAT').ChunkData, pngReader.width, pngReader.height, pngReader.bitDepth)
    scanlines = list(map(lambda a:a[1:], filt_lines))

    colorPanel = []
    if pngReader.bitDepth == 1:
        colorPanel.append([0, 0, 0, 0])
        colorPanel.append([255, 255, 255, 0])
    else:
        for color in read_PLTE(pngReader.get_chunk(b'PLTE').ChunkData):
            colorPanel.append([color[2], color[1], color[0], 0])

    create_bmp(bmp_path, pngReader.width, pngReader.height,
               pngReader.bitDepth, 0,scanlines[::-1], colorPanel)


if __name__ == "__main__":
    png_to_bmp("1608195700280181.png", "3.bmp")



