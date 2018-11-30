import serial
import csv
import datetime
import os.path
#ser = serial.Serial('/dev/ttyUSB0',9600,timeout=10)
CorrectionValue = 0.854983739837398 #補正値


def myfunc():
    if not hasattr(myfunc, "counter"):
        myfunc.counter = 0  # it doesn't exist yet, so initialize it
    myfunc.counter += 1
    return myfunc.counter

def my_index_multi(l, x):
    return [i for i, _x in enumerate(l) if _x == x]

def calculatechksum(p):
  s = 0x00
  for i in range(3, len(p)):
    s += ord(p[i])
  c = 0xFF - (s & 0xFF)
  return chr(c)

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

def CheckStatus(status_hex):
    if status_hex == 0x00:
        status_flg = 0
    
    elif status_hex == 0x01:
        status_flg = 1

    else:
        status_flg = 1
    return status_flg

def demi_SendSerial():
    #コール sned "7E001610010013A20040AE1AC3FFFE000024444D4B3030313FA1"
    cnt = myfunc()
    if cnt == 3:
        respons = "7E00078B0148150000FF16"

    else:
        respons = "7E00078B0148150002FF16"
    return respons

def ReceivePowerData():
    powerdata_str = "7E002410010000000000000000FFFE000024444D4B656530322C30325B3F6F6E30303C3F6F6F2ED9"
    #powerdata_str = "7E002410010000000000000000FFFE000024444D4B656530322C30325B3F6F6E30303C3F6F6F2E"
    powerdata_hex_ls = CreatePacketHexLs(CreatePacketLs(powerdata_str))
    hex_ls_chr=[]
    for tmp in powerdata_hex_ls:
        hex_ls_chr.append(chr(tmp))

    receive_chksum = hex_ls_chr[len(hex_ls_chr)-1]
    chksum = calculatechksum(hex_ls_chr[0:len(hex_ls_chr)-1])

    if chksum == receive_chksum:
        GetPowerData(hex_ls_chr)
    
    else:
        return 0

def GetPowerData(powerdata_ls):

    strData = ''.join(powerdata_ls)

    DelimiterIndex = strData.find(',')
    DIndex_Dollar = strData.rfind('$')
    lastindex = strData.rfind('.')
    XBeesID = strData[DIndex_Dollar+1 : DelimiterIndex]
    CsvList = []

    now = datetime.datetime.now()
    DateHMS = now.strftime("%H%M%S")
    CsvList.append(DateHMS)

    DMKdata_ls = strData[DelimiterIndex+1:lastindex]
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

"""
#string = "7E001610010013A20040AE1AC3FFFE000024444D4B3030313FA1"
string = "7E001610010013A20040AE1AC3FFFE000024444D4B3030313F"

packet_ls = CreatePacketLs(string)
#print(packet_ls)

packet_hex_int_ls = CreatePacketHexLs(packet_ls)
#print(packet_hex_int_ls)
"""

while 1:
    respons_string = demi_SendSerial()

    #respons_string = "7E00078B0148150002FF16"
    respons_ls = CreatePacketHexLs(CreatePacketLs(respons_string))
    status_flg = CheckStatus(respons_ls[len(respons_ls)-3])
    if status_flg == 0:
        val = ReceivePowerData()
        print(val)
        break

    elif status_flg == 1:
        print("error1")

    else:
        print("error2")





"""
str_ls = string[0:]
str_ls_2char = list(zip(*[iter(str_ls)]*2))
print(str_ls_2char)
print(str_ls_2char[0])
"""


"""
hex_ls = []
for tmp in str_ls_2char:
    hex = '0x' + tmp[0]+tmp[1]
    hex_ls.append(hex)

print(hex_ls)

hex_ls_int = [int(s, 16) for s in hex_ls]
print(hex_ls_int)

hex_ls_chr=[]
for tmp in hex_ls_int:
    hex_ls_chr.append(chr(tmp))

print(hex_ls_chr)

chksum = calculatechksum(hex_ls_chr)
hex_ls_chr.append(chksum)
print(hex_ls_chr)
"""