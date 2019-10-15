
## About


## Set-up you local environment
[Configure a development environment for Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-environment#local)

## Python files for data prep, train, track expereiements, and deploy model:

- 01-dataprep.py: Download Turbofan data, unzip, add RUL (remaining useful life) column and save as csv
- 02-train.py: Local Gradient Boost
- 03-train_logging.py
- 04-deploy_model.py
- 05-test_web_service.py

## Resource Files
- turbofan.yml
- score.py
- aml_config.json ([config](config/) directory)
