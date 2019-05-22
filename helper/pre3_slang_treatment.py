'''
Tweets Preprocessing III
Tweet slang treatment
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

URL = 'http://www.noslang.com/'

def slang_treatment(self):
    '''
    Converting slang terms to actual
    words divided into 4 steps of
    decreasing priority order
    '''

    global counter, final
    
    for i in range(links):
        
        words = links[i][1].split()
        marked = [False for num in range(len(words))]
        
        #Step 1
        index = 0
        for word in words:
            punc = word[-1] if word[-1] in (',?.!') else ''
            caps = True if word[0].isupper() else False
        
            cleaned_word = re.sub('[%s]' % re.escape(',?.!'), '', word.lower())
            
            if domain_specific.__contains__(cleaned_word):
                words[index] = domain_specific[cleaned_word] + punc
                words[index] = words[index][0].upper() + words[index][1:] if caps else words[index]

                marked[index] = True

            index += 1

        #Step 2 and 3
        index = 0
        for word in words:
            if not marked[index]:
                cleaned_word = re.sub('[%s]' % re.escape(',?.!'), '', word)
                marked[index] = True if cleaned_word.isdigit() or cleaned_word.isupper() else False

            index += 1

        #Step 4
        index = 0
        for word in words:
            if not marked[index]:

                punc = word[-1] if word[-1] in (',?.!') else ''
                caps = True if word[0].isupper() else False
        
                cleaned_word = re.sub('[%s]' % re.escape(',?.!'), '', word.lower())

                while 1:
                    try:
                        r = requests.post(URL, data = {'action': 'translate', 'p':cleaned_word, 'submit':'Translate'}, headers=headers)
                    except (requests.exceptions.ConnectionError, socks.Socks5Error) as e:
                        print("Request Error")
                        continue
                                            
                    if r.ok:
                        soup = BeautifulSoup(r.text)
                        translated = soup.find('div', {'class':'translation-text'}).get_text().strip()

                        if translated.find('None of the words you entered are in our database.') != -1:
                            translated = cleaned_word
                        break

                    else:
                        print("Issue", r.status_code)
                        break

                if translated != cleaned_word:
                    translated += punc
                    translated = translated[0].upper() + translated[1:] if caps else translated

                    words[index] = translated
    
            index += 1
    
        final.append({'tweet_id':links[i][0], 'tweet_text':' '.join(words)})

        counter += 1
        print(counter)

if __name__ == '__main__':

    #Connection to the Database
    conn = pymysql.connect(host='***', port=3306, user='***', passwd='***', db='***', charset='utf8mb4', autocommit=True)
    cur = conn.cursor()

    q = '''select * from pre2 where tweet_id not in (select tweet_id from pre3)'''

    cur.execute(q)
    rows = list(cur.fetchall())

    print("Total", len(rows))
    counter = 0
    
    #Fetching slangs specific to the dataset
    f = open('domain_specific_slangs.txt', 'r')
    domain_specific = {}
    line = f.readline().strip('\n')
    
    while line != '':
        maps = line.split('- ')
        domain_specific[maps[0].lower()] = maps[1]
        line = f.readline().strip('\n')
    
    f.close()

    #Chunks creation
    rows = [rows[i:i+50]for i in range(0, len(rows), 50)]

    for batch in rows:
        links = tuple(batch)
        final = []

        slang_treatment()
        
        for tweet in final:

            placeholders = ', '.join(['%s'] * len(tweet))
            columns = ', '.join(tweet.keys())

            sql = "INSERT INTO pre3(%s) VALUES (%s)" % (columns, placeholders)

            try:
                cur.execute(sql, list(tweet.values()))
            except pymysql.err.IntegrityError:
                print(tweet.values())

        print("------Batch Inserted------")

    cur.close()
    conn.close()
