# Example 3: Azure Machine Learning Notebooks

![ds design](../images/datascience.png)

In this example we are going to use Azure Machine Learning Notebooks to create our ML remaining useful life model. The data ingestion step will source a versioned dataset using Azure Machine Learning Datastore.

## 1. Turbofan Dataset

### 1.1 Create Azure ML Dataset


![ds design](../images/datasets.jpg)

Go to Azure ML Datasets and **create a dataset** **From local files**

![ds design](../images/create_dataset.jpg)

Create a **Tabular** dataset with a relevant name.

![ds design](../images/dataset_basic.jpg)

Select the downloaded *turbofan.csv* file as your source data.

![ds design](../images/dataset_file.jpg)

Use **comma delimited** and specify to *Use headers from the first file*

![ds design](../images/dataset_settings.jpg)

Keep the default schema and click **create** on the confirmation screen.


## 2. Create Azure Machine Learning Notebook