## Use Azure ML Compute for cloud training
##

from azureml.core import ScriptRunConfig
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.core.runconfig import RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
import json
import sys

from azureml.core.authentication import AzureCliAuthentication

cli_auth = AzureCliAuthentication()

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

# Choose a name for your CPU cluster
cpu_cluster_name = "js-aml-compute"

# Verify that cluster does not exist already
try:
    cpu_cluster = ComputeTarget(workspace=ws, name=cpu_cluster_name)
    print('Found existing cluster, use it.')
except ComputeTargetException:
    compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_D2_V2',
                                                           max_nodes=4)
    cpu_cluster = ComputeTarget.create(ws, cpu_cluster_name, compute_config)

cpu_cluster.wait_for_completion(show_output=True)

aml_run_config = RunConfiguration()


aml_run_config.target = cpu_cluster_name

# AmlCompute is created in the same region as your workspace
# Set the VM size for AmlCompute from the list of supported_vmsizes
aml_run_config.amlcompute.vm_size = 'STANDARD_D2_V2'
aml_run_config.amlcompute._cluster_max_node_count = 2


# Specify CondaDependencies obj, add necessary packages
aml_run_config.environment.python.conda_dependencies = CondaDependencies("./../turbofan.yml")

 #CondaDependencies.create(conda_packages=['scikit-learn'])

############# Experiement remote-gbr-turbofan ######################
experiement_name = 'gbr-turbofan'


exp = Experiment(workspace=ws, name=experiement_name)
src = ScriptRunConfig(source_directory='./', script='01-train.py',run_config=aml_run_config)

run = exp.submit(src,tags={"python version": sys.version[0:6]})

run.wait_for_completion(show_output = True)
