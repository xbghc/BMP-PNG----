# 规定一下命名
# filt_line = (filter type) + data
# scanline是没有被过滤处理的数据

def deFiltering(filt_lines, bitDepth):
    def deFiltering0(data: bytes):
        return data


    def deFiltering1(data: bytes, bitDepth: int):
        if bitDepth >= 8:
            prev_offset = bitDepth//8
        else:
            prev_offset = 1
        dataList = []
        for i in range(len(data)):
            prev = i - prev_offset
            if prev < 0:
                prev_value = 0
            else:
                prev_value = dataList[prev]
            dataList.append(prev_value + data[i])
        return b''.join(map(lambda a: a.to_bytes(1, byteorder='big'), dataList))


    def deFiltering2(data: bytes, prev_line: bytes):
        dataList = []
        for i in range(len(data)):
            b = prev_line[i]
            dataList.append(b + data[i])
        return b''.join(map(lambda a: a.to_bytes(1, byteorder='big'), dataList))


    def deFiltering3(data: bytes, bitDepth: int, prev_line: bytes):
        dataList = []
        prev_offset = (bitDepth+7)//8
        for i in range(len(data)):
            prev = i - prev_offset
            if prev < 0:
                a = 0
            else:
                a = dataList[prev]
            b = prev_line[i]
            dataList.append((a+b)//2 + data[i])
        return b''.join(map(lambda a: a.to_bytes(1, byteorder='big'), dataList))


    def deFiltering4(data: bytes, bitDepth: int, prev_line: bytes):
        dataList = []
        prev_offset = (bitDepth+7)//8
        for i in range(len(data)):
            prev = i - prev_offset
            if prev < 0:
                a = 0
                c = 0
            else:
                a = dataList[prev]
                c = prev_line[prev]
            b = prev_line[i]
            p = a + b - c
            pa = abs(p-a)
            pb = abs(p-b)
            pc = abs(p-c)
            pr = min(pa,pb,pc)
            dataList.append(pr + data[i])
        return b''.join(map(lambda a: a.to_bytes(1, byteorder='big'), dataList))    
    scanlines = []
    for lineNum in range(len(filt_lines)):
        filt_line = filt_lines[lineNum]
        filt_type = filt_line[0]
        data = filt_line[1:]
        if filt_type == 0:
            scanlines.append(deFiltering0(data))
        elif filt_type == 1:
            scanlines.append(deFiltering1(data, bitDepth))
        elif filt_type == 2:
            scanlines.append(deFiltering2(data, scanlines[-1]))
        elif filt_type == 3:
            scanlines.append(deFiltering3(data, bitDepth, scanlines[-1]))
        elif filt_type == 4:
            scanlines.append(deFiltering4(data, bitDepth, scanlines[-1]))
    return scanlines




