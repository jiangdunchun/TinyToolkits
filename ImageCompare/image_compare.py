from tkinter import *

root = Tk()
root.title("Image Compare")

main_window = PanedWindow(orient='vertical')
main_window.pack(fill='both',expand=True)

top_panel = PanedWindow(main_window,orient='horizontal')
top_panel.pack(fill='both',expand=True)
main_window.add(top_panel)

top_left_frame = LabelFrame(top_panel,text='Left',width=400,height=400)
top_panel.add(top_left_frame)

top_right_frame = LabelFrame(top_panel,text='Right',width=400,height=400)
top_panel.add(top_right_frame)

bottom_panel = PanedWindow(main_window,orient='horizontal')
bottom_panel.pack(fill='both',expand=True)
main_window.add(bottom_panel)

bottom_left_frame = LabelFrame(bottom_panel,text='Result',width=400,height=400)
bottom_panel.add(bottom_left_frame)

bottom_right_frame = LabelFrame(bottom_panel,text='Setting',width=400,height=400)
bottom_panel.add(bottom_right_frame)

mainloop()