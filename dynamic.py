#Given a list of integers and another integer Y, find all subset of the list that add up to Y.  For example, array = [1,2,-1,5,10,22,5,8,-3], Y = 5
a = [1,2,-1,5,10,22,5,8,-3]
Y=5

# size == 1: [1] [2] [-1] [5] [10] [22] [5] [8] [-3]
# size ==2:  [1,2] [1,-1] [1,5] [1,10] [1,22] ....
#            [2,-1] [2,5] [2,10] [2,22] [2,5]....
# size ==3: 

array = [1,2,-1,5,10,22,8,-3]

def sublist(array):
    if len(array) == 0:
        return [[]]
    final = []
    first = array[0]
    rest = array[1:]
    temp = sublist(rest)
    for i in temp:
        final.append([first] + i)
    final.extend(temp)
    return final

subs = sublist(array)
for sub in subs:
    if sum(sub) == 5:
        print(sub)         