## Create Azure ML Pipeline to train and deploy model
##

import azureml.core
from azureml.core import Workspace, Datastore,Environment
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineData
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline
from azureml.core import Experiment
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import RunConfiguration
import json

from azureml.core.authentication import AzureCliAuthentication

cli_auth = AzureCliAuthentication()

################ Workspace ##############################
with open("./../config/aml_config.json") as f:
    config = json.load(f)

workspace_name = config["workspace_name"]
resource_group = config["resource_group"]
subscription_id = config["subscription_id"]
workspace_region = config["location"]

#Interactive Authentication
ws = Workspace(workspace_name = workspace_name,
               subscription_id = subscription_id,
               resource_group = resource_group,
                auth=cli_auth)



###########  Set-up Data Store ######################
# Default datastore 
def_data_store = ws.get_default_datastore()

# Get the blob storage associated with the workspace
def_blob_store = Datastore(ws, "workspaceblobstore")


def_blob_store.upload_files(
    ["./../data/turbofan.csv"],
    target_path="data",
    overwrite=True)

def_blob_store.upload_files(
    ["./../score.py"],
    target_path=".",
    overwrite=True)

def_blob_store.upload_files(
    ["./../turbofan.yml"],
    target_path=".",
    overwrite=True)

def_blob_store.upload_files(
    ["./../config/aml_config.json"],
    target_path="config",
    overwrite=True)



blob_input_data = DataReference(
    datastore=def_blob_store,
    data_reference_name="train_data",
    path_on_datastore="data/turbofan.csv")


input_config = DataReference(
    datastore=def_blob_store,
    data_reference_name="config_file",
    path_on_datastore="config/aml_config.json")


output_data1 = PipelineData(
    "output_data1",
    datastore=def_blob_store,
    output_name="output_data1")


###################### Set-Up Compute ######################

cpu_cluster_name = "js-aml-compute"

try:
    cpu_cluster = ComputeTarget(workspace=ws, name=cpu_cluster_name)
    print('Found existing cluster, use it.')
except ComputeTargetException:
    print('Creating a new compute target...')
    compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_D2_V2',
                                                           max_nodes=4)
    cpu_cluster = ComputeTarget.create(ws, cpu_cluster_name, compute_config)

    cpu_cluster.wait_for_completion(show_output=True)

    # For a more detailed view of current cluster status, use the 'status' property
    print(cpu_cluster.status)
    
aml_run_config = RunConfiguration()

# Use the aml_compute you created above. 
aml_run_config.target = cpu_cluster

# Enable Docker
aml_run_config.environment.docker.enabled = True

# Set Docker base image to the default CPU-based image
aml_run_config.environment.docker.base_image = "mcr.microsoft.com/azureml/base:0.2.1"

# Use conda_dependencies.yml to create a conda environment in the Docker image for execution
aml_run_config.environment.python.user_managed_dependencies = False

# Auto-prepare the Docker image when used for execution (if it is not already prepared)
aml_run_config.auto_prepare_environment = True

# Specify CondaDependencies obj, add necessary packages
aml_run_config.environment.python.conda_dependencies = CondaDependencies.create(
    conda_packages=['pandas','scikit-learn==0.20.2'], 
    pip_packages=['azureml-sdk', 'numpy'], 
    pin_sdk_version=False)
    
    
############# Build Pipeline ################################
    
pipeline_param_max_depth = PipelineParameter(
  name="max_depth",
  default_value=3)

pipeline_param_n_estimators = PipelineParameter(
  name="n_estimators",
  default_value=2000)



    
trainStep = PythonScriptStep(
    script_name="pipeline_train.py",
     arguments=["--max_depth", pipeline_param_max_depth,"--n_estimators",pipeline_param_n_estimators,"--input", blob_input_data,"--output_train",output_data1],   
    inputs=[blob_input_data],
    outputs=[output_data1],
    compute_target=cpu_cluster,
    runconfig=aml_run_config,
    source_directory=".",
    allow_reuse=False
)


deployStep = PythonScriptStep(
    script_name="pipeline_deploy.py",
     arguments=["--output_train",output_data1,"--input_config", input_config],   
    inputs=[input_config,output_data1],
    compute_target=cpu_cluster,
    runconfig=aml_run_config,
    source_directory=".",
    allow_reuse=False
)

deployStep.run_after(trainStep)



# list of steps to run
trainDeployModel = [deployStep]


# Build the pipeline
pipeline1 = Pipeline(workspace=ws, steps=[trainDeployModel])

################# Run and Deploy Pipeline ##############################

# Submit the pipeline to be run
pipeline_run1 = Experiment(ws, 'Train_Deploy_Turbofan_Exp').submit(pipeline1)
pipeline_run1.wait_for_completion()

published_pipeline1 = pipeline_run1.publish_pipeline(
     name="Turbofan_Published_Pipeline",
     description="Train Deploy Turbofan Pipeline",
     version="1.0")



