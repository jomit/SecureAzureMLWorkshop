import requests
import time
from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.pipeline.core import PipelineRun
from azureml.pipeline.core import PublishedPipeline
from azureml.core.authentication import AzureCliAuthentication

cli_auth = AzureCliAuthentication()

##------------- Get Workspace

subscriptionId = "<your subscription id>"  # make this a parameter
resourceGroup = "<your resource group>" # make this a parameter
workspaceName = "<your ml workspace name>" # make this a parameter

ws = Workspace(subscriptionId, resourceGroup, workspaceName, auth=cli_auth)

##------------- Run Published pipeline using REST endpoint

aad_token = cli_auth.get_authentication_header()
published_pipeline_id = "ab0691a9-438f-416b-a146-5c7660d1be11" # Replace this with the published pipeline id
published_pipeline = PublishedPipeline.get(ws, published_pipeline_id)
rest_endpoint = published_pipeline.endpoint
print("Rest endpoint: " + rest_endpoint)

response = requests.post(rest_endpoint,
                         headers=aad_token,
                         json={"ExperimentName": "quality_prediction_gb",
                               "RunSource": "SDK", 
                               "ParameterAssignments": {
                                   "modelName": "quality_gbm_model.pkl", 
                                   "datasetName": "qualitydataset",
                                   "datasetStorePath": "/inputdata/train.csv"}}) 
print(response)

run_id = response.json()["Id"]
print("Run id: " + run_id)

pipeline_run = PipelineRun.get(ws, run_id)

while True:
    print ("Checking the job status...")
    status = pipeline_run.get_status()
    if (status == 0 or status == "NotStarted"):
        print("Job " + run_id + " not yet started...")
    elif (status == 1 or status == "Running"):
        print("Job " + run_id + " running...")
    elif (status == 2 or status == "Failed"):
        print("Job " + run_id + " failed!")
        break
    elif (status == 3 or status == "Cancelled"):
        print("Job " + run_id + " cancelled!")
        break
    elif (status == 4 or status == "Finished"):
        print("Job " + run_id + " finished!")
        break
    time.sleep(1)  # wait one second