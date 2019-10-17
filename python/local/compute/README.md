With Azure Machine Learning, you can train your model on a variety of resources or environments, collectively referred to as compute targets.

## Prerequisites
- [Configure a development environment for Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-environment#local)
- [Set up and use compute targets for model training](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-set-up-training-targets)


## Python File for Local and Remote Compute:

### [01-train.py](01-train.py)
Training script used by both local and remote runs. Use [ScriptRunConfig](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-track-experiments#option-2-use-scriptrunconfig) to track experiments when running on different resources.
### [02-train_local_env.py](02-train_local_env.py)
Run 01-train script using local resources
### [03-train_remote.py](03-train_remote.py)
Run 01-train script using Azure ML Compute resources (VM: STANDARD_D2_V2, Max Nodes:2)
