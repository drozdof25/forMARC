import sys
from PyQt5 import QtWidgets
import design


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buttonbrowse1.clicked.connect(self.browse_file_2d)
        self.buttonbrowse2.clicked.connect(self.browse_file_3d)

    def browse_file_2d(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файл решения', './', 'Post File (*.t16 *.t19)')
        if not file:
            return
        self.lineEdit.setText(file[0])

    def browse_file_3d(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файл решения', './', 'Post File (*.t16 *.t19)')
        if not file:
            return
        self.lineEdit_2.setText(file[0])


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()