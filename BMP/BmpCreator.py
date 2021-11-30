

def create_bmp(path, width, height, pixelSize, compressType, scanlines, colorPanel=[], scanlineOder="up"):
    real_bytes_num = (width*pixelSize+7)//8
    if (real_bytes_num)%4==0:
        fill_zero_size = 0
    else:
        fill_zero_size = 4 - real_bytes_num%4
    fill_zero = fill_zero_size * b'0'
    dataList = []
    for scanline in scanlines:
        dataList.append(scanline+fill_zero)
    data = b''.join(dataList)

    dataSize = len(data)
    fileSize = dataSize + 4*len(colorPanel) + 54
    dataAddr = fileSize-dataSize
    infoLength = 40

    def write_number(file, number, bytesNum=4, order='little', signed=False):
        file.write(number.to_bytes(bytesNum, byteorder=order, signed=signed))
    with open(path, 'wb') as f:
        f.write(b'BM')
        write_number(f, fileSize)
        write_number(f, 0)
        write_number(f, dataAddr)
        write_number(f, infoLength)
        write_number(f, width)
        write_number(f, height, signed=True)
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
