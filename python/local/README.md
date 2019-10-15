
## About


## Set-up you local environment
[Configure a development environment for Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-environment#local)

## Python files for data prep, train, track expereiements, and deploy model:

#### [01-dataprep.py](01-dataprep.py)
<br/> Download Turbofan data, unzip, add RUL (remaining useful life) column and save as csv
#### [02-train.py](02-train.py)
<br/> Gradient Boost Regression Model to predict RUL, - pure local machine example
#### [03-train_logging.py](03-train_logging.py)
<br/> Extend *02-train* to track training experiments with Azure Machine Learning Service
<br/> __Resources:__
<br/>[Monitor Azure ML experiment runs and metrics](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-track-experiments#available-metrics-to-track)
#### [04-deploy_model.py](04-deploy_model.py)
<br/> Deploy the _last_ experiement in Azure ML to a RESTful endppoint running on Azure Container Instance
<br/> ___Resources:___ 
<br/> [Deploy models with Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-deploy-and-where)
<br/>[Deploy a model to Azure Container Instances](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-deploy-azure-container-instance)
#### [05-test_web_service.py](05-test_web_service.py)
<br/> Test deployed model with web service endpoint URI.


## Resource Files
- [turbofan.yml](turbofan.yml)
<br/> Conda dependancy file for deployment image
- [score.py](score.py)
<br/> Scoring file used for model inferencing from web service.
- [aml_config.json](config/aml_config.json) ([config](config/) directory)
</br> Global configurations for connecting to Azure Machine Learning Workspace
