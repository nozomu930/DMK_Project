import serial
import csv
import datetime
import os.path
ser = serial.Serial('/dev/ttyUSB0',9600,timeout=10)
CorrectionValue = 0.854983739837398 #補正値

def myfunc():
    if not hasattr(myfunc, "counter"):
        myfunc.counter = 0  # it doesn't exist yet, so initialize it
    myfunc.counter += 1
    return myfunc.counter

def GetPowerData(strData):
    DelimiterIndex = strData.find('?')
    DIndex_Dollar = strData.rfind('$')
    XBeesID = strData[DIndex_Dollar+1 : DelimiterIndex]
    CsvList = []

    now = datetime.datetime.now()
    DateHMS = now.strftime("%H%M%S")
    #DateHMS = '{0:%H%M%S}'.format(now)
    #counter = myfunc()
    CsvList.append(DateHMS)
    for count in range(0,10,3):
        tmp = strData[DelimiterIndex+(1+count) : DelimiterIndex+(4+count)]
        decrypt1 = ord(tmp[0]) - 48 #(0x30)16 = (48)10
        decrypt2 = (ord(tmp[1]) - 48) & 0x3F
        decrypt3 = (ord(tmp[2]) - 48) & 0x3F

        PowerData = (decrypt1<<12)+(decrypt2<<6)+decrypt3
        if PowerData & 0b1000000000000000 == 32768:
            PowerData = -(PowerData & 0b1000000000000000) | (PowerData & 0b0111111111111111)
        
        PowerData *= CorrectionValue #補正値による電力値の補正計算
        print(PowerData)

        CsvList.append(PowerData)
    #print(tmp)pyth
    WriteCSV(CsvList,XBeesID)

def WriteCSV(CsvList,XBeesID):
    SaveDirectory = '../file/'

    now = datetime.datetime.now()
    DateYMD = '{0:%Y%m%d}'.format(now) #20170910
    CsvFileName = SaveDirectory + "PowerData_" + XBeesID + "_" + DateYMD + ".csv"
    ListFileName = SaveDirectory + "PowerData_List.txt"
    ListValue = XBeesID + "_" + DateYMD + "\n"

    #f = open('../output.csv', 'a')
    if os.path.exists(CsvFileName) == True:
        f = open(CsvFileName, 'a')

    else:
        f = open(CsvFileName,'w')

        #csvファイルのリスト作製用
        f_text = open(ListFileName, 'a')
        f_text.write(ListValue)
        f_text.close()

    writer = csv.writer(f, lineterminator='\n')
    writer.writerow(CsvList)
    f.close()

str =  ""
while 1:
    c = ser.read().decode()
    #print(c)

    if c == '$':
        str = c
        while c != '.':
            c = ser.read().decode()
            str += c
        print(str)
        GetPowerData(str)
        str=""
ser.close()

