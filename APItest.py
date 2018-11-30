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
    lastindex = strData.rfind('.')
    XBeesID = strData[DIndex_Dollar+1 : DelimiterIndex]
    CsvList = []

    now = datetime.datetime.now()
    DateHMS = now.strftime("%H%M%S")
    #DateHMS = '{0:%H%M%S}'.format(now)
    #counter = myfunc()
    CsvList.append(DateHMS)

    DMKdata_ls = strData[DelimiterIndex+1:]
    DMKdata_ls_3char = list(zip(*[iter(DMKdata_ls)]*3))
    print(DMKdata_ls_3char)

    for tmp in DMKdata_ls_3char:
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

def CheckStatus(status_hex):
    if status_hex == 0x00:
        status_flg = 0
    
    elif status_hex == 0x01:
        status_flg = 1

    else:
        status_flg = 1
    return status_flg

def CreatePacketLs(s):
    str_ls = s[0:]
    str_ls_2char = list(zip(*[iter(str_ls)]*2))
    return str_ls_2char

def CreatePacketHexLs(p_ls):
    hex_ls = []
    for tmp in p_ls:
        hex = '0x' + tmp[0]+tmp[1]
        hex_ls.append(hex)

    hex_ls_int = [int(s, 16) for s in hex_ls]
    return hex_ls_int



str =  ""
while 1:
    ser.write("7E 00 16 10 01 00 13 A2 00 40 AE 1A C3 FF FE 00 00 24 44 4D 4B 30 30 31 3F A1") 
    c = ser.readline()
    respons_ls = CreatePacketLs(c)
    respons_hex_ls = CreatePacketHexLs(CreatePacketLs(respons_ls))
    status_flg = CheckStatus(respons_hex_ls[len(respons_ls)-3])



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

