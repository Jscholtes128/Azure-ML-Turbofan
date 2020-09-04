# Azure Machine Learning Examples - Predicting Remaining Useful Life of TurboFan

![ds design](/images/datascience.png)

## Familiar Data Science Tools

## [How Azure Machine Learning works: Architecture and concepts](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture)
Learn about the architecture, concepts, and workflow for Azure Machine Learning

![workflow](../../images/workflow.png)


## Prerequisites
Set-up on Azure Portal:
<br/>[Create and manage Azure Machine Learning workspaces in the Azure portal(https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-manage-workspace)
<br/>Set-up you local environment:
<br/>[Configure a development environment for Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-environment#local)

## Python files for data prep, train, track experiments, and deploy model:

### [01-dataprep.py](01-dataprep.py)
Download Turbofan data, unzip, add RUL (remaining useful life) column and save as csv
### [02-train.py](02-train.py)
Gradient Boost Regression Model to predict RUL, - pure local machine example
### [03-train_logging.py](03-train_logging.py)
Extend *02-train* to track training experiments with Azure Machine Learning Service
<br/> __Resources:__
<br/>[Monitor Azure ML experiment runs and metrics](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-track-experiments#available-metrics-to-track)
### [04-deploy_model.py](04-deploy_model.py)
Deploy the _last_ experiment in Azure ML to a RESTful endpoint running on Azure Container Instance
<br/> ___Resources:___ 
<br/> [Deploy models with Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-deploy-and-where)
<br/>[Deploy a model to Azure Container Instances](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-deploy-azure-container-instance)
### [05-test_web_service.py](05-test_web_service.py)
Test deployed model with web service endpoint URI.
<br/> ___Resources:___ 
<br/> [Consume an Azure Machine Learning model deployed as a web service](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-consume-web-service)


## Resource Files
### [turbofan.yml](turbofan.yml)
Conda dependency file for deployment image
### [score.py](score.py)
Scoring file used for model inferencing from web service.
### [aml_config.json](config/aml_config.json) ([config](config/) directory)
Global configurations for connecting to Azure Machine Learning Workspace
<br/> **Please update aml_config.json to use your workspace**
