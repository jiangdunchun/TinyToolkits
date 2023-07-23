from tkinter import *
from tkinter import filedialog
from resizeimage import resizeimage
import qrcode
import os
from datetime import datetime

MAX_LEN = 2000

class QGen:
    def __init__(self,root):
        self.root=root
        self.root.geometry("610x110")
        self.root.title("QR Code Generator")
        self.root.resizable(False,False)

        self.file_dir=StringVar()


        lbl_file_dir=Label(self.root,text="file path",font=("times new roman",15,'bold'),bg='white').place(x=10,y=10)
        txt_file_dir=Entry(self.root,textvariable=self.file_dir,font=("times new roman",15),bg='white').place(x=100,y=10,width=500,height=30)

        btn_gen=Button(self.root,text='generate',command=self.generate,font=("times new roman",18,'bold'),bg='#2196f3',fg='white').place(x=320,y=60,width=200,height=30)
        btn_clr=Button(self.root,text='select file',command=self.select,font=("times new roman",18,'bold'),bg='#607d8b',fg='white').place(x=70,y=60,width=200,height=30)

    def select(self):
        file_dir = filedialog.askopenfilename()
        self.file_dir.set(file_dir)

    def generate(self):
        folder_dir = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        os.makedirs(folder_dir, exist_ok=True)

        file_dir = self.file_dir.get()

        with open(file_dir) as file_obj:
            file_data = file_obj.read()
            
        index = 0
        while len(file_data) > 0:
            split_data = ''
            if len(file_data) > MAX_LEN:
                split_data = file_data[0:MAX_LEN]
                file_data = file_data[MAX_LEN:]
            else:
                split_data = file_data[0:]
                file_data = ''

            qr_code = qrcode.make(split_data)
            qr_code = resizeimage.resize_cover(qr_code,[500,500])
            qr_code.save(folder_dir +"/"+str(index)+'.png')
            index += 1

        os.system('start ' + folder_dir)

root=Tk()
o=QGen(root)
root.mainloop()