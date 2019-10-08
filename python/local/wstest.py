# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 14:49:43 2019

@author: joscholt
"""

from azureml.core.webservice import AciWebservice, Webservice
from azureml.core.image import ContainerImage
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
import json

################ Workspace ##############################
with open("./aml_config.json") as f:
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
    ws = Webservice(ws, 'turbofan-rul')    
    
    print(ws.get_keys()[0])
except Exception as e:
    print(e)
