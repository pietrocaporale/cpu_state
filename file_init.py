import os
import sys


class fileInit:
    """ Class to create and read line value from text init file """

    def __init__(self, file_name, init_param):
        self.INIT_FILE = file_name
        self.INIT_PARAM = init_param

    def readInit(self):
        """ Function to read init param.

            window position (not resize)
        """
        # if exist read init
        paramList = []
        if os.path.exists(self.INIT_FILE):
            file1 = open(self.INIT_FILE, "r")
            with open(self.INIT_FILE, "r") as file1:
                for line in file1:
                    line = line.replace("\n", "")
                    paramList.append(line)
                file1.close()
            return paramList
        else:
            # if not exist write init
            self.writeInit(self.INIT_PARAM)
            paramList = self.readInit()
            return paramList

    def writeInit(self, winParam):
        """ Function to update init file. """
        file1 = open(self.INIT_FILE, "w")
        file1.writelines(winParam)
        file1.close()

    def delInitLine(self, line_selected, with_reload):
        """ Function to remove line from init file

            If with_reload is True, reload script.
        """
        with open(self.INIT_FILE, "r") as f:
            lines = f.readlines()
            with open(self.INIT_FILE, "w") as new_f:
                for line in lines:
                    if not line.startswith(line_selected):
                        new_f.write(line)
        self.writeInit(os.getcwd())
        if with_reload is True:
            self.reload_script()

    def reload_script():
        """ Function reload script to update all new parameters. """
        os.execl(sys.executable, sys.executable, *sys.argv)
