def increment_24(ip,num):
	bytes = ip.split('.')
	ibytes = [int(i) for i in bytes]
	newip_list = []
	for i in range(num):
		ibytes[2] += 1
		if ibytes[2] > 255:
			ibytes[1] += 1
			ibytes[2] = 0
			if ibytes[1] > 255:
				ibytes[0]+= 1
				ibytes[1] = 0
				if ibytes[0] > 224:
					print("The range is too big for IPv4")
					return newip_list
		newip = ".".join(str(i) for i in ibytes)
		print(newip)
	return newip_list