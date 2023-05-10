import tkinter as tk
from file_init import fileInit

WIN_PARAM = "35,0,0"


class winInfo():
    """ Class of information window """

    def __init__(self, canvas_name, x_typ, x_val, q_sens):
        global WIN_PARAM
        self.fi = fileInit(".init", WIN_PARAM)
        param = self.fi.readInit()
        if len(param) > 0:
            WIN_PARAM = param[0]
        self.args = WIN_PARAM.split(",")
        root = tk.Tk()
        root.configure(bg='black')
        # self.root['bg']='black'
        self.canvas_name = canvas_name
        self.x_typ = x_typ
        self.x_val = x_val
        self.q_sens = q_sens
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.option_add("*font", "Inconsolata 10 normal roman")
        if int(self.args[0]) < 35:
            root.option_add("*font", "Inconsolata 8 normal roman")
        self.root = root
        self.setWindowPos()

    def create(self):
        self.label_val = tk.Label(self.root, bg="black", fg='#fff',
                                  text=self.x_typ+"\n"+self.x_val)
        self.label_val.grid(column=0, sticky="WE")
        self.root.mainloop()

    def setWindowPos(self):
        """ Set window position """
        w_canvas, h_canvas, pos_x, pos_y = self.getCanvasPos()
        self.root.geometry(f"{w_canvas}x{h_canvas}+{pos_x}+{pos_y}")

    def getCanvasPos(self):
        add_h = 3
        args = self.args
        w_canvas = (int(args[0])+4)
        h_canvas = int(args[0])+add_h
        pos_y = int(args[2])
        if self.canvas_name == "!canvas":
            pos_x = int(args[1])
        elif self.canvas_name == "!canvas2":
            pos_x = int(args[1])+w_canvas
        elif self.canvas_name == "!canvas3":
            pos_x = int(args[1])+(w_canvas*2)
        else:
            print("none")
        pos_y = pos_y - (h_canvas)
        return w_canvas, h_canvas, pos_x, pos_y
