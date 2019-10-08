# -*- coding: utf-8 -*-

from sklearn.ensemble import GradientBoostingRegressor
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.datasets import load_boston
from sklearn.metrics import mean_absolute_error
from random import randrange,randint


max_depth = randint(2,10)
n_estimators = int(randrange(2000,5000,100))


train = pd.read_csv("data/turbofan.csv")

features  = train.drop('rul',axis=1)


X = train.drop('rul',axis=1)
y = pd.Series(train.rul)

X_train, X_test, y_train, y_test = train_test_split(X, y)


regression_model = GradientBoostingRegressor(
    max_depth=max_depth,
    n_estimators=n_estimators,
    learning_rate=.5
)
regression_model.fit(X_train, y_train)

y_pred = regression_model.predict(X_test)

print(mean_absolute_error(y_test, y_pred))