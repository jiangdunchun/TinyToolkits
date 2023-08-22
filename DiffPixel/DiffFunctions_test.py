import numpy as np
import sys
import cv2

if __name__ == '__main__':  
    DiffFunctions = {}

    with open('DiffFunctions.py', 'r') as diff_functions_file:
        diff_functions_code = diff_functions_file.read()
    print(diff_functions_code)

    exec(diff_functions_code)

    #diff_func = DiffFunctions[sys.argv[1]]
    diff_func = DiffFunctions['ColorDistance']

    if diff_func != None:
        img_1 = cv2.imread('test/original/1.png')
        img_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2RGB)

        img_2 = cv2.imread('test/bc1/1.png')
        img_2 = cv2.cvtColor(img_2, cv2.COLOR_BGR2RGB)

        diff = diff_func(img_1, img_2)
        print(diff)
    