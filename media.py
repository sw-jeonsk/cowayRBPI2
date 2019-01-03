import os
import constant
from tkinter import *
from tkinter import ttk


class media:

    def __init__(self):
        self.m_idle = constant.IDLE
        self.m_bedtime = constant.BEDTIME
        self.m_align = constant.ALIGNMENT
        self.m_wakeup = constant.WAKEUP


        self.m_TkRoot = Tk()
        self.m_TkFrame = Frame(self.m_TkRoot)
        self.m_TkRoot.attributes("-fullscreen", True)   

        self.m_TkRoot.bind("<Escape>", quit)
        self.m_TkRoot.bind("x", quit)

        self.m_TkFrame.pack()
        self.m_TkRoot.mainloop()

    def quit(self, *args):
        print("QUIT---------------------")
        self.m_TkRoot.destroy()



    def IDLE(self):

        os.system('omxplayer --loop --aspect-mode fill ' + self.m_idle + " &")

    def BEDTIME(self):
        os.system('omxplayer  --aspect-mode fill ' + self.m_bedtime + " &")
    def ALIGN(self):
        os.system('omxplayer  --aspect-mode fill ' + self.m_align + " &")
    def WAKEUP(self):
        os.system('omxplayer  --aspect-mode fill ' + self.m_wakeup + " &")

    def KILL(self):
        os.system("pkill -f 'omxplayer*'")

