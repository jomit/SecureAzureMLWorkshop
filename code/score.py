import os
import pickle
import json
import numpy
from azureml.core import Workspace
from azureml.core import Model, Run
from sklearn.externals import joblib
import argparse

##------------- Get Workspace
run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace

##------------- Get Arguments

parser = argparse.ArgumentParser("train")
parser.add_argument("--modelName",type=str)
args = parser.parse_args()

##------------- Model Scoring

model_path = Model.get_model_path(model_name = args.modelName)
model = joblib.load(model_path)

rawdata = '{ "data" : [4.996352,41.68612,41.79799,4.998839,5.051471,27.01976,28.5,36,39.6,22.7,921.2494,2081.41,2170.84,1017.489,24.68081,29.16544,29.65642,29.15765,21.35513,140.4473,133.4049,4.998026,63.68074,25.13597,32.08001,5.075305,27.029,7.516817,54.95351,4.998026,60,40,13,4.933381,11,5.000257,5.001157,28283.33,26892.26,18333.06641]}'

data = json.loads(rawdata)['data']
data = [numpy.array(data)]
result = model.predict(data)

print("Result =>",result.tolist())