import requests
import os
import shutil
import datetime
import random
import json

class MyError(Exception):
    def __str__(self):
        return "get_parking error"

def post_common(ip, sub_url, data):
	headers = {'Authorization': 'Basic YWRtaW46cDAxMjM0', 'Connection': 'Keep-Alive', 'Cache-Control': 'no-store'}
	url ='http://' + ip + sub_url
	try:
		response = requests.post(url, data=data, headers=headers, timeout=6)
		return response.text
	except:
		print(url + ": server error")
		raise MyError()	

def post_common_nodata(ip, sub_url):
	headers = {'Authorization': 'Basic YWRtaW46cDAxMjM0', 'Connection': 'Keep-Alive', 'Cache-Control': 'no-store'}
	url ='http://' + ip + sub_url
	try:
		response = requests.post(url, headers=headers, timeout=6)
		return response.text
	except:
		print(url + ": server error")
		raise MyError()

def get_common(ip, sub_url):
	url ='http://' + ip + sub_url
	headers = {'Authorization': 'Basic YWRtaW46cDAxMjM0', 'Connection': 'Keep-Alive', 'Cache-Control': 'no-store'}	
	try:
		response = requests.get(url, headers=headers, timeout=6)
		if response.status_code == 200:
			#print(ip + " : " + response.text);
			return response.text
		else:
			print(ip + url + ": server error")
			raise MyError()
	except requests.exceptions.ConnectionError as e:
		print(url + ": connect error")
		raise MyError()
	except:
		print(url + ": server error")
		raise MyError() 

def getIpList(args):
	print(args)
	ip_list = []
	bFile = False
	if len(args) == 1:	#192.168.10.123 or connectlist.txt
		print("args=1 in default_module")
		if os.path.isfile(args[0]):
			print("args is file in default_module")
			bFile = True
		else:
			ip_list.append(args[0])
			return ip_list
	elif len(args) >= 2:
		print("args>=2 in default_module")
		ipAddr = args[0].split(".")
		if len(ipAddr) == 4: # 192.168.10.123 150
			endip = args[1]
			postRange = range(int(ipAddr[3]), int(endip)+1)
		elif len(ipAddr) == 3: # 192.168.10 123 124 155
			postRange = args[1:]
	else :
		print('wrong argument')
		exit()
		
	if bFile:
		f=open(args[0], 'r')
		while 1 :
			line=f.readline()
			if not line:
				break
			if "=" in line: #list=192.168.10.0~100,192.168.11.0~100
				whole_ips = line.split("=") #[list, 192.168.10.0~100,192.168.11.0~100]
				if "," in whole_ips[1]: #192.168.10.0~100,192.168.11.0~100
					splited2 = whole_ips[1].split(",") #[192.168.10.0~100, 192.168.11.0~100]
					for splited3 in splited2:
						if "~" in splited3: #192.168.10.0~100
							splited5 = splited3.split("~") #[192.168.10.0, 100]
							start_ip = splited5[0].split(".") #[192, 168, 10, 0]
							start = int(start_ip[3]) #0
							end = int(splited5[1]) #100
							prefix = start_ip[0] + "." + start_ip[1] + "." + start_ip[2] + "."
							for i in range(start, end + 1):
								ip_list.append(prefix + str(i))
						else: #192.168.10.0
							ip_list.append(splited3.strip())
				else: #192.168.10.0~100
					if "~" in whole_ips[1]:
						splited5 = whole_ips[1].split("~") #[192.168.10.0, 100]
						start_ip = splited5[0].split(".") #[192, 168, 10, 0]
						start = int(start_ip[3]) #0
						end = int(splited5[1]) #100
						prefix = start_ip[0] + "." + start_ip[1] + "." + start_ip[2] + "."
						for i in range(start, end + 1):
							ip_list.append(prefix + str(i))
					else:
						ip_list.append(whole_ips[1].strip())
			else:
				ip_list.append(line.strip())
		f.close()
	else:
		print("bFile is false in default_module")
		for post in postRange:
			ip_list.append(ipAddr[0] + '.' + ipAddr[1] + '.' + ipAddr[2] + '.' + str(post))
	return ip_list
