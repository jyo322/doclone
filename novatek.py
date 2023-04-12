import requests
import sys
import os
import shutil
import datetime
import random
import json
import time
from collections import OrderedDict
import default_module as dm


class MyError(Exception):
    def __str__(self):
        return "get_parking error"

class novatek:
	def __init__(self, ip):
		self.ip = ip

	#capture폴더에 캡처이미지 생성
	def get_capture(self):
		strdt = 'capture'
		if(not os.path.isdir(strdt)):
			os.mkdir(strdt)
		strdt2 = 'capture/original'
		if(not os.path.isdir(strdt2)):
			os.mkdir(strdt2)


		addr = self.ip
		capture = '/video/capture?quality=100&mode=0&rand=1234567'
		url ='http://' + addr + capture
		headers = {'Authorization': 'Basic YWRtaW46cDAxMjM0', 'Connection': 'Keep-Alive', 'Cache-Control': 'no-cache' }
		try:	
			response = requests.get(url,headers=headers, stream=True, timeout=3)
			if response.status_code == 200:
				print(addr + ": capture OK");
				with open(strdt2 +'/' + addr + '.jpg', 'wb') as f:
					response.raw.decode_content=True
					shutil.copyfileobj(response.raw, f)
			else:
				print(addr + ": server error");
		except requests.exceptions.ConnectionError as e:
			print(addr + ": connect error");

	#edge값 받아서 리스트로 저장
	def get_edge(self):
		def get_parking(ip):
			headers = {'Authorization': 'Basic YWRtaW46cDAxMjM0', 'Connection': 'Keep-Alive', 'Cache-Control': 'no-cache' }
			url ='http://' + ip + '/parking/edge'
			try:
				response = requests.get(url, headers=headers, timeout=5)
				return response.text
			except:
				print(ip + ": server error get_Parking")
				raise MyError()	
		data = OrderedDict()
		data = json.loads(get_parking(self.ip))
		return data['edge']

	#스레스홀드값 받아와서 리스트로 저장
	def get_threshold(self):
		data = OrderedDict()
		data = json.loads(dm.get_common(self.ip, '/parking'))
		area = OrderedDict()
		areacnt = len(data["areas"])
		threshold = []

		for i in range(int(areacnt)):
			if ('threshold' in data['areas'][i]) == True:
				area[i] = data['areas'][i]['threshold']
				threshold.append(area[i])
			elif ('threshold' in data['areas'][i]) == False:
				area[i] = data["main"]["threshold"]
				threshold.append(area[i])
		return threshold
		

	def get_dewarp(self):
		str_data = dm.get_common(self.ip, "/video/dewarp")
		params = json.loads(str_data)
		return params


	def get_xy(self):
		data = OrderedDict()
		data = json.loads(dm.get_common(self.ip, '/parking'))
		points = OrderedDict()
		areacnt = len(data["areas"])
		xy=[]
		for i in range(0, int(areacnt)):
			points[i] = data["areas"][i]['points'] 
			xy.append(points[i])	
		return(xy)
