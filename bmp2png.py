from BMP.BmpReader import BmpReader
from PNG.PngCreator import create_png, create_IDAT, create_IEND, create_IHDR


def bmp32toPng(bmp: BmpReader, png_path):
    filt_lines = []
    for scanline in bmp.scanlines:
        filt_lines.append(b'0' + scanline)

    create_png(png_path, bmp.width, bmp.height, 8, 6, filt_lines)


def bmp_to_png(bmp_path, png_path):
    bmp = BmpReader()
    bmp.load(bmp_path)

    if bmp.pixelSize == 32:
        bmp32toPng(bmp, png_path)
        return

    BGRcolorPanel = []
    if bmp.colors:
        for color in bmp.colors:
            BGRcolorPanel.append([color[2], color[1], color[0]])

    scanlines = []
    lineExpectedLength = ((bmp.pixelSize*bmp.width+31)//32)*4
    for relineNum in range(bmp.height):
        if bmp.scanlineOrder == "up":
            lineNum = bmp.height - relineNum - 1
        else:
            lineNum = relineNum
        scanlines.append(
            b'0' + bmp.data[lineNum*lineExpectedLength:lineNum*lineExpectedLength+bmp.width*bmp.pixelSize//8])

    create_png(png_path, bmp.width, bmp.height,
               bmp.pixelSize, 3, scanlines, BGRcolorPanel)


def bmp32toPng(bmp: BmpReader, png_path):
    filt_lines = []
    for scanline in bmp.scanlines:
        i = 0
        datas = [0]
        while i < len(scanline):
            datas.append(scanline[i+2])
            datas.append(scanline[i+1])
            datas.append(scanline[i])
            datas.append(scanline[i+3])
            i += 4
        filt_lines.append(
            b''.join(list(map(lambda a: a.to_bytes(1, byteorder='big'), datas))))

    form_c6_d8_png(png_path, bmp.width, bmp.height, filt_lines)


def form_c6_d8_png(path, width, height, filt_scanlines):
    ihdr = create_IHDR(width, height, 8, 6)
    idat = create_IDAT(filt_scanlines)
    iend = create_IEND()
    save_png([ihdr, idat, iend], path)


def save_png(chunks, path):
    with open(path, 'wb') as f:
        f.write((0x89504E470D0A1A0A).to_bytes(8, byteorder='big'))
        for chunk in chunks:
            chunk.save(f)


if __name__ == "__main__":
    bmp_to_png("icon-211027134435Z-258.bmp", "3.png")
