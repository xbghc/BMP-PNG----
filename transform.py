

def toPNGcolorPanel(BMPcolorPanel):
    PNGcolorPanel = []
    for color in BMPcolorPanel:
        PNGcolorPanel.append([color[2], color[1], color[0]])


def toBMPcolorPanel(PNGcolorPanel):
    BMPcolorPanel = []
    for color in PNGcolorPanel:
        BMPcolorPanel.append([color[2], color[1], color[0], 0])


if __name__ == "__main__":
    # png_to_bmp('small/1608195700280181.png', "small/transBmp.bmp")
    pass
