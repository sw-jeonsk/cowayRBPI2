import os
import constant

class media:

    def __init__(self):
        self.m_idle = constant.IDLE
        self.m_bedtime = constant.BEDTIME
        self.m_align = constant.ALIGNMENT
        self.m_wakeup = constant.WAKEUP


    def IDLE(self):

        os.system('omxplayer --loop --aspect-mode fill ' + self.m_idle + " &")

    def BEDTIME(self):
        os.system('omxplayer  --aspect-mode fill ' + self.m_bedtime + " &")

    def WAKEUP(self):
        os.system('omxplayer  --aspect-mode fill ' + self.m_wakeup + " &")

    def KILL(self):
        os.system("pkill -f 'omxplayer*'")

