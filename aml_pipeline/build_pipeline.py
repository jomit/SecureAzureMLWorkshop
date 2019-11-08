import azureml.core
from azureml.core import Workspace, Experiment
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.compute import ComputeTarget, DatabricksCompute
from azureml.exceptions import ComputeTargetException
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.core.dataset import Dataset
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.runconfig import RunConfiguration, CondaDependencies
import os

from azureml.core.authentication import AzureCliAuthentication
cli_auth = AzureCliAuthentication()
##from azureml.core.authentication import MsiAuthentication
##msi_auth = MsiAuthentication()

##------------- Get Workspace

subscriptionId = "<your subscription id>"  # make this a parameter
resourceGroup = "<your resource group>" # make this a parameter
workspaceName = "<your ml workspace name>" # make this a parameter

ws = Workspace(subscriptionId, resourceGroup, workspaceName, auth=cli_auth)
print("Workspace => ",ws.name)


##------------- Pipeline Configuration

sourceDirectory = "./code"
remoteComputeTargetName = "default" # make this a parameter
computeTarget = ws.compute_targets[remoteComputeTargetName]

run_config = RunConfiguration(conda_dependencies=CondaDependencies.create(
        conda_packages=['numpy', 'pandas',
                        'scikit-learn', 'tensorflow', 'keras'],
        pip_packages=['azure', 'azureml-core',
                      'azure-storage',
                      'azure-storage-blob',
                      'azureml-dataprep']))
run_config.environment.docker.enabled = True

##------------- Pipeline Parameters

datasetName = PipelineParameter(name="datasetName", default_value="qualitydataset")
datasetStorePath = PipelineParameter(name="datasetStorePath", default_value="/inputdata/train.csv")
modelName = PipelineParameter(name="modelName", default_value="quality_gbm_model.pkl")

##------------- Data preprocessing step
preprocessingStep = PythonScriptStep(name="preprocess_step",
                        script_name="preprocess.py",
                        source_directory=sourceDirectory,
                        compute_target=computeTarget,
                        arguments=[
                            "--datasetName", datasetName,
                            "--datasetStorePath", datasetStorePath,
                        ],
                        runconfig=run_config,
                        allow_reuse=False)
print("Data preprocessing Step created")


##------------- Model Training step
trainingStep = PythonScriptStep(name="training_step",
                        script_name="train.py",
                        source_directory=sourceDirectory, 
                        compute_target=computeTarget,
                        arguments=[
                            "--datasetName", datasetName,
                            "--modelName", modelName
                        ],
                        runconfig=run_config,
                        allow_reuse=False)
print("Model Training Step created")


##------------- Scoring and Output step
scoringStep = PythonScriptStep(name="scoring_step",
                        script_name="score.py",
                        source_directory=sourceDirectory,
                        compute_target=computeTarget,
                        arguments=[
                            "--modelName", modelName
                        ],
                        runconfig=run_config, 
                        allow_reuse=False)
print("Scoring and output Step created")


##------------- Create Pipeline

trainingStep.run_after(preprocessingStep)
scoringStep.run_after(trainingStep)

qualityMLPipeline = Pipeline(workspace=ws, steps=[scoringStep])
print ("Quality Prediction pipeline is built")

qualityMLPipeline.validate()
print("Quality Prediction pipeline simple validation complete")

##------------- Submit an Experiement using the Pipeline

pipelineRun = Experiment(ws, 'quality_prediction_gb').submit(qualityMLPipeline)
print("Quality Prediction pipeline submitted for execution")

##------------- Publish Pipeline

#publishedPipeline = qualityMLPipeline.publish(name="NewQualityPrediction-Pipeline", description="Quality Prediction pipeline",version="0.1")
publishedPipeline = pipelineRun.publish_pipeline(name="NewQualityPrediction-Pipeline", description="Quality Prediction pipeline",version="0.1")
print("Newly published pipeline id => ",publishedPipeline.id)
print("Newly published pipeline endpoint => ", publishedPipeline.endpoint)

