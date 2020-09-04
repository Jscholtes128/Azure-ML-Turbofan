# Azure Machine Learning Examples - Predicting Remaining Useful Life of TurboFan

![ds design](/images/datascience.png)


## Example 6: Azure Machine Learning & Databricks

### Contents

## 1. Preparation

-- Create Cluster for Azure 




## 2. Data Load

### 2 Set-up Secret Store with Azure Key Vault

Azure Key Vault can be used to Securely store and tightly control access to tokens, passwords, certificates, API keys, and other secrets

#### 2.1.1 Create an Azure Key Vault - Use Azure CLI

```bash
keyVaultName=churnhackaVault-$RANDOM
az keyvault create --name $keyVaultName --resource-group $resourceGroupName --location $location
```

#### 2.1.2 Create an Azure Key Vault - Use Azure Portal

[Create an Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/quick-create-portal#create-a-vault)

### 2.2 Create a Secret and Secret scope for Azure Storage Account

#### 2.2.1 Get Storage Account Key

Copy Storage account name and key 1 to a text editor for later use in this tutorial.
![account key](../images/storage-access-keys.png)

#### 2.2.2 Create Azure Key Vault Secret

Navigate to your newly created key vault in the Azure portal and select Secrets. Then, select + Generate/Import.

![import key](../images/generate-import-secrets.png)

On the Create a secret page, provide the following information, and keep the default values for the remaining fields:

|Property|Value|
|---------------|--------------------------------------------|
|Upload options|Manual|
|Name| Friendly name for your storage account key.|
|Value|key1 from your storage account.|

![create secret](../images/create-storage-secret.png)

Save the key name in a text editor for use later in this tutorial, and select Create. Then, navigate to the Properties menu. Copy the DNS Name and Resource ID to a text editor for use later in the tutorial.

![copy resources](../images/copy-dns-resource.png)

#### 2.2.3 Create Azure Databricks Secret Scope

Navigate to your newly created Azure Databricks resource in the Azure portal and select Launch Workspace.

![launch workspace](../images/launch-databricks-workspace.png)

Once your Azure Databricks workspace is open in a separate window, append #secrets/createScope to the URL. The URL should have the following format:
__https://<\location>.azuredatabricks.net/?o=<\orgID>#secrets/createScope.__

Enter a scope name, and enter the Azure Key Vault DNS name and Resource ID you saved earlier. Save the scope name in a text editor for use later in this tutorial. Then, select Create.

![create scope](../images/create-secret-scope.png)

### 2.3 Mounting Azure Storage Account with Azure Databricks

#### 2.3.1 Create Databricks Cluster

From the home page of your Azure Databricks workspace, select New Cluster under Common Tasks.

![create cluster](../images/create-new-cluster.png)

Enter a cluster name and select Create cluster. The cluster creation takes a few minutes to complete.

#### 2.3.2 Create Databricks Notebook

Once the cluster is created, navigate to the home page of your Azure Databricks workspace, select New Notebook under Common Tasks. This will be the Notebook for the initial __Data Load__.

![create notebook](../images/create-new-notebook.png)

Enter a notebook name (_Data Load_ or _01-Data Load_ or something similar), and set the language to Python. Set the cluster to the name of the cluster you created in the previous step.

### 2.4 Loading Turbofan Data using Mount

#### 2.4.1 Mount Storage Account

Mount the Azure Storage Account where the turbofan  CSV is stored; pass the recently created __secret scope__ and __secret__.

##### 2.4.1.1 Example Mount

Example mounting Azure Storage Account

```python
dbutils.fs.mount(
source = "wasbs://<your-container-name>@<your-storage-account-name>.blob.core.windows.net",
mount_point = "/mnt/<mount-name>",
extra_configs = {"<conf-key>":dbutils.secrets.get(scope = "<scope-name>", key = "<key-name>")})
```

* __mount-name__ is a DBFS path representing where the Blob Storage container or a folder inside the container (specified in source) will be mounted.
* __conf-key__ can be either fs.azure.account.key.<\your-storage-account-name>.blob.core.windows.net or fs.azure.sas.<\your-container-name>.<\your-storage-account-name>.blob.core.windows.net
* __scope-name__ is the name of the secret scope you created in the previous section.
* __key-name__ is the name of they secret you created for the storage account key in your key vault.

##### 2.4.1.2 Turbofan Mount

```python
if not(True in [x.mountPoint == '/mnt/turbofan' for x in dbutils.fs.mounts()]):
    dbutils.fs.mount(
    source = "wasbs://data@<your-storage-account-name>blob.core.windows.net",
    mount_point = "/mnt/turbofan",
    extra_configs = {"fs.azure.account.key.<your-storage-account-name>.blob.core.windows.net":dbutils.secrets.get(scope = "examplescope", key = "turbofan")})
```

#### 2.4.1 Load Turbofan Data

Read the csv data into a pyspark Dataframe and save as a table for use in additional NoteBooks.

```python
df = spark.read.csv("/mnt/turbofan/turbofan.csv",header=True,inferSchema=True)
df.write.mode('overwrite').saveAsTable('TurboFanData')
```

View  Data

![select customers](../images/select_customer_churn.PNG)




