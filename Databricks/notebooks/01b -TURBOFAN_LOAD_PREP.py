# Databricks notebook source
if not(True in [x.mountPoint == '/mnt/turbofan' for x in dbutils.fs.mounts()]):
    dbutils.fs.mount(
    source = "wasbs://turbofan@tempmodelstore.blob.core.windows.net",
    mount_point = "/mnt/turbofan",
    extra_configs = {"fs.azure.account.key.tempmodelstore.blob.core.windows.net":dbutils.secrets.get(scope = "turbofan", key = "turbofan")})

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC DROP TABLE TurboFanData

# COMMAND ----------

df = spark.read.csv('/mnt/turbofan',header=True,inferSchema=True)


# COMMAND ----------

df.write.mode('overwrite').saveAsTable('TurboFanData')

# COMMAND ----------

# MAGIC %sql
# MAGIC REFRESH TABLE TurboFanData

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC SELECT * FROM TurboFanData