from azureml.core import Environment
from azureml.core import ScriptRunConfig
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.core.runconfig import RunConfiguration
import json

with open("./..aml_config.json") as f:
    config = json.load(f)

workspace_name = config["workspace_name"]
resource_group = config["resource_group"]
subscription_id = config["subscription_id"]
workspace_region = config["location"]


#Interactive Authentication
ws = Workspace(workspace_name = workspace_name,
               subscription_id = subscription_id,
               resource_group = resource_group)

local_run = RunConfiguration()

# Editing a run configuration property on-fly.
#user_managed_env = Environment("user-managed-env")

local_run.environment.python.user_managed_dependencies = True


############# Experiement local-gbr-turbofan ######################
experiement_name = 'local-gbr-turbofan'


exp = Experiment(workspace=ws, name=experiement_name)
src = ScriptRunConfig(source_directory='./', script='04-train_runconfig.py',run_config=local_run)

run = exp.submit(src)

run.wait_for_completion(show_output = True)
