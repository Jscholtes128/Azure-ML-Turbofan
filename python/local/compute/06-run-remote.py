
from azureml.core import ScriptRunConfig
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.core.runconfig import RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
import json

with open("../aml_config.json") as f:
    config = json.load(f)

workspace_name = config["workspace_name"]
resource_group = config["resource_group"]
subscription_id = config["subscription_id"]
workspace_region = config["location"]

#Interactive Authentication
ws = Workspace(workspace_name = workspace_name,
               subscription_id = subscription_id,
               resource_group = resource_group)


aml_run_config = RunConfiguration()


aml_run_config.target = "amlcompute"

# AmlCompute is created in the same region as your workspace
# Set the VM size for AmlCompute from the list of supported_vmsizes
aml_run_config.amlcompute.vm_size = 'STANDARD_D2_V2'
aml_run_config.amlcompute._cluster_max_node_count = 2


# Specify CondaDependencies obj, add necessary packages
aml_run_config.environment.python.conda_dependencies = CondaDependencies.create(conda_packages=['scikit-learn'])

############# Experiement remote-gbr-turbofan ######################
experiement_name = 'remote-gbr-turbofan'


exp = Experiment(workspace=ws, name=experiement_name)
src = ScriptRunConfig(source_directory='./', script='04-train_runconfig.py',run_config=aml_run_config)

run = exp.submit(src)

run.wait_for_completion(show_output = True)
