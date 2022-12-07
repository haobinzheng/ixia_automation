import paramiko
import time
import utils 

def ssh(ip,password,username="admin"):
	port = 22
	try:
		ssh = paramiko.SSHClient()  # ??ssh??
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=ip, port=int(port), username=username, password=password)
		return ("Success",ssh)
	except Exception as e:
		error = "???????,{}".format(e)
		ret = {"ip": ip, "data": error}
		return ("Failed",ret)

def ssh_cmd(ssh,cmd,*args,**kwargs):
	if "timeout" in kwargs:
		t = kwargs['timeout']
	else:
		t = 10
	try:
		stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t)
		result = stdout.read()
		result1 = result.decode()
		error = stderr.read().decode('utf-8')

		if not error:
		    ret = {"data":result1}
		    return ("Success",ret)
	except Exception as e:
		error = "???????,{}".format(e)
		ret = {"data": error}
		return ("Failed",ret)

def ssh_interactive_exec(ssh,exec_cmd,*args, **kwargs):
	#relogin_if_needed(tn)
	if "enter_y" in kwargs:
		enter_y = kwargs['enter_y']
	else:
		enter_y = 'y'
	utils.tprint(exec_cmd)
	exec_cmd = exec_cmd + "\n" + enter_y
	result = ssh_cmd(ssh,exec_cmd,timeout=40)
	print(f"in ssh_interactive_exec, output of {exec_cmd}: {result}")
	time.sleep(2)
	return result
	 

def process_ssh_output(output):
	print(output[1]['data'])
	out_list = output[1]['data'].split('\n')
	encoding = 'utf-8'
	out_str_list = [o for o in out_list if o != ''] 
	return out_str_list


def close_ssh(ssh):
	 ssh.close()

if __name__ == "__main__":
	result = ssh("10.105.241.28","Fortinet123!") 
	if result[0] == "Success":
		ssh_handle = result[1]
	output = ssh_cmd(ssh_handle,"get system status")
	output_list = process_ssh_output(output)
	print (output_list)