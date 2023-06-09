import asyncio
import time
import requests
import shutil
import sys
import default_module as dm
def myrequest_get(ip):
	url ='http://' + ip + '/video/capture?quality=100&mode=0&rand=1234567'
	headers = {'Authorization': 'Basic YWRtaW46cDAxMjM0', 'Connection': 'Keep-Alive', 'Cache-Control': 'no-cache' }
	response = requests.get(url,headers=headers, stream=True, timeout=3)
	return response



async def capture_async(ip):
	loop = asyncio.get_event_loop()
	print("capture " + ip)
	try:
		req = loop.run_in_executor(None, myrequest_get, ip)
		response = await req
		print(response)
		if response.status_code == 200:
			print("ok")
		else:
			print("error")
	except Exception as e:
		print("disconnect")



async def main():
	tasks = [asyncio.create_task(capture_async(ip)) for ip in ip_list]
	tasks_results = await asyncio.gather(*tasks)
	return tasks_results


ip_list = dm.getIpList(sys.argv[1:])

start = time.time()
asyncio.run(main())
end = time.time()
print(f"시간: {round(end - start)}초")

