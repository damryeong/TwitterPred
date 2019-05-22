'''
Tweets Preprocessing II
Tweet spell correction
'''

import pymysql
import requests
import csv
import math
from bs4 import BeautifulSoup
import os
import json
import re

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}

url_location = 'http://www.bing.com/account/action?scope=web&setmkt=en-IN&setplang=en-in&setlang=en-in'
url_search = 'http://www.bing.com/search?q='

def spell_doctor(self):
    '''
    Corrects the spelling mistakes
    in a tweet using Bing Search
    '''

    global counter, final

    for i in range(links):
        
        text = links[i][1].replace(' . ', '. ')
        text = text.replace(' ? ', '? ')
        text = text.replace(' , ', ', ')
        text = text.replace(' ! ', '! ')
        
        text = text.split()
        
        punc = {}
        
        for pos in range(len(text)):
            if text[pos].find('.') != -1:
                punc[pos] = '.'
    
        for pos in range(len(text)):
            if text[pos].find('?') != -1:
                punc[pos] = '?'

        for pos in range(len(text)):
            if text[pos].find('!') != -1:
                punc[pos] = '!'

        ngram = zip(*[text[i:] for i in range(3)])
        final_grams = []
        initial_grams = []
        
        for gram in ngram:
            
            initial_grams.append(list(gram))
            
            query = re.sub('[%s]' % re.escape(',?.!'), '', ' '.join(gram))

            s = requests.session()

            while 1:
                try:
                    r1 = s.get(url_location, headers=headers)
                    r2 = s.get(url_search + query, headers=headers)
                except requests.exceptions.ConnectionError:
                    print("Request Error")
                    continue

                if r1.ok and r2.ok:
                    soup = BeautifulSoup(r2.text)
                    
                    try:
                        corrected = soup.find('div', {'id':'sp_requery'}).a.get_text().strip().split()
                        final_grams.append(corrected)
                    except:
                        final_grams.append(query.split())
                    
                    break

                else:
                    print("Issue", r.status_code)
                    break
                       
        final_words = []
        try:
            final_words.extend([final_grams[0][0], final_grams[0][1] if final_grams[0][1] != initial_grams[0][1] else final_grams[1][0]])
        except IndexError:
            final_words.extend(final_grams if not final_grams else final_grams[0])
        
        for num in range(len(final_grams)):
            
            try:
                a = final_grams[num][2]
            except IndexError:
                continue
            
            try:
                b = final_grams[num+1][1]
            except IndexError:
                b = a
        
            try:
                c = final_grams[num+2][0]
            except IndexError:
                c = b
        
            if a != initial_grams[num][2]:
                final_words.append(a)
            elif b != initial_grams[num][2]:
                final_words.append(b)
            else:
                final_words.append(c)
        
        for p in range(len(final_words)):
            if punc.__contains__(p):
                final_words[p] += punc[p]

        translated = ' '.join(final_words)

        punc = {}
        
        for ind in range(len(translated)):
            if translated[ind] in ('.','?','!'):
                punc[ind] = translated[ind]
        
        translated = '; '.join(map(lambda x: x if x == '' else x[0].upper() + x[1:], re.split('\. |\? |\! ', translated)))
        
        for ind in punc:
            translated = translated[:ind] + punc[ind] + translated[ind+1:]
        
        final.append({'tweet_id':links[i][0], 'tweet_text':translated})

        counter += 1
        print(counter)

if __name__ == '__main__':

    #Connection to the Database
    conn = pymysql.connect(host='***', port=3306, user='***', passwd='***', db='***', charset='utf8mb4', autocommit=True)
    cur = conn.cursor()

    q = '''select * from pre1 where tweet_id not in (select tweet_id from pre2)'''

    cur.execute(q)
    rows = list(cur.fetchall())

    print("Total", len(rows))
    counter = 0

    #Chunks creation
    rows = [rows[i:i+500]for i in range(0, len(rows), 500)]

    for batch in rows:
        links = tuple(batch)
        final = []

        spell_doctor()
        
        for tweet in final:

            placeholders = ', '.join(['%s'] * len(tweet))
            columns = ', '.join(tweet.keys())

            sql = "INSERT INTO pre2(%s) VALUES (%s)" % (columns, placeholders)

            try:
                cur.execute(sql, list(tweet.values()))
            except pymysql.err.IntegrityError:
                print(tweet.values())
        
        print("------Batch Inserted------")

    cur.close()
    conn.close()
