# Need upgraded setuptools and need "poster" (only available with python2)
# Need unirest 

RAPIDAPI_HOST = "osome-public.p.rapidapi.com"
RAPIDAPI_KEY = "0493c0e0f4mshe80b4d8c8986e14p103af6jsna45ff41b76b1"
URL_START = "https://osome-public.p.rapidapi.com/tweet-id?q="
STORE_PATH = "./tweet_ids/"

start = "2017-05-01T00:00:00"
end = "2019-05-31T23:59:59"

import requests
import urllib
import time

def get_url_content(url):
	"""Fetches the content from the given url and returns it"""
	print ("Fetching URL: ",url)
	return urllib.request.urlopen(url).read()

def write_new_content(filename,content):
	"""Write the given content in the given filename"""
	print ("Writing Content File: "+filename)
	with open(filename,"wb") as f:
		f.write(content)

def get_requests_url(url):
	return requests.get(url,headers ={"X-RapidAPI-Host": RAPIDAPI_HOST,"X-RapidAPI-Key": RAPIDAPI_KEY})

def get_tweet_ids_by_hashtag(s,start,end):
	""" Takes the hashtag s and gets tweet_ids
	From start to end in ISO datetime format
	Expected ISO Format : yyyy-mm-ddThh:mm:ss"""
	s = "%23"+s
	start = start.replace(':','%3A')
	end = end.replace(':','%3A')
	urllink = URL_START+s+"&start="+start+"&end="+end
	response = get_requests_url(urllink)
	if(str(response.status_code)[0]=='2'):
		print ("Received Response, Status Code: "+str(response.status_code))
		data = response.json()
		urls = data['files']
		for i in range(len(urls)):
			write_new_content(STORE_PATH+s+"_"+str(i)+".txt",get_url_content(urls[i]))
	else:
		print ("HTTP Error, Status Code: "+str(response.status_code))

#get_tweet_ids_by_hashtag("isis",start,end)

def get_tweet_ids_by_hashtags(l,start,end):
	""" Takes the hashtag list l and gets tweet_ids
	From start to end in ISO datetime format
	Expected ISO Format : yyyy-mm-ddThh:mm:ss"""
	s = "%2C".join(["%23"+i for i in l])
	start = start.replace(':','%3A')
	end = end.replace(':','%3A')
	urllink = URL_START+s+"&start="+start+"&end="+end
	response = get_requests_url(urllink)
	if(str(response.status_code)[0]=='2'):
		print ("Received Response, Status Code: "+str(response.status_code))
		data = response.json()
		urls = data['files']
		for i in range(len(urls)):
			write_new_content(STORE_PATH+s+"_"+str(i)+".txt",get_url_content(urls[i]))
	else:
		print ("HTTP Error, Status Code: "+str(response.status_code))

#get_tweet_ids_by_hashtags(["yolo","swag"],"2018-01-01T00:00:00","2018-01-01T23:59:59")

def get_tweet_ids_with_file(filename,start,end):
	"""Gets hashtags store in a file and uses get tweet_ids_by_hashtags to get multiple files with tweet_ids"""
	with open(filename,"r") as f:
		content = f.read()
	l = content.split()
	i = 0
	while(i<len(l)):
		hashtag = l[i].lstrip('#')
		try:
			get_tweet_ids_by_hashtag(hashtag,start,end)
			i+=1
		except:
			continue

		if((i+1)%100==0):
			time.sleep(60)


get_tweet_ids_with_file("hashtags.txt",start,end)