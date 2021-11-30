from io import FileIO
import os
    

def read_number(file:FileIO, bytes:int = 4, signed=False)->int:
    return int.from_bytes(file.read(bytes), byteorder='little', signed=signed)


class BmpReader:
    def load(self, path) -> None:
        if not os.path.exists(path):
            print("错误: 路径不存在!")
            raise Exception
        file = open(path, 'rb')
        if file.read(2) != b'BM':
            print("文件类型不是bmp文件")
            raise Exception

        self.colors = []
        self.fileSize = read_number(file) # 文件大小
        read_number(file) # 略过保留字节
        self.dataAddr = read_number(file) # 像素数组的起始地址
        self.infoSize = read_number(file) # 信息头长度
        if self.infoSize != 40:
            print("无法识别该文件")
            raise Exception
        self.width = read_number(file, signed=True)   # 宽
        self.height = read_number(file, signed=True)  # 高
        if self.height < 0:
            self.height = abs(self.height)
            self.scanlineOrder = "down"
        else:
            self.scanlineOrder = "up"
        read_number(file, 2) # 色彩平面数，总是1
        self.pixelSize = read_number(file, 2) # 每个像素所占的bit数，即色深
        self.compressType = read_number(file) # 压缩说明
        self.dataSize = read_number(file) # 原始位图数据大小
        self.horiReso = read_number(file) # 水平分辨率
        self.vertReso = read_number(file) # 垂直分辨率
        self.colorNum = read_number(file) # 颜色数, 为0表示为默认的(2^色深)个
        self.impoColorNum = read_number(file) # 重要的颜色索引数，为0时表示所有颜色都是重要的；通常不使用本项
        if not file.tell() == self.dataAddr:
            # 调色板
            self.colors = []
            if self.colorNum == 0:
                colorNum = 2**self.pixelSize
            else:
                colorNum = self.colorNum
            i = 0
            while i<colorNum:
                bluePart = read_number(file, 1) # 蓝色分量
                greenPart = read_number(file, 1) # 蓝色分量
                redPart = read_number(file, 1) # 蓝色分量
                alpha = read_number(file, 1) # 填充符
                self.colors.append([bluePart,greenPart,redPart,alpha])
                i+=1
        
        if file.tell()!=self.dataAddr:
            print("数据读取有误")
            raise Exception
        data = file.read()
        file.close()

        self.scanlines = []
        self.scanlineLength = self.width*self.pixelSize//8
        if self.scanlineLength%4!=0:
            self.lineLength = self.scanlineLength + 4 - self.scanlineLength%4
        else:
            self.lineLength = self.scanlineLength
        if self.scanlineOrder == "up":
            for lineNum in range(self.height):
                lineIndex = (self.height-lineNum-1)*self.lineLength
                self.scanlines.append(data[lineIndex:lineIndex+self.lineLength])
        else:
            for lineNum in range(self.height):
                lineIndex = lineNum*self.lineLength
                self.scanlines.append(data[lineIndex:lineIndex+self.lineLength])
        
    
    def display(self):
        print("文件大小为：{} bytes".format(self.fileSize))
        print("像素数组的起始地址为：{} bytes".format(self.dataAddr))
        print("信息头长度为：{} bytes".format(self.infoSize))
        print("图片宽度为：{} bytes".format(self.width))
        print("图片高度为：{} bytes".format(self.height))
        print("每个像素的位数：{} ".format(self.pixelSize))
        print("压缩类型：{} ".format(self.compressType))
        print("像素数据大小：{} bytes".format(self.dataSize))
        print("颜色索引数：{} bytes".format(self.colorNum))
        print("重要的颜色索引数：{} bytes".format(self.impoColorNum))
        print("调色板为：{}".format(self.colors))
        print("扫描线数据：")
        for line in self.scanlines:
            print(line)
        print("分析完成！")
    

    def save(self, path):
        with open(path, 'wb') as f:
            f.write(b'BM')
            f.write(self.fileSize.to_bytes(4,byteorder='little'))
            f.write((0).to_bytes(4,byteorder='little'))
            f.write(self.dataAddr.to_bytes(4,byteorder='little'))
            f.write(self.infoSize.to_bytes(4,byteorder='little'))
            f.write(self.width.to_bytes(4,byteorder='little'))
            f.write(self.height.to_bytes(4,byteorder='little'))
            f.write((1).to_bytes(2,byteorder='little'))
            f.write(self.pixelSize.to_bytes(2,byteorder='little'))
            f.write(self.compressType.to_bytes(4,byteorder='little'))
            f.write(self.dataSize.to_bytes(4,byteorder='little'))
            f.write(self.horiReso.to_bytes(4,byteorder='little'))
            f.write(self.vertReso.to_bytes(4,byteorder='little'))
            f.write(self.colorNum.to_bytes(4,byteorder='little'))
            f.write(self.impoColorNum.to_bytes(4,byteorder='little'))
            if self.colors:
                for colorForm in self.colors:
                    for color in colorForm:
                        f.write(color.to_bytes(1,byteorder='little'))
            f.write(self.data)



if __name__ == "__main__":
    bmp = BmpReader()
    bmp.load("3.bmp")
    bmp.save("icon.bmp")
    
