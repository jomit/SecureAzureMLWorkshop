import azureml.core
from azureml.core import Workspace, Experiment
from azureml.core import Run
from azureml.core.dataset import Dataset
import argparse
import os

##------------- Get Workspace
run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace


##------------- Get Arguments

parser = argparse.ArgumentParser("preprocess")
parser.add_argument("--datasetName",type=str)
parser.add_argument("--datasetStorePath",type=str)
args = parser.parse_args()


##------------- Get Default datastore
defaultStore = ws.get_default_datastore() #defaultStore = Datastore(ws, "workspaceblobstore")
print("Datastore => ", defaultStore.name)

##------------- Register the Dataset
datapath = defaultStore.path(args.datasetStorePath)
dataset = Dataset.from_delimited_files(datapath)
dataset = dataset.register(workspace = ws,
                           name = args.datasetName,
                           description = 'Training data for quality prediction',
                           exist_ok = True)
print("Registered dataset  => ", args.datasetName)