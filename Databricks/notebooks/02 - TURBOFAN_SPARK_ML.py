# Databricks notebook source
# MAGIC %md ## Using Spark.ML for Turbofan RUL Prediction

# COMMAND ----------

# DBTITLE 1,Read Table Created in Step 1, Data Prep
df = spark.read.table('TurboFanData')

# COMMAND ----------

# MAGIC %md Create Pipeline for Vector Steps and GBTRegressor.

# COMMAND ----------

# 70 / 30 split for testing and training
train, test = df.randomSplit([0.7, 0.3])

# COMMAND ----------

from pyspark.ml.feature import VectorAssembler, VectorIndexer
featuresCols = df.columns
featuresCols.remove('rul')
# This concatenates all feature columns into a single feature vector in a new column "rawFeatures".
vectorAssembler = VectorAssembler(inputCols=featuresCols, outputCol="rawFeatures")
# This identifies categorical features and indexes them.
vectorIndexer = VectorIndexer(inputCol="rawFeatures", outputCol="features", maxCategories=4)

# COMMAND ----------

from pyspark.ml.regression import GBTRegressor
# Takes the "features" column and learns to predict "rul"
gbt = GBTRegressor(labelCol="rul",featuresCol="features")

# COMMAND ----------

from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import RegressionEvaluator

# Define a grid of hyperparameters to test:
#  - maxDepth: max depth of each decision tree in the GBT ensemble
#  - maxIter: iterations, i.e., number of trees in each GBT ensemble
# In this example notebook, we keep these values small.  In practice, to get the highest accuracy, you would likely want to try deeper trees (10 or higher) and more trees in the ensemble (>100).
paramGrid = ParamGridBuilder()\
  .addGrid(gbt.maxDepth, [2, 5])\
  .addGrid(gbt.maxIter, [2, 10])\
  .build()
# Define an evaluation metric,'R2'.  This tells CrossValidator how well we are doing by comparing the true labels with predictions.
evaluator = RegressionEvaluator(metricName="mae", labelCol=gbt.getLabelCol(), predictionCol=gbt.getPredictionCol())
# Declare the CrossValidator, which runs model tuning for us.
cv = CrossValidator(estimator=gbt, evaluator=evaluator, estimatorParamMaps=paramGrid)

# COMMAND ----------

from pyspark.ml import Pipeline
pipeline = Pipeline(stages=[vectorAssembler, vectorIndexer, cv])

# COMMAND ----------


#fit data to pipeline and train model
pipelineModel = pipeline.fit(train)

# COMMAND ----------

#Calc Pred Values 
predictions = pipelineModel.transform(test)

# COMMAND ----------

display(predictions.select("rul", "prediction", *featuresCols))

# COMMAND ----------

# Display R2
mae = evaluator.evaluate(predictions)
print("Test Error = %g" % mae)