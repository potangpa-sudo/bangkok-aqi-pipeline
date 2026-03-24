#!/usr/bin/env bash

set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-rg-bangkok-aqi}"
LOCATION="${LOCATION:-southeastasia}"
CONTAINER_NAME="${CONTAINER_NAME:-aqi-data}"
JOB_CRON_SCHEDULE="${JOB_CRON_SCHEDULE:-0 * * * *}"
JOB_TRIGGER_TYPE="${JOB_TRIGGER_TYPE:-Schedule}"
STORAGE_ACCOUNT="${STORAGE_ACCOUNT:-stbangkokaqi$RANDOM}"
ACR_NAME="${ACR_NAME:-acrbangkokaqi$RANDOM}"
CONTAINER_APP_ENV="${CONTAINER_APP_ENV:-cae-bangkok-aqi}"
CONTAINER_APP_JOB_NAME="${CONTAINER_APP_JOB_NAME:-caj-bangkok-aqi}"
IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-bangkok-aqi}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
AQI_LATITUDE="${AQI_LATITUDE:-13.75}"
AQI_LONGITUDE="${AQI_LONGITUDE:-100.5}"
AQI_TIMEZONE="${AQI_TIMEZONE:-Asia/Bangkok}"
AZURE_STORAGE_CONTAINER_NAME="${AZURE_STORAGE_CONTAINER_NAME:-$CONTAINER_NAME}"
ALERT_WEBHOOK_URL="${ALERT_WEBHOOK_URL:-}"

echo "--- Starting Azure Batch Deployment ---"
echo "Resource group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "Job trigger type: $JOB_TRIGGER_TYPE"

if ! command -v az >/dev/null 2>&1; then
    echo "Azure CLI is required but was not found." >&2
    exit 1
fi

if [[ "$JOB_TRIGGER_TYPE" != "Schedule" && "$JOB_TRIGGER_TYPE" != "Manual" ]]; then
    echo "JOB_TRIGGER_TYPE must be either Schedule or Manual." >&2
    exit 1
fi

echo "Ensuring Azure Container Apps extension is installed..."
az extension add --name containerapp --upgrade --allow-preview true >/dev/null

echo "Creating resource group: $RESOURCE_GROUP..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" >/dev/null

echo "Creating storage account: $STORAGE_ACCOUNT..."
az storage account create \
    --name "$STORAGE_ACCOUNT" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    >/dev/null

CONN_STR="$(
    az storage account show-connection-string \
        --name "$STORAGE_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --output tsv
)"

echo "Creating blob container: $CONTAINER_NAME..."
az storage container create \
    --name "$CONTAINER_NAME" \
    --connection-string "$CONN_STR" \
    >/dev/null

echo "Creating Azure Container Registry: $ACR_NAME..."
az acr create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ACR_NAME" \
    --sku Basic \
    --admin-enabled true \
    >/dev/null

echo "Building batch image in ACR..."
az acr build \
    --registry "$ACR_NAME" \
    --image "$IMAGE_REPOSITORY:$IMAGE_TAG" \
    .

IMAGE_NAME="$ACR_NAME.azurecr.io/$IMAGE_REPOSITORY:$IMAGE_TAG"
ACR_USERNAME="$(az acr credential show --name "$ACR_NAME" --query username --output tsv)"
ACR_PASSWORD="$(
    az acr credential show \
        --name "$ACR_NAME" \
        --query 'passwords[0].value' \
        --output tsv
)"

echo "Creating Container Apps managed environment..."
if az containerapp env show --name "$CONTAINER_APP_ENV" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    echo "Reusing existing Container Apps environment: $CONTAINER_APP_ENV"
else
    az containerapp env create \
        --name "$CONTAINER_APP_ENV" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        >/dev/null
fi

SECRET_ARGS=(
    "storage-conn-str=$CONN_STR"
    "acr-password=$ACR_PASSWORD"
)
if [[ -n "$ALERT_WEBHOOK_URL" ]]; then
    SECRET_ARGS+=("alert-webhook-url=$ALERT_WEBHOOK_URL")
fi

ENV_VARS=(
    "AQI_LATITUDE=$AQI_LATITUDE"
    "AQI_LONGITUDE=$AQI_LONGITUDE"
    "AQI_TIMEZONE=$AQI_TIMEZONE"
    "AZURE_STORAGE_CONTAINER_NAME=$AZURE_STORAGE_CONTAINER_NAME"
    "AZURE_STORAGE_CONNECTION_STRING=secretref:storage-conn-str"
)
if [[ -n "$ALERT_WEBHOOK_URL" ]]; then
    ENV_VARS+=("ALERT_WEBHOOK_URL=secretref:alert-webhook-url")
fi

echo "Creating Container Apps job: $CONTAINER_APP_JOB_NAME..."
JOB_ARGS=(
    --name "$CONTAINER_APP_JOB_NAME"
    --resource-group "$RESOURCE_GROUP"
    --environment "$CONTAINER_APP_ENV"
    --image "$IMAGE_NAME"
    --registry-server "$ACR_NAME.azurecr.io"
    --registry-username "$ACR_USERNAME"
    --registry-password "secretref:acr-password"
    --cpu "0.5"
    --memory "1.0Gi"
    --replica-timeout "1800"
    --replica-retry-limit "1"
    --parallelism "1"
    --secrets "${SECRET_ARGS[@]}"
    --env-vars "${ENV_VARS[@]}"
    --trigger-type "$JOB_TRIGGER_TYPE"
)

if [[ "$JOB_TRIGGER_TYPE" == "Schedule" ]]; then
    JOB_ARGS+=(--cron-expression "$JOB_CRON_SCHEDULE")
fi

if az containerapp job show --name "$CONTAINER_APP_JOB_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    echo "Updating existing Container Apps job: $CONTAINER_APP_JOB_NAME..."
    az containerapp job update "${JOB_ARGS[@]}" >/dev/null
else
    az containerapp job create "${JOB_ARGS[@]}" >/dev/null
fi

echo "--- Deployment Complete ---"
echo "Resource Group: $RESOURCE_GROUP"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Blob Container: $CONTAINER_NAME"
echo "ACR: $ACR_NAME"
echo "Container Apps Environment: $CONTAINER_APP_ENV"
echo "Container Apps Job: $CONTAINER_APP_JOB_NAME"
echo "Image: $IMAGE_NAME"
if [[ "$JOB_TRIGGER_TYPE" == "Schedule" ]]; then
    echo "Schedule: $JOB_CRON_SCHEDULE"
else
    echo "Job trigger: manual"
    echo "Run manually with:"
    echo "az containerapp job start --name $CONTAINER_APP_JOB_NAME --resource-group $RESOURCE_GROUP"
fi
