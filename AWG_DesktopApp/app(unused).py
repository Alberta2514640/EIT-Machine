import sys
import io
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QTextEdit, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from EIT.JAC import eit_external_mesh
from NewNumpyImageWindow import NewImage

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        # Selection Panel
        groupBox = QGroupBox("Output Selection")
        vbox = QVBoxLayout()

        output1 = QPushButton('Output 1')
        output2 = QPushButton('Output 2')
        output3 = QPushButton('Output 3')
        output4 = QPushButton('Output 4')

        output5 = QPushButton('Output 5')
        output6 = QPushButton('Output 6')
        output7 = QPushButton('Output 7')
        output8 = QPushButton('Output 8')

        output9 = QPushButton('Output 9')
        output10 = QPushButton('Output 10')
        output11 = QPushButton('Output 11')
        output12 = QPushButton('Output 12')

        output13 = QPushButton('Output 13')
        output14 = QPushButton('Output 14')
        output15 = QPushButton('Output 15')
        output16 = QPushButton('Output 16')

        vbox.addWidget(output1)
        vbox.addWidget(output2)
        vbox.addWidget(output3)
        vbox.addWidget(output4)

        vbox.addWidget(output5)
        vbox.addWidget(output6)
        vbox.addWidget(output7)
        vbox.addWidget(output8)

        vbox.addWidget(output9)
        vbox.addWidget(output10)
        vbox.addWidget(output11)
        vbox.addWidget(output12)

        vbox.addWidget(output13)
        vbox.addWidget(output14)
        vbox.addWidget(output15)
        vbox.addWidget(output16)

        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        grid.addWidget(groupBox, 0, 0)

        # Text Boxes
        groupBox2 = QGroupBox("Set Waveform Properties")
        vbox2 = QVBoxLayout()

        hbox1 = QHBoxLayout()
        label1 = QLabel("Square")
        button1 = QPushButton("Square")
        slider1 = QSlider(Qt.Horizontal)
        slider1.setMinimum(0)
        slider1.setMaximum(10)
        slider1.setTickPosition(QSlider.TicksBelow)
        slider1.setTickInterval(1)
        label1a = QLabel("Amplitude")
        slider1a = QSlider(Qt.Horizontal)
        slider1a.setMinimum(0)
        slider1a.setMaximum(10)
        slider1a.setTickPosition(QSlider.TicksBelow)
        slider1a.setTickInterval(1)
        label1f = QLabel("Frequency")
        slider1f = QSlider(Qt.Horizontal)
        slider1f.setMinimum(0)
        slider1f.setMaximum(10)
        slider1f.setTickPosition(QSlider.TicksBelow)
        slider1f.setTickInterval(1)
        label1o = QLabel("Offset")
        slider1o = QSlider(Qt.Horizontal)
        slider1o.setMinimum(0)
        slider1o.setMaximum(10)
        slider1o.setTickPosition(QSlider.TicksBelow)
        slider1o.setTickInterval(1)
        hbox1.addWidget(label1)
        hbox1.addWidget(button1)
        hbox1.addWidget(slider1)
        hbox1.addWidget(label1a)
        hbox1.addWidget(slider1a)
        hbox1.addWidget(label1f)
        hbox1.addWidget(slider1f)
        hbox1.addWidget(label1o)
        hbox1.addWidget(slider1o)
        vbox2.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        label2 = QLabel("Sine")
        button2 = QPushButton("Sine")
        slider2 = QSlider(Qt.Horizontal)
        slider2.setMinimum(0)
        slider2.setMaximum(10)
        slider2.setTickPosition(QSlider.TicksBelow)
        slider2.setTickInterval(1)
        label2a = QLabel("Amplitude")
        slider2a = QSlider(Qt.Horizontal)
        slider2a.setMinimum(0)
        slider2a.setMaximum(10)
        slider2a.setTickPosition(QSlider.TicksBelow)
        slider2a.setTickInterval(1)
        label2f = QLabel("Frequency")
        slider2f = QSlider(Qt.Horizontal)
        slider2f.setMinimum(0)
        slider2f.setMaximum(10)
        slider2f.setTickPosition(QSlider.TicksBelow)
        slider2f.setTickInterval(1)
        label2o = QLabel("Offset")
        slider2o = QSlider(Qt.Horizontal)
        slider2o.setMinimum(0)
        slider2o.setMaximum(10)
        slider2o.setTickPosition(QSlider.TicksBelow)

        slider2o.setTickInterval(1)
        hbox2.addWidget(label2)
        hbox2.addWidget(button2)
        hbox2.addWidget(slider2)
        hbox2.addWidget(label2a)
        hbox2.addWidget(slider2a)
        hbox2.addWidget(label2f)
        hbox2.addWidget(slider2f)
        hbox2.addWidget(label2o)
        hbox2.addWidget(slider2o)
        vbox2.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        label3 = QLabel("Triangle")
        button3 = QPushButton("Triangle")
        slider3 = QSlider(Qt.Horizontal)
        slider3.setMinimum(0)
        slider3.setMaximum(10)
        slider3.setTickPosition(QSlider.TicksBelow)
        slider3.setTickInterval(1)
        label3a = QLabel("Amplitude")
        slider3a = QSlider(Qt.Horizontal)
        slider3a.setMinimum(0)
        slider3a.setMaximum(10)
        slider3a.setTickPosition(QSlider.TicksBelow)
        slider3a.setTickInterval(1)
        label3f = QLabel("Frequency")
        slider3f = QSlider(Qt.Horizontal)
        slider3f.setMinimum(0)
        slider3f.setMaximum(10)
        slider3f.setTickPosition(QSlider.TicksBelow)
        slider3f.setTickInterval(1)
        label3o = QLabel("Offset")
        slider3o = QSlider(Qt.Horizontal)
        slider3o.setMinimum(0)
        slider3o.setMaximum(10)
        slider3o.setTickPosition(QSlider.TicksBelow)
        slider3o.setTickInterval(1)
        hbox3.addWidget(label3)
        hbox3.addWidget(button3)
        hbox3.addWidget(slider3)
        hbox3.addWidget(label3a)
        hbox3.addWidget(slider3a)
        hbox3.addWidget(label3f)
        hbox3.addWidget(slider3f)
        hbox3.addWidget(label3o)
        hbox3.addWidget(slider3o)
        vbox2.addLayout(hbox3)

        vbox2.addStretch(1)
        groupBox2.setLayout(vbox2)
        grid.addWidget(groupBox2, 0, 1, 2, 1)

        # EIT Panel
        groupBox3 = QGroupBox("EIT Options")
        
        vbox3 = QVBoxLayout()
        name = QLabel("Model")
        select= QPushButton("JAC")
        global image
        image=select.clicked.connect(self.select_clicked)
        vbox3.addWidget(name)
        vbox3.addWidget(select)

        vbox3.addStretch(1)
        groupBox3.setLayout(vbox3)
        grid.addWidget(groupBox3, 0, 2, 3, 2)

        self.setGeometry(300, 300, 700, 400)
        self.setWindowTitle('16 Channel Arbitrary Waveform Generator')
        self.show()

    def select_clicked(self):
        m=eit_external_mesh.main()
        global image
        image=NewImage('JAC.png')
        return image
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    global image
    ex = Example()
    sys.exit(app.exec_())
