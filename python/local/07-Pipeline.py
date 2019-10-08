# -*- coding: utf-8 -*-

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



###########  Set-up Data Store ######################
# Default datastore 
def_data_store = ws.get_default_datastore()

# Get the blob storage associated with the workspace
def_blob_store = Datastore(ws, "workspaceblobstore")


def_blob_store.upload_files(
    ["./data/turbofan.csv"],
    target_path="data",
    overwrite=True)

def_blob_store.upload_files(
    ["score.py"],
    target_path=".",
    overwrite=True)

def_blob_store.upload_files(
    ["my.yml"],
    target_path=".",
    overwrite=True)

def_blob_store.upload_files(
    ["aml_config.json"],
    target_path=".",
    overwrite=True)



blob_input_data = DataReference(
    datastore=def_blob_store,
    data_reference_name="train_data",
    path_on_datastore="data/turbofan.csv")


output_data1 = PipelineData(
    "output_data1",
    datastore=def_blob_store,
    output_name="output_data1")


###################### Set-Up Compute ######################

compute_name = "aml-compute"
vm_size = "STANDARD_D2_V2"
if compute_name in ws.compute_targets:
    compute_target = ws.compute_targets[compute_name]
    if compute_target and type(compute_target) is AmlCompute:
        print('Found compute target: ' + compute_name)
else:
    print('Creating a new compute target...')
    provisioning_config = AmlCompute.provisioning_configuration(vm_size=vm_size,  # STANDARD_NC6 is GPU-enabled
                                                                min_nodes=1,
                                                                max_nodes=2)
    # create the compute target
    compute_target = ComputeTarget.create(
        ws, compute_name, provisioning_config)
    
    # Can poll for a minimum number of nodes and for a specific timeout.
    # If no min node count is provided it will use the scale settings for the cluster
    compute_target.wait_for_completion(
        show_output=True, min_node_count=None, timeout_in_minutes=20)

    # For a more detailed view of current cluster status, use the 'status' property
    print(compute_target.status)
    
aml_run_config = RunConfiguration()

# Use the aml_compute you created above. 
aml_run_config.target = compute_target

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
    script_name="06-Pipeline_Train.py",
     arguments=["--max_depth", pipeline_param_max_depth,"--n_estimators",pipeline_param_n_estimators],   
    inputs=[blob_input_data],
   # outputs=[output_data1],
    compute_target=compute_target,
    runconfig=aml_run_config,
    source_directory="."
)


deployStep = PythonScriptStep(
    script_name="04-deploy_model.py",
    compute_target=compute_target,
    runconfig=aml_run_config,
    source_directory="."
)

deployStep.run_after(trainStep)



# list of steps to run
trainDeployModel = [deployStep]


# Build the pipeline
pipeline1 = Pipeline(workspace=ws, steps=[trainDeployModel])

# Submit the pipeline to be run
pipeline_run1 = Experiment(ws, 'Train_Deploy_Turbofan_Exp').submit(pipeline1)
pipeline_run1.wait_for_completion()

published_pipeline1 = pipeline_run1.publish_pipeline(
     name="Turbofan_Published_Pipeline",
     description="Train Deploy Turbofan Pipeline",
     version="1.0")



