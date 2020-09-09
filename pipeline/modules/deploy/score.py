
# Change the name based on the randomly generated filename
# Scoring Script will need model id from registered model
import json
import numpy as np
from sklearn.externals import joblib
from sklearn.ensemble import GradientBoostingRegressor
import pandas as pd
from azureml.core.model import Model
import os

def init():
    global model
    # retreive the path to the model file using the model name
    pth = Model.get_model_path('turbofan-pipeline-rul')
    model_path = pth 
    #os.path.join(pth, 'model.pkl')
    #os.getenv('AZUREML_MODEL_DIR')
    model = joblib.load(model_path)
    

def run(raw_data):
    # grab and prepare the data
    data = pd.read_json(json.loads(raw_data),orient='records')

    y_hat = model.predict(data)
    return json.dumps(y_hat.tolist())