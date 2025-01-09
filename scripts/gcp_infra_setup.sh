#! /usr/bin/env bash
# 2025-01-08
# Setup Cloud Run instance and a Cloud SQL instance on a public IP.

# Lets see how vanilla we can make this.

set -eou pipefail


PROJECT_ID=" "
REGION="us-west1"
DEPLOYMENT_NAME="atoywebapi"
SERVICE_ACCOUNT_NAME="${DEPLOYMENT_NAME}-sa"
DB_INSTANCE_NAME="${DEPLOYMENT_NAME}-20250107"
# Name of the database within the postgres instance.
DB_DB_NAME="${DEPLOYMENT_NAME}"
DB_USER_NAME="service"
DB_PASSWORD=$(openssl rand -base64 12)

# Create service account for cloud run service
gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}" \
  --display-name="Service Account for Cloud Run ${DEPLOYMENT_NAME}" \
  --project="${PROJECT_ID}"

  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Create vanilla cloud sql postgres instance with database and user.
gcloud sql instances create "${DB_INSTANCE_NAME}" \
    --region="${REGION}" \
    --database-version="POSTGRES_17" \
    --tier="db-g1-small" \
    --edition="enterprise" \
    --project="${PROJECT_ID}"

gcloud sql databases create "${DB_DB_NAME}" \
    --instance="${DB_INSTANCE_NAME}" \
    --project="${PROJECT_ID}"

gcloud sql users create "${DB_USER_NAME}" \
    --instance="${DB_INSTANCE_NAME}" \
    --password="${DB_PASSWORD}" \
    --project="${PROJECT_ID}"

echo "REMEMBER TO STORE THE DB PASSWORD: ${DB_PASSWORD}"

# Grab the full email for the SA we created above for cloudrun.
sa_email=$(gcloud iam service-accounts list --project=$PROJECT_ID --format="value(email)" --filter="name:${SERVICE_ACCOUNT_NAME}")

# Get name of connection from the cloud sql database instance created above.
instance_connection_name=$(gcloud sql instances describe "${DB_INSTANCE_NAME}" --project="${PROJECT_ID}" --format="value(connectionName)")

gcloud run deploy "${DEPLOYMENT_NAME}" \
    --source="." \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --service-account="${sa_email}" \
    --add-cloudsql-instances="${instance_connection_name}" \
    --set-env-vars="DATABASE_URL=postgresql+psycopg2://${DB_USER_NAME}:${DB_PASSWORD}@/${DB_DB_NAME}?host=/cloudsql/${PROJECT_ID}:${REGION}:${DB_INSTANCE_NAME}"
# psycopg2 driver apparently require "host" in the path for Cloud SQL connection via Unix sockets. It also doesn't require "/.s.PGSQL.5432" to be tacked on to the end.