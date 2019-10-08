import paramiko
import time

def ssh(ip,username,password,cmd):
	port = 22
	try:
		ssh = paramiko.SSHClient()  # ??ssh??
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=ip, port=int(port), username=username, password=password, )
		stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
		result = stdout.read()
		result1 = result.decode()
		error = stderr.read().decode('utf-8')

		if not error:
		    ret = {"ip":ip,"data":result1}
		    ssh.close()
		    return ("Success",ret)
	except Exception as e:
		error = "???????,{}".format(e)
		ret = {"ip": ip, "data": error}
		return ("Failed",ret)

if __name__ == "__main__":
	result = ssh("10.105.50.59","admin","admin","get system status") 
	print (result)