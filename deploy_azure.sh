#!/bin/bash

# Exit on error
set -e

# Configuration
RESOURCE_GROUP="rg-bangkok-aqi"
LOCATION="southeastasia"
STORAGE_ACCOUNT="stbangkokaqi$RANDOM" # Random suffix for uniqueness
CONTAINER_NAME="aqi-data"
ACR_NAME="acrbangkokaqi$RANDOM"
CONTAINER_APP_ENV="cae-bangkok-aqi"
CONTAINER_APP_NAME="ca-bangkok-aqi"

echo "--- Starting Azure Deployment ---"

# 1. Create Resource Group
echo "Creating Resource Group: $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Storage Account
echo "Creating Storage Account: $STORAGE_ACCOUNT..."
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Get Connection String
CONN_STR=$(az storage account show-connection-string --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --output tsv)

# Create Container
echo "Creating Blob Container: $CONTAINER_NAME..."
az storage container create --name $CONTAINER_NAME --connection-string "$CONN_STR"

# 3. Create Azure Container Registry
echo "Creating ACR: $ACR_NAME..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Login to ACR
az acr login --name $ACR_NAME

# 4. Build and Push Image
IMAGE_TAG="$ACR_NAME.azurecr.io/bangkok-aqi:latest"
echo "Building and Pushing Image: $IMAGE_TAG..."
az acr build --registry $ACR_NAME --image bangkok-aqi:latest .

# 5. Create Container App Environment
echo "Creating Container App Environment..."
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# 6. Create Container App (Job would be better for batch, but App is easier to demo)
# We'll set it to run the extract script by default
echo "Creating Container App..."
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $IMAGE_TAG \
  --target-port 80 \
  --ingress external \
  --query properties.configuration.ingress.fqdn \
  --secrets storage-conn-str="$CONN_STR" \
  --env-vars AZURE_STORAGE_CONNECTION_STRING=secretref:storage-conn-str AZURE_STORAGE_CONTAINER_NAME=$CONTAINER_NAME

echo "--- Deployment Complete ---"
echo "Resource Group: $RESOURCE_GROUP"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Container App: $CONTAINER_APP_NAME"
echo "Connection String (save this!): $CONN_STR"
