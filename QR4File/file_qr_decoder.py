from tkinter import *
from tkinter import filedialog
import os
import cv2
import zlib
from pyzbar.pyzbar import decode

class QGen:
    def __init__(self,root):
        self.root=root
        self.root.geometry("610x110")
        self.root.title("File QR Decoder")
        self.root.resizable(False,False)

        self.file_dir = StringVar()

        lbl_file_dir = Label(self.root,text="file dir",font=("times new roman",15,'bold'),bg='white').place(x=10,y=10)
        txt_file_dir = Entry(self.root,textvariable=self.file_dir,font=("times new roman",15),bg='white').place(x=100,y=10,width=500,height=30)
        btn_decode = Button(self.root,text='decode',command=self.decode,font=("times new roman",18,'bold'),bg='#2196f3',fg='white').place(x=320,y=60,width=200,height=30)
        btn_select_dir = Button(self.root,text='select dir',command=self.select_dir,font=("times new roman",18,'bold'),bg='#607d8b',fg='white').place(x=70,y=60,width=200,height=30)

    def select_dir(self):
        file_dir = filedialog.askdirectory()
        self.file_dir.set(file_dir)

    def decode(self):
        file_dir = self.file_dir.get()
        input_images = os.listdir(file_dir)

        index_data_dic = {}
        for image_file in input_images:
            img = cv2.imread(file_dir + '/' + image_file)
            decoded = decode(img)
            decoded_data = decoded[0].data.decode('utf-8')

            index = ord(decoded_data[0])
            decoded_data = decoded_data[1:]
            index_data_dic[index] = decoded_data

        keys = sorted(index_data_dic.keys())

        compressed_str = ''
        for index in keys:
            compressed_str = compressed_str + index_data_dic[index]
        compressed_bytes = bytes([ord(c) - 1 for c in compressed_str])

        decompressed_bytes = zlib.decompress(compressed_bytes)
        decompressed_str = decompressed_bytes.decode()

        output_dir = file_dir + '/output'
        os.makedirs(output_dir, exist_ok=True)

        while (len(decompressed_str) > 0):
            index = decompressed_str.find('|')
            file_name = decompressed_str[0:index]
            decompressed_str = decompressed_str[index+1:]

            index = decompressed_str.find('|')
            content_len = int(decompressed_str[0:index])
            decompressed_str = decompressed_str[index+1:]

            content = decompressed_str[0:content_len]
            decompressed_str = decompressed_str[content_len:]

            file = open(output_dir + '/' + file_name, "w")
            file.write(content)
            file.close()

        os.system('start ' + output_dir)    

root = Tk()
o = QGen(root)
root.mainloop()
