import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QTextEdit, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        # Selection Panel
        groupBox = QGroupBox("Selection Panel")
        vbox = QVBoxLayout()

        button1 = QPushButton('Button 1')
        button2 = QPushButton('Button 2')
        button3 = QPushButton('Button 3')

        vbox.addWidget(button1)
        vbox.addWidget(button2)
        vbox.addWidget(button3)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        grid.addWidget(groupBox, 0, 0)

        # Text Boxes
        groupBox2 = QGroupBox("Text Boxes")
        vbox2 = QVBoxLayout()

        hbox1 = QHBoxLayout()
        label1 = QLabel("Label 1")
        textbox1 = QLineEdit()
        hbox1.addWidget(label1)
        hbox1.addWidget(textbox1)
        vbox2.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        label2 = QLabel("Label 2")
        textbox2 = QTextEdit()
        hbox2.addWidget(label2)
        hbox2.addWidget(textbox2)
        vbox2.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        label3 = QLabel("Label 3")
        textbox3 = QLineEdit()
        hbox3.addWidget(label3)
        hbox3.addWidget(textbox3)
        vbox2.addLayout(hbox3)

        hbox4 = QHBoxLayout()
        label4 = QLabel("Label 4")
        textbox4 = QLineEdit()
        hbox4.addWidget(label4)
        hbox4.addWidget(textbox4)
        vbox2.addLayout(hbox4)

        vbox2.addStretch(1)
        groupBox2.setLayout(vbox2)
        grid.addWidget(groupBox2, 0, 1, 2, 1)

        self.setGeometry(300, 300, 700, 400)
        self.setWindowTitle('Basic GUI')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
