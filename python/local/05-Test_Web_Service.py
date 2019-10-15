## Test Deployed Web Service
##

import numpy as np
import pandas as pd
import json
import requests
from azureml.core.webservice import AciWebservice, Webservice
from azureml.core.image import ContainerImage
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace


################ Workspace ##############################
with open("./config/aml_config.json") as f:
    config = json.load(f)

workspace_name = config["workspace_name"]
resource_group = config["resource_group"]
subscription_id = config["subscription_id"]
workspace_region = config["location"]

#Interactive Authentication
ws = Workspace(workspace_name = workspace_name,
               subscription_id = subscription_id,
               resource_group = resource_group)

webservice_name = 'turbofan-rul'

try:
    service = Webservice(ws, webservice_name) 
    
    uri = service.scoring_uri
    key =service.get_keys()[0]

    train = pd.read_csv("data/turbofan.csv")
    
    sampleSize = round(5/len(train),4)
    testdf = train.sample(frac=sampleSize)
    
    X = testdf.drop('rul',axis=1)
    y = testdf.rul.tolist()
    
    
    input_data = json.dumps(X.to_json( orient='records')) # Create JSON of sample records    
    
    headers = {'Content-Type':'application/json'}
    
    #for AKS deployment you'd need to the service key in the header as well    
    headers = {'Content-Type':'application/json',  'Authorization':('Bearer '+ 'DWr1oUvE5te275ouxKfEDwsDmjRyIdBF')} 
    
    
    resp = requests.post('http://28b77357-0b9e-4760-bac7-19a3dd34b608.centralus.azurecontainer.io/score', input_data, headers=headers)
    
    print("POST to url", uri)
    print("input data:", input_data)
    print("label:", y)
    print("prediction:", resp.text)
except Exception:
    print("Web Service Not Found")