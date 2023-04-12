import asyncio
import requests
import time
from aiohttp import ClientSession




urls = ['http://192.168.0.222/video/capture?quality=100&mode=0&rand=1234567']
headers = {'Authorization': 'Basic YWRtaW46cDAxMjM0', 'Connection': 'Keep-Alive', 'Cache-Control': 'no-cache' }

async def url_request(url):  
    async with ClientSession() as session: 
        async with session.get(url,headers=headers, stream=True, timeout=3) as response: 
            resp = await response.status_code
            print(resp)



async def main():
    htmls = [url_request(url) for url in urls] 
    for i, completed in enumerate(asyncio.as_completed(htmls)): 
        await completed
        


start_ = time.time()
event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(main())
except:
    event_loop.close()
print("async 총걸린시간 {}".format(time.time() - start_))