## Use AMLs Python SDK to track experiment and log run metrics
##

from sklearn.ensemble import GradientBoostingRegressor
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.datasets import load_boston
from sklearn.metrics import mean_absolute_error
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from random import randrange,randint
from sklearn.externals import joblib
import json


################ Workspace ##############################
with open("./config/aml_config.json") as f:
    config = json.load(f)

workspace_name = config["workspace_name"]
resource_group = config["resource_group"]
subscription_id = config["subscription_id"]
workspace_region = config["location"]


max_depth = randint(2,10)
n_estimators = int(randrange(2000,5000,100))


#Interactive Authentication
ws = Workspace(workspace_name = workspace_name,
               subscription_id = subscription_id,
               resource_group = resource_group)



############# Experiement gbr-turbofan ######################
experiment = Experiment(ws, 'gbr-turbofan')


train = pd.read_csv("data/turbofan.csv")

X = train.drop('rul',axis=1)
y = pd.Series(train.rul)

run =  experiment.start_logging()

 # Log the algorithm parameter alpha to the run
run.log('max_depth', max_depth)
run.log('n_estimators', n_estimators)


X_train, X_test, y_train, y_test = train_test_split(X, y)


regression_model = GradientBoostingRegressor(
    max_depth=max_depth,
    n_estimators=n_estimators,
    learning_rate=.5
)

regression_model.fit(X_train, y_train)

y_pred = regression_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
run.log('mae', mae)


# Save the model to the outputs directory for capture
model_file_name = 'outputs/model.pkl'

joblib.dump(value = regression_model, filename = model_file_name)

# upload the model file explicitly into artifacts 
run.upload_file(name = model_file_name, path_or_stream = model_file_name)

# Complete the run
run.complete()

