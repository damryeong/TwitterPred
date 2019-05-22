'''
Tweets Preprocessing I
Tweet clean up and hashtags Preprocessing
'''

import pymysql
import re
import random
import ngrams

#Connection to the Database
conn = pymysql.connect(host='***', port=3306, user='***', passwd='***', db='***', charset='utf8mb4', autocommit=True)
cur = conn.cursor()

def filter_tweet(text, hashtags, user_mentions):
    
    #Removing links
    text = re.sub(r"(?:https?\://)\S+", "", text).strip()
    
    #Removing Multiples by Single
    text = re.sub(r"\.+", '.', text)
    text = re.sub(r"\?+", '?', text)
    text = re.sub(r"\!+", '!', text)
    
    #Saving from "Nice Try" Slang Translation
    text = text.replace(' nt ', ' not ')
    
    text = text.replace('&amp;', 'and')
    
    text = '. '.join(text.split('.'))
    text = ', '.join(text.split(','))
    text = '? '.join(text.split('?'))
    text = '! '.join(text.split('!'))

    text = text.split()
    final_words = []
    c = 0

    for word in text:
        if word.strip() == '':
            continue
        elif word[0] == '#' and word.count('#') == 1:
            if word[-1] not in ('.', '?', '!'):
                
                k = c + 1
                flag = 0
                
                while k < len(text):
                    if text[k][0] != '#':
                        flag = 1
                        break
                    k += 1
                
                if flag == 1:
                    try:
                        final_words.append(hashtags[word])
                    except KeyError:
                        final_words.append(word[1:])
            
                else:
                    if final_words[-1][-1] not in ('.', '?', '!'):
                        final_words[-1] = final_words[-1] + '.'
                
                    try:
                        final_words.append(hashtags[word] + '.')
                    except KeyError:
                        final_words.append(word[1:] + '.')
                    
            else:
                #Example - "#Missing.". In Hashtags it is only "#Missing"
                try:
                    final_words.append(hashtags[word[:-1]] + word[-1])
                except KeyError:
                    final_words.append(word)

        else:
            final_words.append(word)
            if c == len(text) - 1 and final_words[-1][-1] not in ('.', '?', '!'):
                final_words[-1] = final_words[-1] + '.'

        c += 1

    tweet_mentions = ' '.join(final_words)

    tweet_names = []
    for word in final_words:
        try:
            tweet_names.append(user_mentions[word])
        except KeyError:
            tweet_names.append(word)       
    tweet_names = ' '.join(tweet_names)

    return tweet_names, tweet_mentions

def split_by_uppercase(hashtag):
    
    uppercase_spots = [b.isupper() for b in hashtag]
    
    if True not in uppercase_spots:
        return hashtag
    
    indices = []
    i = 0

    while i < len(hashtag):
        if uppercase_spots[i] is True:
            start = i
            
            while (i+1 < len(hashtag) and uppercase_spots[i] is True and uppercase_spots[i+1] is True) or (len(hashtag) == i+1 and uppercase_spots[i] is True):
                i += 1

            end = i

            if start == end:
                indices.append(start)
                i += 1
            else:
                indices.append((start, end))

        else:
            i += 1

    final_string = []
    
    if (type(indices[0]) is int and indices[0] != 0):
        final_string.append(hashtag[:indices[0]])
    if (type(indices[0]) is tuple and indices[0][0] != 0):
        final_string.append(hashtag[:indices[0][0]])

    for i in range(len(indices)):
        if type(indices[i]) is tuple:
            final_string.append(hashtag[indices[i][0]:indices[i][1]])
        else:
            try:
                if type(indices[i+1]) is int:
                    final_string.append(hashtag[indices[i]:indices[i+1]])
                else:
                    final_string.append(hashtag[indices[i]:indices[i+1][0]])
            except IndexError:
                final_string.append(hashtag[indices[i]:])

    return ' '.join(final_string)


def expand_hashtags(hashtags):

    final_hashtags = {}

    for hashtag in hashtags:
        
        #Split around underscore
        if hashtag.find('_') != -1:
            final_hashtags['#' + hashtag] = ' '.join(hashtag.split('_'))
        
        #Split around hyphen
        elif hashtag.find('-') != -1:
            final_hashtags['#' + hashtag] = ' '.join(hashtag.split('-'))
        
        #Numbers and Capitals
        elif re.findall('\d+', hashtag):
            
            #Split around numbers
            nums = re.findall('\d+', hashtag)
            htag = hashtag
            broken_hashtag = []
            
            for num in nums:
                pos = hashtag.find(num)
                if pos == 0:
                    broken_hashtag.append(num)
                else:
                    broken_hashtag.extend([split_by_uppercase(hashtag[:pos]), num])

                hashtag = hashtag[pos + len(num):]
        
            if hashtag != '':
                broken_hashtag.append(split_by_uppercase(hashtag))
    
            final_hashtags['#' + htag] = ' '.join(broken_hashtag)

        #Capitals
        elif True in [b.isupper() for b in hashtag]:
            final_hashtags['#' + hashtag] = split_by_uppercase(hashtag)
        
        #No Pattern - Segmentation Algorithm
        else:
            final_hashtags['#' + hashtag] = ' '.join(ngrams.segment(hashtag))

    return final_hashtags

def coverup(tweets):

    for tweet in tweets:
        tweet_names = tweet[1].split()
        final = []

        for t in tweet_names:
            if t.find('#') != -1:
                hashes = t.split('#')
                hashlist = [hashes[0]]
                hashlist.extend(['#' + k for k in hashes[1:]])
                final.extend(hashlist)

            else:
                final.append(t)

        proper_tweet = ' '.join(final)
        hashtags = []
        hashtags_sql = []

        for word in proper_tweet.split():
            if word[0] == '#':
                if word[-1] in ('.',',','!','?','-'):
                    hashtags.append(word[1:-1])
                    hashtags_sql.append((tweet[0], word[1:-1]))
                else:
                    hashtags.append(word[1:])
                    hashtags_sql.append((tweet[0], word[1:]))

        cur.executemany('insert into hashtags values(%s, %s)', hashtags_sql)

        hashtags = expand_hashtags(hashtags)
        text1, text2 = filter_tweet(proper_tweet, hashtags, {})

        cur.execute('update pre1 set tweet_text_names=%s, tweet_text_mentions=%s where tweet_id=%s', (text1, text2, tweet[0]))

if __name__ == '__main__':

    cur.execute("select tweet_id, tweet_text from posts where tweet_id not in (select tweet_id from pre1)")

    fetched = cur.fetchall()
    tweet_ids = []

    for tweet in fetched:
        # Treat hastags
        cur.execute('select hashtag from hashtags where tweet_id=%s', (tweet[0]))
        hashtags = cur.fetchall()
        
        if hashtags:
            try:
                hashtags = [str(h[0]) for h in hashtags]
                hashtags = expand_hashtags(hashtags)
            except UnicodeEncodeError:
                hashtags = {}
        else:
            hashtags = {}

        #Treat User mentions
        cur.execute('select b.name, b.screen_name from user_mentions a inner join users b on a.user_id = b.user_id where tweet_id=%s', (tweet[0]))
        mentions = cur.fetchall()

        mentions_map = {}

        for user in mentions:
            mentions_map['@' + user[1]] = user[0]

        #Texts with user mentions retained and user mentions replaced
        text1, text2 = filter_tweet(tweet[1], hashtags, mentions_map)

        cur.execute('insert into pre1 values(%s, %s, %s)', (tweet[0], text1, text2))

    # Tweets still with ill Hashtags
    cur.execute('''select * from pre1 where tweet_text_names like "%#%"''')
    tweets = cur.fetchall()

    coverup(tweets)

    cur.close()
    conn.close()