from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ImageWidget import *
from OpenPathWidget import *
import cv2
    
class MainWindow(QWidget):  
    def __init__(self):  
        super().__init__()
        self.setWindowTitle("DiffPixel")

        self.original_img_widget = None
        self.modified_img_widget = None

        main_vbox = QVBoxLayout()
        self.setLayout(main_vbox)

        self.image_hbox = QHBoxLayout()
        main_vbox.addLayout(self.image_hbox,1)

        original_open_path_widget = OpenPathWidget(None,False)
        original_open_path_widget.pathOpenedSignal.connect(self.open_original_img)
        self.image_hbox.addWidget(original_open_path_widget,1)

        modified_open_path_widget = OpenPathWidget(None,False)
        modified_open_path_widget.pathOpenedSignal.connect(self.open_modified_img)
        self.image_hbox.addWidget(modified_open_path_widget,1)

        self.result_img_widget = ImageWidget(None)
        self.image_hbox.addWidget(self.result_img_widget,1)

        setting_hbox = QHBoxLayout()
        main_vbox.addLayout(setting_hbox,0)

        diff_func_combo_box = QComboBox()
        setting_hbox.addWidget(diff_func_combo_box,0)

        setting_h_spacer = QSpacerItem(700,13,QSizePolicy.Expanding,QSizePolicy.Minimum)
        setting_hbox.addItem(setting_h_spacer)

        save_button = QPushButton()
        setting_hbox.addWidget(save_button,0)

    def open_original_img(self, path):
        original_img = cv2.imread(path)
        self.original_img_data = cv2.cvtColor(original_img,cv2.COLOR_BGR2RGB)

        path_widget = self.image_hbox.itemAt(0)
        self.image_hbox.removeItem(path_widget)
        if path_widget.widget():
            path_widget.widget().deleteLater()

        self.original_img_widget = ImageWidget(None,self.original_img_data)
        self.image_hbox.insertWidget(0,self.original_img_widget,1)    

        self.diff()

    def open_modified_img(self, path):
        modified_img = cv2.imread(path)
        self.modified_img_data = cv2.cvtColor(modified_img, cv2.COLOR_BGR2RGB)

        path_widget = self.image_hbox.itemAt(1)
        self.image_hbox.removeItem(path_widget)
        if path_widget.widget():
            path_widget.widget().deleteLater()

        self.modified_img_widget = ImageWidget(None,self.modified_img_data)
        self.image_hbox.insertWidget(1,self.modified_img_widget,1)  

        self.diff()

    def diff(self):
        if  self.original_img_widget != None and self.modified_img_widget != None:
            diff_data = self.modified_img_data - self.original_img_data
            diff_data = diff_data * diff_data

            rst_widget = self.image_hbox.itemAt(2)
            self.image_hbox.removeItem(rst_widget)
            if rst_widget.widget():
                rst_widget.widget().deleteLater()

            self.result_img_widget = ImageWidget(None,diff_data)
            self.image_hbox.addWidget(self.result_img_widget,1)  

            self.original_img_widget.renderAreaChangedSignal.connect(self.modified_img_widget.renderAreaChanged)
            self.original_img_widget.renderAreaChangedSignal.connect(self.result_img_widget.renderAreaChanged)

            self.modified_img_widget.renderAreaChangedSignal.connect(self.original_img_widget.renderAreaChanged)
            self.modified_img_widget.renderAreaChangedSignal.connect(self.result_img_widget.renderAreaChanged)

            self.result_img_widget.renderAreaChangedSignal.connect(self.original_img_widget.renderAreaChanged)
            self.result_img_widget.renderAreaChangedSignal.connect(self.modified_img_widget.renderAreaChanged)



import sys
from qt_material import apply_stylesheet

if __name__ == "__main__":  
    app = QApplication(sys.argv)  
    apply_stylesheet(app, theme='dark_teal.xml')
    win = MainWindow()  
    win.show()  
    sys.exit(app.exec_())