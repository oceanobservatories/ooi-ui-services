# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import requests
import json
import time
import os

# urls=[
# 'http://ray-srv.ooi.rutgers.edu:12570/sensor/user/inv/null/CP05MOAS-GL001-00-PARAD0000',
# 'http://ray-srv.ooi.rutgers.edu:12570/sensor/user/inv/null/CP05MOAS-GL002-00-CTDGV0000']

urls=[  'https://api.github.com/events',
        'http://feeds.delicious.com/v2/json/recent',
        'hhtps://www.googles.com',
        'http://api.ihackernews.com/page']
# example urls

def get_save_file(urls):
#creates a local file and saves the downloaded page as a json in  'cache' subdirectory
# prints time( in secs) of the function and what is and what is not saved
    



    start= time.time()
    for url in urls:
        try:
            resp = requests.get(url)
            data = json.dumps(resp.json()) 
            save_file(data, url)
        except IOError:
            print" didn't open URL:" + url
        
           
    end=time.time()
    print end-start


        
def save_file(data,url):
    path = 'cache'
# 'path' folder where files are stored
    try:
#url[-27:] makes CP05MOAS-GL002-00-CTDGV0000 the file name
        file_name= url[-2:]+'.json'
        
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, file_name ), 'w') as temp_file:
            temp_file.write(data)
# creates a 'cache' folder if there is none 
# saves the file in a 'cache subdirectory'             
        print "saved " + url
                        #url[-27:]
    except IOError:
        print "didn't save file:" + url
        #                    url[-27:]    

get_save_file(urls)




# <codecell>


