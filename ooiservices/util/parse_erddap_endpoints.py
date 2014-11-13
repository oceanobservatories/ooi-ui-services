
# coding: utf-8

# In[170]:

import requests
import json
import re
import time
from ooiservices import app

#base_url = "http://erddap.ooi.rutgers.edu/erddap"
from config import ERDDAPURL
base_url = ERDDAPURL


meta_outline = None
cache_update = None

def getStreamIdsForRef(ref):
    ref = re.sub(r'-', '_', ref)
    stream_list = []
    meta_outline = get_meta_outline()
    for row in meta_outline["table"]["rows"]:
        dataset_id = row[-1]
        if dataset_id.startswith(ref):
            stream_name = dataset_id.split(ref)[1]
            stream_name = stream_name.lstrip('_')
            if stream_name not in stream_list:
                stream_list.append(stream_name)

    return stream_list

def get_meta_outline():
    global meta_outline
    global cache_update
    if meta_outline is None:
        cahce_update = time.time()
        url = base_url+"/info/index.json"
        meta_outline = requests.get(url)
        meta_outline = meta_outline.json()
    if cache_update < (time.time() + 60):
        cahce_update = time.time()
        url = base_url+"/info/index.json"
        meta_outline = requests.get(url)
        meta_outline = meta_outline.json()
    return meta_outline

def getAttribsForRef(ref,stream):
    variable_list = []
    
    url = base_url + "/info/" + ref + '_' + stream + "/index.json"
    ref_outline = requests.get(url)
    
    d = ref_outline.json()['table']
    cols = d['columnNames']
    for i,c in enumerate(cols):
        if c == "Variable Name":            
            break
    for r in d['rows']:
        if r[i] != "NC_GLOBAL" and r[i] not in variable_list and r[i] != "time":
            variable_list.append(r[i])

    if variable_list:
        app.logger.error(repr(variable_list))
    return variable_list


# In[173]:


#ref_id = "CP05MAS_GL001_03_CTDGVM0000"
#stream_list = getStreamIdsForRef(ref_id)
#print stream_list
#
#for stream in stream_list:
    #params = getAttribsForRef(ref_id,stream)
#
#print params


# In[173]:



