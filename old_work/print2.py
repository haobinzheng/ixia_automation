import sys
to = 20
digits = len(str(to - 1))
delete = "\b" * (digits)
for i in range(to):
   print("{0}{1:{2}}".format(delete, i, digits), end='')
   sys.stdout.flush()