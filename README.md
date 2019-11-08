# Create Secure Batch ML Pipelines

![Architecture](https://github.com/jomit/secure-ml-platform/blob/master/images/architecture.png)

### Prerequisites

- Install [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)

### Create Virtual Network

- `az group create -l westus -n ASecureMLPlatform`

- `az network vnet create -n mlvnet -g ASecureMLPlatform -l westus --address-prefix 10.1.0.0/16 --subnet-name mldefault --subnet-prefix 10.1.0.0/24`

### Create Storage Account

- `az storage account create -n jomitsecuremldata -g ASecureMLPlatform -l westus --sku Standard_LRS --https-only true`

- `az network vnet subnet update -g ASecureMLPlatform --vnet-name mlvnet --name mldefault --service-endpoints "Microsoft.Storage"`

- `$subnetid=(az network vnet subnet show -g ASecureMLPlatform --vnet-name mlvnet --name mldefault --query id --output tsv)`

- `az storage account network-rule add -g ASecureMLPlatform --account-name jomitsecuremldata --subnet $subnetid`

### Create ML Workspace

- `az extension add -n azure-cli-ml`

- `$storageid=(az storage account show -n jomitsecuremldata --query id --output tsv)`

- `az ml workspace create -w securemlws -g ASecureMLPlatform -l westus --storage-account $storageid`

- `az ml datastore list -w securemlws -g ASecureMLPlatform`

- `az ml datastore set-default -n workspaceblobstore -w securemlws -g ASecureMLPlatform`

- `az storage account update -g ASecureMLPlatform -n jomitsecuremldata --default-action Deny`

- (Optional) Add Client IP in storage account firewall for access issues outside the network.

- (Optional) Entire ML Workspace behind VNET in on roadmap.

### Create Data Science Virtual Machine

- `az group deployment create -g ASecureMLPlatform --template-file dsvm-template.json --parameters dsvm-parameters.json --parameters adminPassword=<Your Password>`

- (Optional) To enable MSI Authentication for notebooks, create Identity for VM and provide Contributor access to AML Workspace

- (Optional) Also try Notebook VM in VNET once GA

### Attach AML Remote Compute

- `az network public-ip update -g ASecureMLPlatform -n jomitsecuremlvm-ip --dns-name jomitsecuremlvm --allocation-method Dynamic`

- `az ml computetarget attach remote -a jomitsecuremlvm.westus.cloudapp.azure.com -n default -u jomit -p <Your Password> -g ASecureMLPlatform -w securemlws --ssh-port 22`

### Upload Input Datasets

- (Optional) You can also create a seperate storage account dedicated for input datasets but for now we will use the storage account associated with the workspace)

- `az ml datastore upload -n workspaceblobstore -w securemlws -g ASecureMLPlatform -p ./data -u /inputdata`

### Create AML Pipeline

- `az ml run submit-script -e buildpipeline -w securemlws -g ASecureMLPlatform -d ./aml_pipeline/dependencies.yaml ./aml_pipeline/build_pipeline.py --target default`

- `az ml dataset list -w securemlws -g ASecureMLPlatform`

### Run Published Pipeline

- `az ml run submit-script -e buildpipeline -w securemlws -g ASecureMLPlatform -d ./aml_pipeline/dependencies.yaml ./tests/run_pipeline.py --target default`


# Additional Resources

- [AML Pipeline Getting Started](https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-getting-started.ipynb)

- [Secure Azure ML experimentation and inference jobs within an Azure Virtual Network](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-enable-virtual-network)

- [MLOps using Azure ML Services and Azure DevOps](https://github.com/microsoft/MLOpsPython)
