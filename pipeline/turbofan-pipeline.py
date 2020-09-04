from azureml.core import Workspace
from azureml.core import Experiment
from azureml.pipeline.core import Pipeline
from azureml.data.data_reference import DataReference
from azureml.core.compute import AmlCompute, ComputeTarget
from modules.ingestion.data_ingestion_step import data_ingestion_step
from modules.preprocess.data_preprocess_step import data_preprocess_step
from modules.train.train_step import train_step
from modules.evaluate.evaluate_step import evaluate_step
from modules.deploy.deploy_step import deploy_step
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

datastore = ws.get_default_datastore()

# Create CPU compute target
print('Creating CPU compute target ...')
cpu_cluster_name = 'ds3cluster'
cpu_compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_DS3_V2', 
                                                           idle_seconds_before_scaledown=1200,
                                                           min_nodes=0, 
                                                           max_nodes=2)
cpu_compute_target = ComputeTarget.create(ws, cpu_cluster_name, cpu_compute_config)
cpu_compute_target.wait_for_completion(show_output=True)

datastore = DataReference(datastore, mode='mount')

# Step 1: Data ingestion 
data_ingestion_step, data_ingestion_outputs = data_ingestion_step(datastore, cpu_compute_target)

# Step 2: Data preprocessing 
data_preprocess_step, data_preprocess_outputs = data_preprocess_step(data_ingestion_outputs['raw_data_dir'], cpu_compute_target)

# Step 3: Train Model
train_step, train_outputs = train_step(data_preprocess_outputs['train_dir'], cpu_compute_target)

# Step 4: Evaluate Model
evaluate_step, evaluate_outputs = evaluate_step(train_outputs['model_dir'], data_preprocess_outputs['test_dir'], cpu_compute_target)

# Step 5: Deploy Model
deploy_step, deploy_outputs = deploy_step(train_outputs['model_dir'], evaluate_outputs['accuracy_file'], data_preprocess_outputs['test_dir'], cpu_compute_target)


# Submit pipeline
print('Submitting pipeline ...')
pipeline_parameters = {
    'max_depth': 5,
    'n_estimators': 500
}


# Submit pipeline
print('Submitting pipeline ...')

pipeline = Pipeline(workspace=ws, steps=[data_ingestion_step,data_preprocess_step,train_step,evaluate_step,deploy_step])
pipeline_run = Experiment(ws, 'turbofan-pipeline').submit(pipeline, pipeline_parameters=pipeline_parameters)

