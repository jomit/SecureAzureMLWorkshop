import os
from azureml.core import Workspace
from azureml.core import Model, Run
from azureml.core.dataset import Dataset
import pandas as pd
import numpy as np
import pickle
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, recall_score, precision_score
import argparse

##------------- Get Workspace
run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace


##------------- Get Arguments

parser = argparse.ArgumentParser("train")
parser.add_argument("--datasetName",type=str)
parser.add_argument("--modelName",type=str)
args = parser.parse_args()

##------------- Print score helper method

def printScores(y_pred, y_true):
    print()
    cm = confusion_matrix(y_true, y_pred)
    print(cm)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    print( 'precision = ', precision, ', recall = ', recall)

##------------- Model Training

allData = ws.datasets[args.datasetName].to_pandas_dataframe()
print(allData.shape)

allfeatures = ['Quality','S1','S2','S3','S5','S6','S7','S8','S9','S10','S11','S12','S13','S14','S15','S16','S17','S18','S19','S20','S21','S22','S23','S24','S25','S26','S27','S28','S29','S30','S31','S32','S33','S34','S35','S36','S37','S38','S39','S40','S41']

trainData = allData[allfeatures]
trainData = trainData.dropna()
print(trainData.shape)

X = trainData[allfeatures[1:len(allfeatures)]].astype(float).values # exclude first feature
y = trainData[allfeatures[0]].astype(float).values  # use first feature

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

from sklearn.ensemble import GradientBoostingClassifier
model_GBM = GradientBoostingClassifier(random_state=42, verbose=1)
model_GBM.fit(X_train, y_train)
printScores(model_GBM.predict(X_train), y_train)
printScores(model_GBM.predict(X_test), y_test)


##------------- Serialize the Model

with open(args.modelName,'wb') as f:
    pickle.dump(model_GBM, f)

##------------- Upload the Model file explicitly into artifacts

run.upload_file(name="./outputs/" + args.modelName, path_or_stream=args.modelName)
print("Uploaded the model {} to experiment {}".format(args.modelName, run.experiment.name))

##------------- Register the Model

model = Model.register(model_path = args.modelName,
                       model_name = args.modelName,
                       tags = {'area': "QualityPrediction", 'type': "GBM"},
                       description = "Quality prediction model",
                       workspace = ws)