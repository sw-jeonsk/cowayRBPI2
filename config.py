import csv
import constant

class config:
    def __init__(self):

        ReadFile = open(constant.CONFIGPATH, "rb")
        reader = csv.reader(ReadFile)

        for row in reader:
            if (row[0] == 'head'):
                constant.headValue = int(row[1])
            else:
                constant.feetValue = int(row[1])    



        ReadFile.close()  

        self.m_Write = open(constant.CONFIGPATH, "wb")

        self.m_Writer = csv.writer(self.m_Write)

        self.m_Write.seek(0)
