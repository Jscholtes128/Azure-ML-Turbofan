## Azure Machine Learning DevOps (MLOPs)

Use [Azure Pipeline](https://azure.microsoft.com/en-us/services/devops/pipelines/) to automatically train and deploy machine learning models with Azure Machine Learning Service.
This example demonstrates a build pipeline to train a model on code check-in to GitHub.

## Prerequisites
Before you read this topic, you should understand [how the Azure Machine Learning service works.](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture)

Review the [Azure Machine Learning Service CI\CD How-to Guide](https://docs.microsoft.com/en-us/azure/devops/pipelines/targets/azure-machine-learning?context=azure%2Fmachine-learning%2Fservice%2Fcontext%2Fml-context&view=azure-devops&tabs=yaml)

![devops](../../../images/mlops_diagram.PNG)

The CI/CD Pipele in this example re-trains uses the file:
- [01-train.py](01-train.py)
