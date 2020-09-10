# Databricks notebook source
from azureml.core.webservice import AciWebservice, Webservice
from azureml.core.image import ContainerImage
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
import json


webservice_name = 'turbofan-rul'

# COMMAND ----------

subscription_id = "" #you should be owner or contributor
resource_group = "" #you should be owner or contributor
workspace_name = "" #your workspace name
workspace_region = "" #your region

try:
  ws = Workspace.from_config()
  print("Using Config File")
except Exception:
  ws = Workspace(workspace_name = workspace_name,
               subscription_id = subscription_id,
               resource_group = resource_group)
  print("Unable to find config")

# COMMAND ----------

from azureml.core.model import Model
run = [x for x in ws.experiments['gbt-turbofan'].get_runs()][0]
model_name = "gbt-turbofan"
print(run)

mymodel = run.register_model(model_name = "gbt-turbofan", model_path = "gbt_turbofan.mml")


# COMMAND ----------

#Register the model

print(mymodel.name, mymodel.description, mymodel.version)

# COMMAND ----------

score_sparkml = """
import json
import pyspark
import os
from azureml.core.model import Model
from pyspark.ml import Pipeline, PipelineModel
from pyspark.sql import SQLContext
from pyspark import SparkContext
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.feature import VectorAssembler, VectorIndexer
import pandas as pd

sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)
spark = sqlContext.sparkSession
 
def init():
    # One-time initialization of PySpark and predictive model
   
 
    global trainedModel
    #global spark
 
    #spark = pyspark.sql.SparkSession.builder.appName("ADB and AML notebook by Jonathan").getOrCreate()
    #model_name = "{model_name}" #interpolated
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # For multiple models, it points to the folder containing all deployed models (./azureml-models)
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'gbt_turbofan.mml')    
    #model_path = Model.get_model_path('gbt_turbofan.mml')
   
    trainedModel = PipelineModel.load(model_path)
    
def run(input_json):
    if isinstance(trainedModel, Exception):
        return json.dumps({{"trainedModel":str(trainedModel)}})
      
    try:
        sc = spark.sparkContext
        df_pd = pd.read_json(json.loads(input_json),orient='records')
        input_df = spark.createDataFrame(df_pd)
        #input_list = json.loads(input_json)
        #input_rdd = sc.parallelize(input_list)
        #input_df = spark.read.json(input_rdd)
    
        # Compute prediction
        prediction = trainedModel.transform(input_df)
        #result = prediction.first().prediction
        predictions = prediction.collect()
 
        #Get each scored result
        preds = [str(x['prediction']) for x in predictions]
        result = ",".join(preds)
        # you can return any data type as long as it is JSON-serializable
        return result
    except Exception as e:
        result = str(e)
        return result
    
""".format(model_name='gbt_turbofan.mml')
 
exec(score_sparkml)
 
with open("score_sparkml.py", "w") as file:
    file.write(score_sparkml)

# COMMAND ----------

from azureml.core.conda_dependencies import CondaDependencies 

myacienv = CondaDependencies.create(conda_packages=['scikit-learn','numpy','pandas']) #showing how to add libs as an eg. - not needed for this model.

with open("mydeployenv.yml","w") as f:
    f.write(myacienv.serialize_to_string())

# COMMAND ----------

from azureml.core.webservice import AciWebservice, Webservice
from azureml.exceptions import WebserviceException
from azureml.core.model import InferenceConfig
from azureml.core.environment import Environment
from azureml.core.conda_dependencies import CondaDependencies 


# Remove any existing service under the same name.
try:
    Webservice(ws, webservice_name).delete()
except WebserviceException:
    pass

env = Environment.get(ws, name='AzureML-PySpark-MmlSpark-0.15')

inference_config = InferenceConfig(entry_script="score_sparkml.py",
                                   environment = env
                                   )

deployment_config = AciWebservice.deploy_configuration(cpu_cores = 1, memory_gb = 1,auth_enabled=True)


#image_config = ContainerImage.image_configuration(execution_script = "score_sparkml.py", 
#                                    runtime = "spark-py", 
#                                    conda_file = "mydeployenv.yml")

myservice = Model.deploy(ws, webservice_name, [mymodel], inference_config, deployment_config)

#myservice = Model.deploy(ws, webservice_name, [mymodel], inference_config, myaci_config)
myservice.wait_for_deployment(show_output=True)

# COMMAND ----------


print(myservice.get_keys())
print(myservice.scoring_uri)

# COMMAND ----------

key =myservice.get_keys()[0]

df = spark.read.table('TurboFanData')
train = df.toPandas()
sampleSize = round(5/len(train),4)
testdf = train.sample(frac=sampleSize)

X = testdf.drop('rul',axis=1)
y = testdf.rul.tolist()

input_data = json.dumps(X.to_json( orient='records')) # Create JSON of sample records    

headers = {'Content-Type':'application/json'}

#for AKS deployment you'd need to the service key in the header as well    
headers = {'Content-Type':'application/json',  'Authorization':('Bearer '+ key)} 

resp = myservice.run(input_data=input_data)

print(resp)