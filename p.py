import re
import csv

nums = []


with open ("mld.txt","r") as f:
	lines = f.readlines()
	for l in lines:
		if "#" in l:
			continue
		matched = re.search(r'\| ([0-9]+) \|',l)
		if matched:
			n = matched.group(1)
			nums.append(n)
	#print(nums)
	num_dict = {}
	for i in nums:
		num_dict[i] = num_dict.setdefault(i,0) + 1

	#print(num_dict)
	print("================ cases with duplcated tags ============")
	for k,v in num_dict.items():
		if int(v) > 1:
			print(k,v)


oriel_cases = []
with open('mld.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    for row in reader:
        #print(row)
        oriel_cases.append(row[1])
    oriel_cases.pop(0)
    #print(oriel_cases)

cases_dict = {}
for i in oriel_cases:
	cases_dict[i] = cases_dict.setdefault(i,0) + 1

#print(cases_dict)

set1 = set(num_dict.items())
set2 = set(cases_dict.items())

#print( set1 ^ set2)

print("======================== oriel cases not being used =================")
print (set(nums) ^ set(oriel_cases))
