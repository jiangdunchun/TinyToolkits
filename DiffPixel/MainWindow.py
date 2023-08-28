from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ImageWidgetFile import *
from OpenPathWidget import *
import cv2
    
class MainWindow(QWidget):  
    def __init__(self, diff_functions):  
        super().__init__()
        self.setWindowTitle("DiffPixel")
        self.diff_functions = diff_functions

        self.original_img_widget = None
        self.modified_img_widget = None

        main_vbox = QVBoxLayout()
        self.setLayout(main_vbox)

        self.image_hbox = QHBoxLayout()
        main_vbox.addLayout(self.image_hbox,1)

        self.original_widget = ImageWidget(None,True)
        self.original_widget.renderAreaChangedSignal.connect(self.reader_area_changed)
        self.original_widget.ImgLoadedSignal.connect(self.img_loaded)
        self.image_hbox.addWidget(self.original_widget,1)

        self.modified_widget = ImageWidget(None,True)
        self.modified_widget.renderAreaChangedSignal.connect(self.reader_area_changed)
        self.modified_widget.ImgLoadedSignal.connect(self.img_loaded)
        self.image_hbox.addWidget(self.modified_widget,1)

        self.result_widget = ImageWidget(None,False)
        self.result_widget.renderAreaChangedSignal.connect(self.reader_area_changed)
        self.image_hbox.addWidget(self.result_widget,1)

        setting_hbox = QHBoxLayout()
        main_vbox.addLayout(setting_hbox,0)

        self.diff_func_combo_box = QComboBox()
        self.diff_func_combo_box.addItems(self.diff_functions.keys())
        setting_hbox.addWidget(self.diff_func_combo_box,0)

        setting_h_spacer = QSpacerItem(700,13,QSizePolicy.Expanding,QSizePolicy.Minimum)
        setting_hbox.addItem(setting_h_spacer)

        save_button = QPushButton()
        setting_hbox.addWidget(save_button,0)

    def reader_area_changed(self, render_area):
        area = np.array(render_area)
        self.original_widget.SetRenderArea(area)
        self.modified_widget.SetRenderArea(area)
        self.result_widget.SetRenderArea(area)

    def img_loaded(self):
        if self.original_widget.HasImg() and self.modified_widget.HasImg():
            diff_func = self.diff_functions[self.diff_func_combo_box.currentText()]
            diff_data = diff_func(self.original_widget.GetImgData(), self.modified_widget.GetImgData())
            self.result_widget.SetImgData(diff_data)
            self.result_widget.SetDiffDataRange(0.0,10.0)



import sys
from qt_material import apply_stylesheet

if __name__ == "__main__":  
    DiffFunctions = {}
    with open('DiffFunctions.py', 'r') as diff_functions_file:
        diff_functions_code = diff_functions_file.read()
    exec(diff_functions_code)

    app = QApplication(sys.argv)  
    apply_stylesheet(app, theme='dark_teal.xml')
    window = MainWindow(DiffFunctions)
    window.showMaximized()
    window.show()  
    sys.exit(app.exec_())