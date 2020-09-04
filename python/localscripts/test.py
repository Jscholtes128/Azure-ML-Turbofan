from azureml.core.webservice import AciWebservice, Webservice
from azureml.core.image import ContainerImage
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.core.environment import Environment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.model import InferenceConfig,Model
import json
import sys
from azureml.core.webservice import LocalWebservice

### for VS Code (pip install azure-cli)
from azureml.core.authentication import AzureCliAuthentication

cli_auth = AzureCliAuthentication()


webservice_name = 'turbofan-rul'

################ Workspace ##############################
with open("./config/aml_config.json") as f:
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

run = [x for x in ws.experiments['gbr-turbofan'].get_runs()][0]
run_metrics = run.get_metrics()