## Azure ML Turbo Fan 
This series of projects demonstrates how to quickly leverage Azure Machine Learning Services from an on-premise Python ML development environment. The code located under _local_ starts with a local train file and progresses to being able to track you experiment runs, leverage both local and Azure compute, register your model version and finally deploy your model as a RESTful service.

### Projects
- Using Azure Machine Learning Service (AML) Python SDK from [Local Environment](/)
   - Track local experiments using Azure Machine Learning Workspace
   - Register ML models and deploy to Azure Container Instance
- Using AML to change [compute targets](compute)
   - Train with both local and cloud compute
- Azure AI/ML & [MLOps](devops) (Pipelines and Azure DevOps)
   - Build and deploy an Azure Machine Learning [Pipeline](pipeline) for model traning, model registration and model deployment.
   - Scripts for CD/CD with Azure [DevOps](devops)

## [How Azure Machine Learning works: Architecture and concepts](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture)
Learn about the architecture, concepts, and workflow for Azure Machine Learning

![workflow](../../images/workflow.png)


## Prerequisites
Set-up on Azure Portal:
<br/>[Create and manage Azure Machine Learning workspaces in the Azure portal(https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-manage-workspace)
<br/>Set-up you local environment:
<br/>[Configure a development environment for Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-environment#local)

## Python files for data prep, train, track expereiements, and deploy model:

### [01-dataprep.py](01-dataprep.py)
Download Turbofan data, unzip, add RUL (remaining useful life) column and save as csv
### [02-train.py](02-train.py)
Gradient Boost Regression Model to predict RUL, - pure local machine example
### [03-train_logging.py](03-train_logging.py)
Extend *02-train* to track training experiments with Azure Machine Learning Service
<br/> __Resources:__
<br/>[Monitor Azure ML experiment runs and metrics](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-track-experiments#available-metrics-to-track)
### [04-deploy_model.py](04-deploy_model.py)
Deploy the _last_ experiement in Azure ML to a RESTful endppoint running on Azure Container Instance
<br/> ___Resources:___ 
<br/> [Deploy models with Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-deploy-and-where)
<br/>[Deploy a model to Azure Container Instances](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-deploy-azure-container-instance)
### [05-test_web_service.py](05-test_web_service.py)
Test deployed model with web service endpoint URI.
<br/> ___Resources:___ 
<br/> [Consume an Azure Machine Learning model deployed as a web service](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-consume-web-service)


## Resource Files
### [turbofan.yml](turbofan.yml)
Conda dependancy file for deployment image
### [score.py](score.py)
Scoring file used for model inferencing from web service.
### [aml_config.json](config/aml_config.json) ([config](config/) directory)
Global configurations for connecting to Azure Machine Learning Workspace
