# Databricks notebook source
# MAGIC %md ## Azure Machine Learning Service, Experiment, AutoML, Deployment</br>
# MAGIC Run an experiment for Azure Machine Learning Service [Automated ML](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-automated-ml) to find 'best model' for deployment to Azure Container Instance (ACI)<br/><br/>
# MAGIC 
# MAGIC #### [Configure Azure Databricks for AutoML](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-environment#azure-databricks)

# COMMAND ----------

dbutils.library.installPyPI("xgboost")
dbutils.library.restartPython()

# COMMAND ----------

from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.train.automl import AutoMLConfig
from azureml.train.automl.run import AutoMLRun
import logging
from azureml.core.webservice import AciWebservice, Webservice
from azureml.core.image import ContainerImage

# COMMAND ----------

import os

project_folder = './sample_projects/automl-demo-predmain'


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

# MAGIC %md Create *automl-predictive-rul* experiment for Regressive AutoML using the Nasa Turbofan data 

# COMMAND ----------

experiment_name = 'automl-predictive-rul'
experiment = Experiment(ws, experiment_name)

# COMMAND ----------

from azureml.core import Dataset

df = spark.read.table('TurboFanData')
training_data = df.toPandas()
dbutils.fs.mkdirs('dbfs:/data')
training_data.to_csv('/dbfs/data/temp.csv')
ds = ws.get_default_datastore()
ds.upload(src_dir='/dbfs/data', target_path='tempdata', overwrite=True, show_progress=True)

training_data = Dataset.Tabular.from_delimited_files(path=ds.path('tempdata/temp.csv'))
label = 'rul'

# COMMAND ----------

import azureml.dataprep as dprep
import uuid
#x_prep = df.drop('rul').toPandas()
#y_prep = df.select('rul').toPandas()
#x_prep = dprep.read_pandas_dataframe(df.drop('rul').toPandas(),temp_folder='/dbfs/tmp'+str(uuid.uuid4()))
#y_prep  = dprep.read_pandas_dataframe(df.select('rul').toPandas(),temp_folder='/dbfs/tmp'+str(uuid.uuid4()))

# COMMAND ----------

#x_prep = x_prep
#y_prep = y_prep.to_long(dprep.ColumnSelector(term='.*', use_regex = True))

# COMMAND ----------

# MAGIC %md ## Configure Automated ML
# MAGIC 
# MAGIC You can use these params.
# MAGIC 
# MAGIC |Property|Description|
# MAGIC |-|-|
# MAGIC |**task**|classification or regression|
# MAGIC |**primary_metric**|This is the metric that you want to optimize. Classification supports the following primary metrics: <br><i>accuracy</i><br><i>AUC_weighted</i><br><i>average_precision_score_weighted</i><br><i>norm_macro_recall</i><br><i>precision_score_weighted</i>|
# MAGIC |**primary_metric**|This is the metric that you want to optimize. Regression supports the following primary metrics: <br><i>spearman_correlation</i><br><i>normalized_root_mean_squared_error</i><br><i>r2_score</i><br><i>normalized_mean_absolute_error</i>|
# MAGIC |**iteration_timeout_minutes**|Time limit in minutes for each iteration.|
# MAGIC |**iterations**|Number of iterations. In each iteration AutoML trains a specific pipeline with the data.|
# MAGIC |**n_cross_validations**|Number of cross validation splits.|
# MAGIC |**spark_context**|Spark Context object. for Databricks, use spark_context=sc|
# MAGIC |**max_concurrent_iterations**|Maximum number of iterations to execute in parallel. This should be <= number of worker nodes in your Azure Databricks cluster.|
# MAGIC |**X**|(sparse) array-like, shape = [n_samples, n_features]|
# MAGIC |**y**|(sparse) array-like, shape = [n_samples, ], [n_samples, n_classes]<br>Multi-class targets. An indicator matrix turns on multilabel classification. This should be an array of integers.|
# MAGIC |**path**|Relative path to the project folder. AutoML stores configuration files for the experiment under this folder. You can specify a new empty folder.|
# MAGIC |**preprocess**|set this to True to enable pre-processing of data eg. string to numeric using one-hot encoding|
# MAGIC |**exit_score**|Target score for experiment. It is associated with the metric. eg. exit_score=0.995 will exit experiment after that|

# COMMAND ----------

from azureml.core.compute import AmlCompute
from azureml.core.compute import ComputeTarget
import time

cpu_cluster_name = "js-aml-compute"

# Verify that cluster does not exist already
try:
    cpu_cluster = ComputeTarget(workspace=ws, name=cpu_cluster_name)
    print('Found existing cluster, use it.')
except ComputeTargetException:
    compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_D2_V2',
                                                           max_nodes=4)
    cpu_cluster = ComputeTarget.create(ws, cpu_cluster_name, compute_config)
    
automl_settings = {
    "name": "automl-predictive-rul_{0}".format(time.time()),
    "experiment_timeout_minutes" : 20,
    "enable_early_stopping" : True,
    "iteration_timeout_minutes": 2,
    "n_cross_validations": 5,
    "primary_metric": 'r2_score',
    "max_concurrent_iterations": 6,
}

automl_config = AutoMLConfig(task='regression',
                             debug_log='automl_errors.log',
                             path=project_folder,
                             compute_target=cpu_cluster,
                             #spark_context=sc,
                             training_data=training_data,
                             label_column_name=label,
                             **automl_settings,
                             featurization='auto',
                             experiment_exit_score = .98
                             )



# COMMAND ----------

# MAGIC %md Submit the experiment to Automated ML service. This step can take longer depending on the settings. AutoML will give us updates as models are trained and evaluated by the metric we specified above. The information from each ML model training will be stored in the Experiment section of the Azure ML Workspace in Azure Portal.

# COMMAND ----------

# DBTITLE 1,Submit run to your Databricks cluster
local_run = experiment.submit(automl_config, show_output = True) # for higher runs please use show_output=False and use the below

# COMMAND ----------

# DBTITLE 1,Monitor progress in the portal
displayHTML("<a href={} target='_blank'>Your experiment in Azure Portal: {}</a>".format(local_run.get_portal_url(), local_run.id))

# COMMAND ----------

# MAGIC %md **Run After AutoML Experiement is Complete**

# COMMAND ----------

# MAGIC %md We want to keep the best model and deploy it as a service.

# COMMAND ----------

#find the run with the highest accuracy value.
best_run, fitted_model = local_run.get_output()

# COMMAND ----------

#View best run properties, model, params, etc.
details = best_run.get_details()
details['properties']