import csv
data = {}
inFile = open("/Users/seokyujeon/Desktop/github/cowayRBPI2/examples/config.csv", "rb")

reader = csv.reader(inFile)

for row in reader:
    data[row[0]] = int(row[1])



inFile.close()


print(data)
outFile = open("config.csv", "wb")

writer = csv.writer(outFile)
array = []

array.append(['head', data['head'] + 1])
writer.writerow(array[0])
array.append(['foot', data['foot'] + 1])
writer.writerow(array[1])


outFile.seek(0)

array.append(['head', data['head'] + 2])
writer.writerow(array[2])
array.append(['foot', data['foot'] + 2])
writer.writerow(array[3])





# writer.