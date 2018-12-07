import serial
import csv
import datetime
import os.path
from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.devices import XBee64BitAddress
from digi.xbee.devices import ZigBeeDevice
from digi.xbee.devices import XBeeMessage

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
# Open serial port
device = XBeeDevice(PORT,BAUD_RATE)
#device = ZigBeeDevice(PORT, BAUD_RATE)

CorrectionValue = 0.854983739837398 #補正値

#引数(ASCII文字のリスト)　例: 適['D','M','K']　不適['0x44','0x4d','0x4b']
def calculatechksum(p):
  s = 0x00
  for i in range(3, len(p)):
    s += ord(p[i])
  c = 0xFF - (s & 0xFF)
  return chr(c)

def CreateDMKDictionary(csv_url):
    #csvファイルの読み込み
    dic = {}
    with open(csv_url,"r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            dic[row['name']] = row['address']
    return dic

def GetPowerData(strData):
    DelimiterIndex = strData.find(',')
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
    #WriteCSV(CsvList,XBeesID)
    return CsvList

def main():
    try:
        device.open()
        print("Device is opened")

        DMK_dictionary = CreateDMKDictionary("config/DMKModuleList.csv")
        #frame = CreateFrame(DMK_dictionary['DMKEE01'],'#DMKEE01?')
        #print(frame)

        # Instantiate a remote XBee device object.
        remote_device = RemoteXBeeDevice(device,XBee64BitAddress.from_hex_string(DMK_dictionary['DMKEE01']))

        if remote_device is None:
            print("Could not find the remote local_xbee")
            exit(1)

        #ブロードキャストで送る場合
        #device.send_data_broadcast("Hello XBee World!")

        # Send data using the remote object.
        device.send_data(remote_device, "#DMKEE01?")
        print("Send success")

        while True:   
            # Read data.
            xbee_message = device.read_data(None)
            if xbee_message is not None:
                #remote_device = xbee_message.remote_device
                data = xbee_message.data
                is_broadcast = xbee_message.is_broadcast
                timestamp = xbee_message.timestamp
                print(data.decode())
                li = GetPowerData(data.decode())
                print(li)
                break

    finally:
        if device is not None and device.is_open():
            device.close()
            print("Device is closed")

if __name__ == '__main__':
    main()




"""
DATA_TO_SEND = "Hello!"

SOURCE_ENDPOINT = 0xA0
DESTINATION_ENDPOINT = 0xA1
CLUSTER_ID = 0x1554
PROFILE_ID = 0x1234

#print("Sending explicit data to %s >> %s..." % (remote_device.get_64bit_addr(), DATA_TO_SEND))

# Send explicit data using the remote object.
device.send_expl_data(remote_device, DATA_TO_SEND, SOURCE_ENDPOINT,
                        DESTINATION_ENDPOINT, CLUSTER_ID, PROFILE_ID)
"""