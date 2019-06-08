from twython import Twython
import numpy as np
import pandas as pd


STORE_PATH = "./tweet_ids/"
APP_KEY = 'P0bUVPSQymvevVJxvvpqwOj6H' 
APP_SECRET = '5JnOWfNSCe3Ynh9pIm7KMQvH1IQqr9yNM6FhRzVUiuAaTh7Rwy'
needed_columns = ['coordinates','created_at','entities','favorite_count','id_str','lang','metadata','place','retweet_count','retweeted','retweeted_status','text','user']
complex_columns = ['entities','retweeted_status','user','place']

def get_tweet_ids_from_file(filename,tweet_ids_from_file):
	"""get tweet_ids in the given filename and put them in the list tweet_ids_from_file"""

	print ("extending list(tweet_ids_from_file) with tweet_ids from filename: "+filename)
	f = open(STORE_PATH+filename, 'r')
	ids= f.read()
	ids=ids.split()
	tweet_ids_from_file.extend(ids)


def get_twython_api(APP_KEY,APP_SECRET):
	twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
	ACCESS_TOKEN = twitter.obtain_access_token()
	twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
	return twitter


def get_statuses_by_id(tweet_ids_from_file,statuses_list,APP_KEY,APP_SECRET):
	"""search tweet_ids from list tweet_ids_from_file"""

	print ("extending list(statuses_list) with statuses from search result: "+filename)

	#APP_KEY = 'P0bUVPSQymvevVJxvvpqwOj6H' 
	#APP_SECRET = '5JnOWfNSCe3Ynh9pIm7KMQvH1IQqr9yNM6FhRzVUiuAaTh7Rwy'

	twitter=get_twython_api(APP_KEY,APP_SECRET)

	for tweet_id in tweet_ids_from_file:
		status=twitter.show_status(tweet_id)
		statuses_list.extend(status)
  

def convert_to_df(statuses_list):
	tweets_df = pd.DataFrame()
	tweets_df = tweets_df.append(statuses_list,ignore_index = True)
	return tweets_df

def filter_statuses(tweets_df,needed_columns):
	tweets_sel = tweets_df[columns]
	return tweets_sel

def create_other_columns(tweets_sel):
	tweets_sel['uploader_id'] = tweets_sel['user'].apply(lambda x: x['id_str'])
	tweets_sel['uploader_name'] = tweets_sel['user'].apply(lambda x: x['name'])
	tweets_sel['uploader_screen_name'] = tweets_sel['user'].apply(lambda x: x['screen_name'])
	tweets_sel['num_likes']= tweets_sel['favorite_count']
	tweets_sel['num_retweets'] = tweets_sel['retweet_count']
	for i in range(tweets_sel.shape[0]):
		place = tweets_sel.loc[i,'place']
		if(type(place)==dict):
			tweets_sel.loc[i,'tweet_country_name'] = place['country']
			tweets_sel.loc[i,'tweet_location'] = place['full_name']
		else:
		    tweets_sel.loc[i,'tweet_country_name'] = None
		    tweets_sel.loc[i,'tweet_location'] = None

def get_hashtags(tweets_sel):  
	#Hashtag
	hashtags_df = pd.DataFrame(columns=['tweet_id','hashtag'])
	tweets_sel['num_hashtags'] = [0 for i in range(tweets_sel.shape[0])]
	for i in range(tweets_sel.shape[0]):
		tweet_id = tweets_sel.loc[i,'id_str']
		hashtags = list(map(lambda x:x.get('text'),tweets_sel.iloc[i]['entities']['hashtags']))
		if(len(hashtags)!=0):
			temp_df = pd.DataFrame(list(zip([tweet_id]*len(hashtags),hashtags)),columns=['tweet_id','hashtag'])
			hashtags_df = hashtags_df.append(temp_df,ignore_index=True)
			tweets_sel.loc[i,'num_hashtags'] = len(hashtags)
	return tweets_sel,hashtags_df

def get_usermentions(tweets_sel):
	usermentions_df = pd.DataFrame(columns=['tweet_id','user_id','name','screen_name'])
	for i in range(tweets_sel.shape[0]):
		tweet_id = tweets_sel.loc[i]['id_str']
		usermentions = list(map(lambda x:[x.get(j) for j in ['id_str','name','screen_name']],tweets_sel.loc[i]['entities']['user_mentions']))
		if(len(usermentions)!=0):
			lists = [[tweet_id,j[0],j[1],j[2]] for j in usermentions]
			temp_df = pd.DataFrame(lists,columns=['tweet_id','user_id','name','screen_name'])
			usermentions_df = usermentions_df.append(temp_df,ignore_index=True)
		tweets_sel.loc[i,'num_user_mentions'] = int(len(usermentions))
	return tweets_sel,usermentions_df


def make_usermetadata(tweets_sel):
	cols = ['uploader_id','name','screen_name','description','location','followers_count','friends_count','created_at','favourites_count','lang','verified','statuses_count','url']
	user_metadata_df = pd.DataFrame(columns=cols)
	for i in range(tweets_sel.shape[0]):
		tweet_id = tweets_sel.loc[i,'id_str']
		#print(tweet_id)
		#print(tweets_sel.loc[i,'user'])
		user_data = [tweets_sel.loc[i,'user'][j] for j in ['id_str',]+cols[1:]]
		if(len(user_data)!=0):
			temp_df = pd.DataFrame([user_data],columns=cols)
			user_metadata_df = user_metadata_df.append(temp_df,ignore_index=True)
	return user_metadata_df

def get_urls_df(tweets_sel):
	urls_df = pd.DataFrame(columns=['tweet_id','url'])
	for i in range(tweets_sel.shape[0]):
		tweet_id = tweets_sel.loc[i,'id_str']
		urls = list(map(lambda x:x.get('expanded_url'),tweets_sel.iloc[i]['entities']['urls']))
		if(len(urls)!=0):
			temp_df = pd.DataFrame(list(zip([tweet_id]*len(urls),urls)),columns=['tweet_id','url'])
			urls_df = urls_df.append(temp_df,ignore_index=True)
		tweets_sel.loc[i,'num_urls'] = len(urls)
	return tweets_sel,urls_df

def get_timeline_df_of_screen_name(screen_name,APP_KEY,APP_SECRET):

	twitter=get_twython_api(APP_KEY,APP_SECRET)
	timeline=twitter.get_user_timeline(screen_name=screen_name,count=2000,include_rts=True)

	cols_timeline = ['tweet_id','text','created_at','user_id','name','screen_name']
	tweet_user_timeline_df = pd.DataFrame(columns=cols_timeline)
	#print(tweet_user_timeline_df)
	for i in range(len(timeline)):
		tweet_id = timeline[i]['id_str']
		text=timeline[i]['text']
		created_at=timeline[i]['created_at']
		user_data = [timeline[i]['user'][j] for j in ['id_str','name','screen_name']]
		#print(user_data)
		if(len(user_data)!=0):
			lists_timeline = [tweet_id,text,created_at,]+user_data
			temp_df = pd.DataFrame([lists_timeline],columns=cols_timeline)
			tweet_user_timeline_df = tweet_user_timeline_df.append(temp_df,ignore_index=True)
	return tweet_user_timeline_df


