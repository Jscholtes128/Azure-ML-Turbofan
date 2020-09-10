## Register model from last experiment 
## and deploy to Azure Container Instance
##

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

run = [x for x in ws.experiments['gbr-turbofan'].get_runs()][0]
run_metrics = run.get_metrics()

print(run)

model = run.register_model(model_name = "turbofan-rul", model_path = "outputs/model.pkl", tags={"mae":run_metrics["mae"],"python version": sys.version[0:6]})

deployment_config = AciWebservice.deploy_configuration(cpu_cores = 1, memory_gb = 1,auth_enabled=True)
#deployment_config = LocalWebservice.deploy_configuration(port=8890) ##deploy locally for testing

myenv = Environment(name="myenv")
conda_dep = CondaDependencies("turbofan.yml")
#conda_dep.add_conda_package("numpy")
#conda_dep.add_conda_package("scikit-learn")
# You must list azureml-defaults as a pip dependency
#conda_dep.add_pip_package("azureml-defaults")

myenv.python.conda_dependencies=conda_dep

inference_config = InferenceConfig(entry_script="score.py",
                                   environment=myenv)


#image_config = ContainerImage.image_configuration(execution_script = "score.py", 
                                   # runtime = "python", 
                                    #conda_file = "turbofan.yml")


try:
    service = Webservice(ws, webservice_name)        
    service.delete()    
except Exception as e:
    print("No Existing Service")

service = Model.deploy(ws, webservice_name, [model], inference_config, deployment_config)

#service.get_logs()


#service = Webservice.deploy_from_model(workspace=ws,
                                     #  name = webservice_name,
                                      # deployment_config = aci_config,
                                       #models = [model],
                                       #image_config = image_config)
service.wait_for_deployment(show_output = True)

print(service.get_keys())
print(service.scoring_uri)
