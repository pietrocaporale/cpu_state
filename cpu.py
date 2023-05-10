import sys
import os
import psutil
import tkinter as tk
import time
import traceback
import threading
from file_init import fileInit
from wininfo import winInfo

""" Parameters. """
WIN_PARAM = "35,0,0"
SENSUSE = ""
SENSSTR = "perc,freq,temp"
TERMPRT = False
REFRESH_PERIOD = 1
lastClickX = 0
lastClickY = 0
openInfo = False
infoWin = object

# CORES: int = psutil.cpu_count(logical=False) or 1
THREADS: int = psutil.cpu_count(logical=True) or 1

psu = psutil


def reload_script():
    """ Function reload script to update all new parameters. """
    os.execl(sys.executable, sys.executable, *sys.argv)


def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y


class rootCpu():
    def __init__(self):
        global WIN_PARAM, SENSUSE, SENSSTR
        self.width_bar = 20
        self.showContinuos = True
        LIST_INIT = WIN_PARAM + "\n" + SENSSTR
        self.fi = fileInit(".init", LIST_INIT)
        param = self.fi.readInit()
        if len(param) > 0:
            WIN_PARAM = param[0]
            SENSSTR = param[1]
            SENSUSE = SENSSTR.split(",")
        self.args = WIN_PARAM.split(",")
        self.root = tk.Tk()
        self.root.configure(bg='blue')
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.title("fCpu")
        self.root.bind('<Button-1>', self.SaveLastClickPos)
        self.root.bind('<B1-Motion>', self.Dragging)
        self.setWindowPos()

    def create(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.perc_col1 = "green"
        self.perc_col2 = "red"
        self.freq_col1 = "orange"
        self.freq_col2 = "red"
        self.temp_col1 = "blue"
        self.temp_col2 = "red"
        for sens in SENSUSE:
            if sens == "perc":
                self.my_canvas = tk.Canvas(self.frame, borderwidth=1, width=int(self.args[0]), bg="black")
                self.my_canvas.pack(side=tk.LEFT, fill="x", expand=0)
            elif sens == "freq":
                self.my_canvas2 = tk.Canvas(self.frame, borderwidth=1, width=int(self.args[0]), bg="black")
                self.my_canvas2.pack(side=tk.LEFT, fill="x", expand=0)
            elif sens == "temp":
                self.my_canvas3 = tk.Canvas(self.frame, borderwidth=1, width=int(self.args[0]), bg="black")
                self.my_canvas3.pack(side=tk.LEFT, fill="x", expand=0)

        self.root.bind('<Button-2>', self.reload_script)
        self.root.bind('<Button-3>', self.closeApp)
        self.root.mainloop()

    def reload_script(self, event):
        reload_script()

    def getWinVal(self, sens):
        """ get cpu values """
        if sens == "perc":
            x_typ = "Perc"
            x_val = str(int(self.perc))+"%"
        elif sens == "freq":
            x_typ = "Freq"
            x_val = str(int(self.freq))
        elif sens == "temp":
            x_typ = "Temp"
            x_val = str(int(self.temp))+"°"
        return x_typ, x_val

    def openWinfo(self, event):
        """ Open info panel """
        global openInfo
        global infoWin
        if event.widget._name == "!canvas":
            x_typ, x_val = self.getWinVal(SENSUSE[0])
        elif event.widget._name == "!canvas2":
            x_typ, x_val = self.getWinVal(SENSUSE[1])
        elif event.widget._name == "!canvas3":
            x_typ, x_val = self.getWinVal(SENSUSE[2])

        openInfo = True
        infoWin = winInfo(event.widget._name, x_typ, x_val, len(SENSUSE))
        infoWin.create()

    def closeWinfo(self, event):
        """ Close info panel """
        global openInfo
        global infoWin
        if openInfo is True:
            try:
                infoWin.root.destroy()
            except tk.TclError:
                pass
            openInfo = False

    def draw_res(self, my_canvas, in_val, delta, _color1, _color2, sens):
        """ Draw cpu windows"""
        my_canvas.delete("gradient")
        width = my_canvas.winfo_width()
        height = my_canvas.winfo_height()
        limit = height
        (r1, g1, b1) = my_canvas.winfo_rgb(_color1)
        (r2, g2, b2) = my_canvas.winfo_rgb(_color2)
        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit

        color_line = []
        for ii in range(int(limit)):
            i = limit - ii  # second color up
            # i = ii  # second color down
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
            color_line.append(color)

        _delta = delta
        _out_eq = in_val*limit/_delta
        out_eq = _out_eq
        if out_eq < 1 and in_val > 0:
            out_eq = 2
        start_draw = limit - out_eq - 1
        # _in_eq = in_val * 100 / _delta
        # print("in_val %.2f (%.2f) out_eq %.0f (%.2f) start_draw %.0f delta %.0f " % (in_val, _in_eq, out_eq, _out_eq, start_draw, _delta))
        if TERMPRT is True:
            print(" " + sens+" %.2f " % (in_val))
        for ii in range(int(limit)):
            if ii > start_draw:
                i = ii - 1
                my_canvas.create_line(0, i, width, i, tags=("gradient",), fill=color_line[ii])
        my_canvas.lower("gradient")
        my_canvas.bind('<Enter>', self.openWinfo)
        my_canvas.bind('<Leave>', self.closeWinfo)

    def refresh(self):
        """ Main refresh call """
        if self.showContinuos is False:
            return
        for sens in SENSUSE:
            if sens == "perc":
                self.perc, self.deltaPerc = get_cpu_percent()
                self.draw_res(self.my_canvas, self.perc, self.deltaPerc, self.perc_col1, self.perc_col2, sens)
            elif sens == "freq":
                self.freq, self.deltaFreq = get_cpu_freq("current", 0)
                self.draw_res(self.my_canvas2, self.freq, self.deltaFreq, self.freq_col1, self.freq_col2, sens)
            elif sens == "temp":
                self.temp, self.deltaTemp = get_cpu_temp("current", 0)
                self.draw_res(self.my_canvas3, self.temp, self.deltaTemp, self.temp_col1, self.temp_col2, sens)

    def SaveLastClickPos(self, event):
        global lastClickX, lastClickY
        lastClickX = event.x
        lastClickY = event.y

    def Dragging(self, event):
        """ On move event """
        global SENSSTR
        x, y = event.x - lastClickX + self.root.winfo_x(), event.y - lastClickY + self.root.winfo_y()
        self.root.geometry("+%s+%s" % (x, y))
        self.fi.writeInit(self.getWindowPos() + "\n" + SENSSTR)

    def getWindowPos(self):
        """ Get window position values """
        t = []
        t.append(self.root.winfo_height())
        t.append(self.root.winfo_x())
        t.append(self.root.winfo_y())
        win_pos = str(t[0])+","+str(t[1])+","+str(t[2])
        return win_pos

    def setWindowPos(self):
        """ Set window position """
        args = self.args
        width_win = (int(args[0])+4)*len(SENSUSE)  # 35
        height_win = int(args[0])
        if int(args[2]) == 0 and int(args[2]) == 0:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            center_x = int(screen_width / 2 - height_win / 2)
            center_y = int(screen_height / 2 - int(args[1]) / 2)
            self.root.geometry(f"{width_win}x{height_win}+{center_x}+{center_y}")
        else:
            self.root.geometry(f"{width_win}x{height_win}+{int(args[1])}+{int(args[2])}")

    def closeApp(self, event):
        if hasattr(self, 'hwin'):
            self.hwin.window.destroy()
        self.root.destroy()
        os._exit(0)


def every(delay, task):
    """ Refresh loop """
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()
            # in production code you might want to have this instead of course:
            # logger.exception("Problem while executing repetitive task.")
        # skip tasks if we are behind schedule:
        next_time += (time.time() - next_time) // delay * delay + delay


def update():
    app.refresh()


threading.Thread(target=lambda: every(REFRESH_PERIOD, update)).start()


def get_cpu_freq(type="current", sh=False):
    """ Get cpu frequence """
    res = 0
    freq = psu.cpu_freq()
    if not freq:
        sys.exit("can't read any frequence")
    if type == "current":
        res = freq[0]
    elif type == "min":
        res = freq[1]
    elif type == "max":
        res = freq[2]
    else:
        res = "None"
    if sh:
        print("%s %.0f , min= %.0f, max= %.0f" % (
            "CPU frequence ", freq[0], freq[1], freq[2]))
    delta = freq[1] + freq[2]
    return res, delta


def get_cpu_percent(sh=False):
    """ Get cpu usage in % """
    res = psu.cpu_percent(interval=None, percpu=False)
    if not res:
        sys.exit("can't read any percent")
    if sh:
        print("%s %s%s " % (
            "CPU usage ", res, "%"))
    delta = 100
    return res, delta


def get_cpu_temp(type="current", sh=False):
    """ Get cpu temperature """
    res = 0
    temps = psu.sensors_temperatures()
    if temps:
        for name, entries in temps.items():
            if name == "coretemp":
                for entry in entries:
                    if entry.label == "Package id 0":
                        if type == "current":
                            temp = entry.current
                            break
                        elif type == "high":
                            temp = entry.high
                            break
                        elif type == "critical":
                            temp = entry.critical
                            break
                        else:
                            temp = "None"
                            break
        res = temp
        if sh:
            print("%s %s °C (high = %s °C, critical = %s °C)" % (
                "CPU temperature ", entry.current, entry.high,
                entry.critical))
        delta = entry.critical
    return res, delta


app = rootCpu()
app.create()
