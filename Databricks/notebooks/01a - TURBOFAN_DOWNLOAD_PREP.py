# Databricks notebook source
# MAGIC %md 
# MAGIC ##NASA Turbofan Data Prep

# COMMAND ----------

# MAGIC %md ### Acquire and Prepare Data
# MAGIC For this notebook, we will use the NASA Prognostics Center's Turbo-Fan Failure dataset.
# MAGIC It is located here: https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/#turbofan

# COMMAND ----------

import logging
import numpy as np
import pandas as pd
# import needed libraries for downloading and unzipping the file
import urllib.request
from zipfile import ZipFile

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC DROP TABLE TurboFanData

# COMMAND ----------

# MAGIC %md Download and un-zip the data

# COMMAND ----------

# download from url
response = urllib.request.urlopen("https://ti.arc.nasa.gov/c/6/")
output = open('CMAPSSData.zip', 'wb')    # note the flag:  "wb"        
output.write(response.read())
output.close()

# COMMAND ----------

# unzip files
zipfile = ZipFile("CMAPSSData.zip")
zipfile.extract("train_FD001.txt")

# COMMAND ----------

# MAGIC %md Read data into a Pandas DataFrame.<br/>
# MAGIC Note the headers were not in the space seperated txt file, they are assigned from them from the ReadMe in the zip file.  Use Pandas read_csv with the delimiter option.

# COMMAND ----------

train = pd.read_csv("train_FD001.txt", delimiter="\s|\s\s", index_col=False, engine='python', names=['unit','cycle','os1','os2','os3','sm1','sm2','sm3','sm4','sm5','sm6','sm7','sm8','sm9','sm10','sm11','sm12','sm13','sm14','sm15','sm16','sm17','sm18','sm19','sm20','sm21'])

# COMMAND ----------

# MAGIC %md Take a quick look at the data

# COMMAND ----------

train.head(5)

# COMMAND ----------

# MAGIC %md Our dataset has a number of units in it, with each engine flight listed as a cycle. The cycles count up until the engine fails. What we would like to predict is the number of cycles until failure. 
# MAGIC So we need to calculate a new column called **RUL**, or **Remaining Useful Life**.  It will be the last cycle value minus each cycle value per unit.

# COMMAND ----------

# Assign ground truth
def assignrul(df):
    maxi = df['cycle'].max()
    df['rul'] = maxi - df['cycle']
    return df
    

train_new = train.groupby('unit').apply(assignrul)

# Display Columns
train_new.columns

# COMMAND ----------

# MAGIC %md Dataframe now has the 'RUL' column.  

# COMMAND ----------

train_new.head(5)

# COMMAND ----------

# MAGIC %md Create PySpark Dataframe from pandas Dataframe, condense partitions (files) and save to table for additional Notebook use

# COMMAND ----------

df = spark.createDataFrame(train_new)
df.write.mode('overwrite').saveAsTable('TurboFanData')

# COMMAND ----------

# MAGIC %sql
# MAGIC REFRESH TABLE TurboFanData

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC SELECT * FROM TurboFanData

# COMMAND ----------

# MAGIC %fs
# MAGIC 
# MAGIC ls dbfs:/user/hive/warehouse/turbofandata