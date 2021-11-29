from io import FileIO
import os

def input_available(path:str)->FileIO:
    if not os.path.exists(path):
        print("错误: 路径不存在!")
        return None
    f = open(path, 'rb')
    filetype = f.read(2)
    if filetype != b'BM':
        print("文件类型不是bmp文件")
        f.close()
        return None
    return f


def read_number(file:FileIO, bytes:int = 4)->int:
    return int.from_bytes(file.read(bytes), byteorder='little')


class BmpReader:
    def load(self, path) -> None:
        self.colors = None
        file = input_available(path)
        if not file:
            print("打开文件失败！")
            return

        self.fileSize = read_number(file) # 文件大小
        read_number(file) # 略过保留字节
        self.dataAddr = read_number(file) # 像素数组的起始地址
        self.infoSize = read_number(file) # 信息头长度
        self.width = read_number(file)   # 宽
        self.height = read_number(file)  # 高
        read_number(file, 2) # 色彩平面数，总是1
        self.pixelSize = read_number(file, 2) # 每个像素的位数，即色深
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
            while i<colorNum and file.tell()<self.dataAddr:
                bluePart = read_number(file, 1) # 蓝色分量
                greenPart = read_number(file, 1) # 蓝色分量
                redPart = read_number(file, 1) # 蓝色分量
                alpha = read_number(file, 1) # 填充符
                self.colors.append([bluePart,greenPart,redPart,alpha])
                i+=1
        
        if file.tell()!=self.dataAddr:
            print("数据读取有误")
        self.data = file.read()
        file.close()
    
    
    def save(self, path)-> None:
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


def analyze_bmp(path:str)->None:
    print("开始分析文件：{}".format(path))

    # 判断合法性
    bmp = BmpReader()
    bmp.load(path)

    print("文件大小为：{} bytes".format(bmp.fileSize))
    print("像素数组的起始地址为：{} bytes".format(bmp.dataAddr))
    print("信息头长度为：{} bytes".format(bmp.infoSize))
    print("图片宽度为：{} bytes".format(bmp.width))
    print("图片高度为：{} bytes".format(bmp.height))
    print("每个像素的位数：{} ".format(bmp.pixelSize))
    print("压缩类型：{} ".format(bmp.compressType))
    print("像素数据大小：{} bytes".format(bmp.dataSize))
    print("水平分辨率：{} bytes".format(bmp.horiReso))
    print("垂直分辨率：{} bytes".format(bmp.vertReso))
    print("颜色索引数：{} bytes".format(bmp.colorNum))
    print("重要的颜色索引数：{} bytes".format(bmp.impoColorNum))
    print("分析完成！")


    
    



if __name__ == "__main__":
    path = "test_change.bmp"
    # analyze_bmp(path)
    bmp = BmpReader()
    bmp.load("1608195700280181.bmp")
    print(bmp.data)
    print('\n'*5)
    bmp1 = BmpReader()
    bmp1.load("test_change.bmp")
    print(bmp1.data)
    
