import cv2
import sys
from PIL import Image
from numpy import asarray
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QGroupBox
from PyQt5.QtGui import QPixmap, QImage


class NewImage(QWidget):

    def __init__(self, npImage):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
        groupBox = QGroupBox()
        vbox = QVBoxLayout()
        label = QLabel(self)
        pixmap = self.ConvertNumpyToQPixmap(npImage)
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        vbox.addWidget(label)
        groupBox.setLayout(vbox)
        grid.addWidget(groupBox, 0, 0)
        self.resize(pixmap.width(), pixmap.height())
        self.setWindowTitle('JAC Image')
        self.show()

    @staticmethod
    def ConvertNumpyToQPixmap(np_img):
        img = Image.open(np_img)
        numpydata = asarray(img)
        print(numpydata)
        height, width, channel = numpydata.shape
        bytesPerLine = 4*width
        return QPixmap(QImage(numpydata, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    currentNumpyImage = cv2.imread("capture.png")
    window = NewImage(currentNumpyImage)
    sys.exit(app.exec_())