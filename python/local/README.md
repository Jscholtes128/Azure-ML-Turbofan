
## About


## Set-up you local environment
[Configure a development environment for Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-environment#local)

## Python files for data prep, train, track expereiements, and deploy model:

- [01-dataprep.py](01-dataprep.py)
<br/> Download Turbofan data, unzip, add RUL (remaining useful life) column and save as csv
- 02-train.py
<br/> Gradient Boost Regression Model to predict RUL, - pure local machine example
- 03-train_logging.py
<br/> Extend *02-train* to track training experiments with Azure Machine Learning Service
- 04-deploy_model.py
<br/> Deploy the _last_ experiement in Azure ML to a RESTful endppoint running on Azure Container Instance
- 05-test_web_service.py

## Resource Files
- turbofan.yml
- score.py
- aml_config.json ([config](config/) directory)
