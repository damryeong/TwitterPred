# Need upgraded setuptools and need "poster" (only available with python2)
# Need unirest 

RAPIDAPI_HOST = "osome-public.p.rapidapi.com"
RAPIDAPI_KEY = "ffe7ad2b0fmshfd5922868484357p1c7e80jsn08f30f6f12e9"
STORE_PATH = "./tweet_ids/"

import unirest
import urllib2

def get_url_content(url):
	"""Fetches the content from the given url and returns it"""
	print "Fetching URL: ",url
	return urllib2.urlopen(url).read()

def write_new_content(filename,content):
	"""Write the given content in the given filename"""
	print "Writing Content File: "+filename
	with open(filename,"w") as f:
		f.write(content)

def get_tweet_ids_by_hashtag(s,start,end):
	""" Takes the hashtag s and gets tweet_ids
	From start to end in ISO datetime format
	Expected ISO Format : yyyy-mm-ddThh:mm:ss"""
	s = "%23"+s
	start = start.replace(':','%3A')
	end = end.replace(':','%3A')
	response = unirest.get("https://osome-public.p.rapidapi.com/tweet-id?q="+s+"&start="+start+"&end="+end,headers={"X-RapidAPI-Host": RAPIDAPI_HOST,"X-RapidAPI-Key": RAPIDAPI_KEY})
	if(str(response.code)[0]=='2'):
		print "Received Response, Status Code: "+str(response.code)
		urls = response.body['files']
		for i in range(len(urls)):
			write_new_content(STORE_PATH+s+"_"+str(i)+".txt",get_url_content(urls[i]))
	else:
		print "HTTP Error, Status Code: "+str(response.code)

def get_tweet_ids_by_hashtags(l,start,end):
	""" Takes the hashtag list l and gets tweet_ids
	From start to end in ISO datetime format
	Expected ISO Format : yyyy-mm-ddThh:mm:ss"""
	s = "%2C".join(["%23"+i for i in l])
	start = start.replace(':','%3A')
	end = end.replace(':','%3A')
	response = unirest.get("https://osome-public.p.rapidapi.com/tweet-id?q=%23"+s+"&start="+start+"&end="+end,headers={"X-RapidAPI-Host": RAPIDAPI_HOST,"X-RapidAPI-Key": RAPIDAPI_KEY})
	if(str(response.code)[0]=='2'):
		print "Received Response, Status Code: "+str(response.code)
		urls = response.body['files']
		for i in range(len(urls)):
			write_new_content(STORE_PATH+s+"_"+str(i)+".txt",get_url_content(urls[i]))

	else:
		print "HTTP Error, Status Code: "+str(response.code)

#get_tweet_ids_by_hashtags(["yolo","swag"],"2018-01-01T00:00:00","2018-01-01T23:59:59")

def get_tweet_ids_with_file(filename,start,end):
	"""Gets hashtags store in a file and uses get tweet_ids_by_hashtags to get multiple files with tweet_ids"""
	with open(filename,"r") as f:
		content = f.read()
	l = content.split()
	get_tweet_ids_by_hashtags(l,start,end)

get_tweet_ids_with_file("hashtags.txt","2018-01-01T00:00:00","2018-01-01T23:59:59")


