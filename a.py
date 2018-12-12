import csv

def CreateDMKDictionary(csv_url):
    #csvファイルの読み込み
    dic = {}
    with open(csv_url,"r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            dic[row['name']] = row['address']
    return dic

DMK_dictionary = CreateDMKDictionary("config/DMKModuleList.csv")
for tmp in DMK_dictionary:
    print(tmp)
    print(DMK_dictionary[tmp])
    remote_address = DMK_dictionary[tmp]
    call_message = '#' + tmp + '?'

    print(call_message)

print(DMK_dictionary)
