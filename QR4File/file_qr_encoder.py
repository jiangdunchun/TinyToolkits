from tkinter import *
from tkinter import filedialog
import qrcode
import os
import zlib
from datetime import datetime

MAX_LEN = 1500

class QGen:
    def __init__(self,root):
        self.root=root
        self.root.geometry("610x410")
        self.root.title("File QR Encoder")
        self.root.resizable(False,False)

        lbl_files = Label(self.root,text="files",font=("times new roman",15,'bold'),bg='white').place(x=10,y=10)
        self.files_text = Text(self.root,font=("times new roman",15),bg='white')
        self.files_text.place(x=60,y=10,width=540,height=330)
        btn_encode = Button(self.root,text='encode',command=self.encode,font=("times new roman",18,'bold'),bg='#2196f3',fg='white').place(x=320,y=360,width=200,height=30)
        btn_add_file = Button(self.root,text='add file',command=self.add_file,font=("times new roman",18,'bold'),bg='#607d8b',fg='white').place(x=70,y=360,width=200,height=30)

    def add_file(self):
        file = filedialog.askopenfilename()
        self.files_text.insert(INSERT,file + '\n')

    def encode(self):
        input_files = filter(None, self.files_text.get("1.0", END).split('\n'))

        decompressed_str = ''
        for file in input_files:
            file_name = os.path.basename(file)
            with open(file) as f_obj:
                content = f_obj.read()
            content_len = len(content)
            decompressed_str += file_name + '|' + str(content_len) + '|' + content
        decompressed_bytes = decompressed_str.encode()

        compressed_bytes = zlib.compress(decompressed_bytes)
        compressed_data = ''
        for b in compressed_bytes:
            compressed_data += chr(b + 1)

        output_dir = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        os.makedirs(output_dir, exist_ok=True)

        index = 1
        while len(compressed_data) > 0:
            split_data = ''
            if len(compressed_data) > MAX_LEN:
                split_data = compressed_data[0:MAX_LEN]
                compressed_data = compressed_data[MAX_LEN:]
            else:
                split_data = compressed_data[0:]
                compressed_data = ''

            split_data = chr(index) + split_data
            qr_code = qrcode.make(split_data)
            qr_code.save(output_dir +"/"+str(index)+'.png')
            index += 1

        os.system('start ' + output_dir)    

root = Tk()
o = QGen(root)
root.mainloop()
