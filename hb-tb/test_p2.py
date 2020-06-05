from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

def testing(*args,**kwargs):
    name = args[0]
    age = kwargs["age"]
    print("testing")
    print("testing name = {},age={}".format(name,age))

    b = {"name":"mike","age":14,"location":"china"}
    a = "mike"
    print("{} is a good man".format(a))

    for k,v in b.items():
        print(k,v)

if __name__ == "__main__":
    testing("steve",age=30)
