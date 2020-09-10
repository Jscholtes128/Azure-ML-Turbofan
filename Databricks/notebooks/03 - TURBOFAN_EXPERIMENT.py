# Databricks notebook source
# MAGIC %md ### Track NASA Turbofan Model with Azure Machine Learning Service 

# COMMAND ----------

# MAGIC %md Use [widgets](https://docs.azuredatabricks.net/user-guide/notebooks/widgets.html) to capture model input params and to enable Azure Machine Learning MLFlow integration

# COMMAND ----------

import mlflow

# COMMAND ----------

## Create widgets for model input params and to enable Azure Machine Learning MLFlow integration

dbutils.widgets.text("maxDepth","5","maxDepth")
dbutils.widgets.text("maxIter","5","maxIter")

maxDepth = int(dbutils.widgets.get("maxDepth"))
maxIter = int(dbutils.widgets.get("maxIter"))

dbutils.widgets.dropdown("useAMLS","False",["True","False"],"Use AMLs:")
useAMLs = (dbutils.widgets.get("useAMLS") == 'True')

# COMMAND ----------

import azureml.core
import os
import shutil

from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from pyspark.ml import Pipeline
from azureml.core.webservice import AciWebservice, Webservice


from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import GBTRegressor

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

df = spark.read.table('TurboFanData')

# COMMAND ----------

train, test = df.randomSplit([0.7, 0.3])

# COMMAND ----------

from pyspark.ml.feature import VectorAssembler, VectorIndexer
featuresCols = df.columns
featuresCols.remove('rul')

# This concatenates all feature columns into a single feature vector in a new column "rawFeatures".
vectorAssembler = VectorAssembler(inputCols=featuresCols, outputCol="rawFeatures")
# This identifies categorical features and indexes them.
vectorIndexer = VectorIndexer(inputCol="rawFeatures", outputCol="features", maxCategories=4)

# COMMAND ----------

dbutils.fs.rm('dbfs:/gbt_turbofan.mml',True)

# COMMAND ----------

model_name = "gbt_turbofan.mml"
model_dbfs = os.path.join("/dbfs/", model_name)

experiment = Experiment(ws, 'gbt-turbofan')

run =  experiment.start_logging()
run.tag('compute','databricks')


# Log Run Params
run.log('maxIter', maxIter)
run.log('maxDepth', maxDepth)

gbt = GBTRegressor(labelCol="rul",featuresCol="features",maxDepth=maxDepth,)

paramGrid = ParamGridBuilder()\
  .addGrid(gbt.maxDepth, [2,maxDepth])\
  .addGrid(gbt.maxIter, [2,maxIter])\
  .build()

evaluator = RegressionEvaluator(metricName="mae", labelCol=gbt.getLabelCol(), predictionCol=gbt.getPredictionCol())

cv = CrossValidator(estimator=gbt, evaluator=evaluator, estimatorParamMaps=paramGrid)
pipeline = Pipeline(stages=[vectorAssembler, vectorIndexer, cv])
model = pipeline.fit(train)

predictions = model.transform(test)

## Log MAE and model
mae = evaluator.evaluate(predictions)
run.log("mae",mae)
print("Test Error = %g" % mae)

# save model
model.write().overwrite().save(model_name)

# upload the serialized model into run history record
mdl, ext = model_name.split(".")
model_zip = mdl + ".zip"
#shutil.make_archive(mdl, 'zip', model_dbfs)
#run.upload_file(model_name, model_zip)  
run.upload_folder(model_name,path=model_dbfs)
#run.upload_file("outputs/" + model_name, path_or_stream = model_dbfs) #cannot deal with folders

# now delete the serialized model from local folder since it is already uploaded to run history 
#shutil.rmtree(model_dbfs)
#os.remove(model_zip)
        
run.complete()