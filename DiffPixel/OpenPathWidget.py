from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

debug_print = False

class OpenPathWidget(QWidget):
    pathOpenedSignal = pyqtSignal(str)
    def __init__(self, parent, open_folder, file_filter='All Types(*)'):
        super(OpenPathWidget, self).__init__(parent)
        self.open_folder = open_folder
        self.file_filter = file_filter

        pixmap = QPixmap('./asset/open.svg')
        label = QLabel(self)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        layout = QHBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            path = ''
            if self.open_folder:
                path = QFileDialog.getExistingDirectory(self, 'Open Folder', './')
            else:
                path,_ = QFileDialog.getOpenFileName(self, 'Open File', './', self.file_filter)

            if path == '':
                return 
            
            if debug_print:
                print('pathOpenedSignal:', path)
            self.pathOpenedSignal.emit(path)



import sys
if __name__ == '__main__':
    debug_print = True

    app = QApplication(sys.argv)

    widget = OpenPathWidget(None, False, 'txt(*.txt);;png(*.png)')
    #widget = OpenPathWidget(None, False, 'Image Files(*.jpg *.gif *.png *.jpeg)')

    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())

