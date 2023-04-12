from defisheye import Defisheye
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
import novatek as nov
import glob
from PIL import Image
import onnxruntime
import cv2
import shutil


#폴더생성
def make_folder(strdt):
	if(not os.path.isdir(strdt)):
		os.mkdir(strdt)


#캡처이미지 드와핑
def dewarp_img(img_capture, img_dewarp):
	dewarp = camera.get_dewarp()
	obj = Defisheye(img_capture, dtype='equalarea', xcenter=dewarp['centerX'], ycenter=dewarp['centerY'], radius=dewarp['outterRadius'], pfov=120, p_radius=256)
	obj.convert(img_dewarp)

#주차영역의 중심점 구하기
def center():
	x_c=[]
	y_c=[]
	xy = camera.get_xy()
	#xy=[x좌표0,y좌표0,x좌표1,y좌표1,x좌표2,y좌표2,....]
	#len(xy)=주차영역갯수
	#len_xy=주차영영역 구성 점 갯수
	for i in range(0,len(xy)):
		len_xy=int(len(xy[i])/2)
		x=0
		y=0
		for j in range(0,len_xy):
			x=x+xy[i][0]
			del xy[i][0]
			y=y+xy[i][0]
			del xy[i][0]
		x_c.append(x/len_xy)
		y_c.append(y/len_xy)
	return x_c, y_c


# AI프로그램 실행하여 자동차 있는 구역찾은 후 이미지 출력
def ai_draw(img_dewarp):
		ort_session = onnxruntime.InferenceSession("models/ssd_mobv2.onnx")
		img_ai = cv2.imread(img_dewarp)
		ort_inputs = {ort_session.get_inputs()[0].name: img_ai[None]}
		ort_outs = ort_session.run(None, ort_inputs)
		boxes = ort_outs[1][0]
		scores = ort_outs[4][0]
		boxes_ = (boxes * 512).astype(int)

		#AI 적용 이미지 출력
		for (t, l, b, r), s in zip(boxes_, scores):
			if s >= .3:
				blue=(255, 0, 0)
				img_ai = cv2.rectangle(img_ai, (l, t), (r, b), blue, 2)
		cv2.imwrite("capture/AI/"+ip+".jpg", img_ai)
		return img_ai


#구한 중심점 perspective변환하여 ai인식 이미지에 그리기
def draw_center(x_c, y_c, img_ai):
	xy = camera.get_xy()
	x_cp=[]
	y_cp=[]
	dewarp = camera.get_dewarp()
	obj = Defisheye(img_capture, dtype='equalarea', xcenter=dewarp['centerX'], ycenter=dewarp['centerY'], radius=dewarp['outterRadius'], pfov=120, p_radius=256)
	obj.convert(img_dewarp)
	for i in range(0,len(xy)):
		(x_c_p, y_c_p) = obj.convert_point(x_c[i],y_c[i])
		x_cp.append(x_c_p)
		y_cp.append(y_c_p)
		#cv2.putText(이미지, 문자열, 좌표, 폰트종류, 폰트크기, 색, 굵기, 선타입)
		text = str(i)
		red = (0, 0, 255)
		img_result = cv2.putText(img_ai, text, (x_cp[i] ,y_cp[i]), cv2.FONT_HERSHEY_COMPLEX, 0.8, red, 2, cv2.LINE_8)
	cv2.imwrite("capture/result/"+ip+".jpg", img_result)
	return x_cp, y_cp, img_result


#AI로 만차인 영역찾아서 리스트로 변환
def ai_mangong(x_cp, y_cp):
	#AI로 만차인 영역 찾기
	ort_session = onnxruntime.InferenceSession("models/ssd_mobv2.onnx")
	img_ai = cv2.imread(img_dewarp)
	ort_inputs = {ort_session.get_inputs()[0].name: img_ai[None]}
	ort_outs = ort_session.run(None, ort_inputs)
	boxes = ort_outs[1][0]
	scores = ort_outs[4][0]
	boxes_ = (boxes * 512).astype(int)
	man=[]
	for (t, l, b, r), s in zip(boxes_, scores):
		if s >= .3:
			for i in range(0,len(x_c)):
				if (t<y_cp[i]<b or t>y_cp[i]>b) and (l<x_cp[i]<r or l>x_cp[i]>r):
					man.append(i)
	#AI로 확인한 만차인 영역 리스트로변환하기
	mangong=[]
	xy = camera.get_xy()
	for i in range(0,len(xy)):
		mangong.append("공차")
	sorted_man=sorted(man)
	for i in range(0,len(sorted_man)):
		mangong[sorted_man[i]]="만차"
	return mangong


def camera_mangong():
	#카메라에서 만공파악하기
	edge=camera.get_edge()
	threshold=camera.get_threshold()
	mangong_camera=[]	
	for i in range(0,len(edge)):
		if edge[i] <= float(threshold[i]):
			mangong_camera.append("공차")
		else:
			mangong_camera.append("만차")
	return mangong_camera

def compare_mangong(mangong, mangong_camera, img_result):
	#AI와 카메라에서의 만공차 비교하기
	xy = camera.get_xy()
	for i in range(0,len(xy)):
		if mangong[i] != mangong_camera[i]:
			print(ip, "pgs",i,"확인필요" )
			#오류 영역 초록색으로 나타내기
			img_result = cv2.rectangle(img_result, (x_cp[i]+40 ,y_cp[i]+30), (x_cp[i]-30 ,y_cp[i]-40), (0, 255, 0), 2)
			cv2.imwrite("capture/result/"+ip+".jpg", img_result)
			#에러인 경우 error 폴더에 복사 붙여넣기
			shutil.copy("capture/result/" +ip+ ".jpg", "capture/error")

ip_list = dm.getIpList(sys.argv[1:])
for ip in ip_list:
	try:
		make_folder('capture')
		make_folder('capture/dewarp')
		make_folder('capture/AI')
		make_folder('capture/result')
		make_folder('capture/error')

		#캡처로 이미지 받기
		camera = nov.novatek(ip)
		capture = camera.get_capture()
		
		#이미지 주소 설정
		img_capture = "capture/original/"+ip+".jpg"
		img_dewarp = "capture/dewarp/"+ip+".jpg"
		img_ai = "capture/AI/"+ip+".jpg"
		img_result = "capture/result/"+ip+".jpg"

		dewarp_img(img_capture, img_dewarp)
		img_ai = ai_draw(img_dewarp)
		x_c, y_c = center()
		x_cp, y_cp, img_result = draw_center(x_c, y_c, img_ai)
		mangong = ai_mangong(x_cp, y_cp)
		mangong_camera = camera_mangong()

		compare_mangong(mangong, mangong_camera, img_result)





	except:
		print(ip, "error")


