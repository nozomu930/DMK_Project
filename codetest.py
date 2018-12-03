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

#引数(ASCII文字のリスト)　例: 適['D','M','K']　不適['0x44','0x4d','0x4b']
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

def ConvertHexlitoCHRli(li):
    hex_li_chr=[]
    for tmp in li:
        hex_li_chr.append(chr(tmp))
    return hex_li_chr

def CreateFrame(address,RFdata):
    #APIフレームデータの初期値
    start_delimiter = "0x7E"
    length_M = "0x00"
    length_L = "0x00"
    frame_type = "0x10"
    frame_id = "0x01"
    destination_address_16bit = ["0xFF","0xFE"]
    broadcast_radius = "0x00"
    options = "0x00"

    #引数のaddressを16進文字列に変換しリスト化する
    address_2chr = list(zip(*[iter(address)]*2))
    destination_address_64bit = []
    for tmp in address_2chr:
        hex_tmp = tmp[0] + tmp[1]
        hex_str = '0x' + hex_tmp
        destination_address_64bit.append(hex_str)

    #引数のRFdataを16進数文字列に変換しリスト化する
    RFdata_li = []
    for tmp in RFdata:
        hex_str = hex(ord(tmp))
        RFdata_li.append(hex_str)   

    #frameの仮結合
    frame_tmp = [frame_type,frame_id] + destination_address_64bit + destination_address_16bit + [broadcast_radius,options] + RFdata_li

    #データ長の計算
    frame_len = hex(len(frame_tmp))
    frame_len = (frame_len[2:]).rjust(4,'0')
    length_M = '0x' + frame_len[0] + frame_len[1]
    length_L = '0x' + frame_len[2] + frame_len[3]

    #データ長(下位)、データ長(上位)、開始コードの順にリストに追加
    frame_tmp.insert(0,length_L)
    frame_tmp.insert(0,length_M)
    frame_tmp.insert(0,start_delimiter)

    #チェックサムの計算
    frame_tmp_int = [int(s, 16) for s in frame_tmp]
    chksum = hex(ord(calculatechksum(ConvertHexlitoCHRli(frame_tmp_int))))
    frame_tmp.append(chksum)

    return frame_tmp

def CreateDMKDictionary(csv_url):
    #csvファイルの読み込み
    dic = {}
    with open(csv_url,"r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            dic[row['name']] = row['address']
    return dic



DMK_dictionary = CreateDMKDictionary("config/DMKModuleList.csv")

frame = CreateFrame(DMK_dictionary['DMKEE01'],'#DMKEE01?')
print(frame)
frame = CreateFrame(DMK_dictionary['DMKEE02'],'#DMKEE02?')
print(frame)

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
#string = "7E001610010013A20040AE1AC3FFFE000024444D4B3030313FA1"
string = "7E001610010013A20040AE1AC3FFFE000024444D4B3030313F"

packet_ls = CreatePacketLs(string)
#print(packet_ls)

packet_hex_int_ls = CreatePacketHexLs(packet_ls)
#print(packet_hex_int_ls)
"""

#DMK_li = ['DMKEE01','0013A20040AE1AC3','DMKEE02','0013A20040AE1ABB']
#DMK_li = {'DMKEE01':'0013A20040AE1AC3','DMKEE02':'0013A20040AE1ABB'}
#DMK_module_li = list(zip(*[iter(DMK_li)]*2))
#print(DMK_li['DMKEE01'])

"""
#csvファイルの読み込み
DMK_dictionary = {}
with open("config/DMKModuleList.csv","r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        DMK_dictionary[row['name']] = row['address']
"""

"""
frame = CreateFrame(DMK_module_li[0][1],'#DMKEE01?')
print(frame)
frame = CreateFrame(DMK_module_li[1][1],'#DMKEE02?')
print(frame)
"""


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