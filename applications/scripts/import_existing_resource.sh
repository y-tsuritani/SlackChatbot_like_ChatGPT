#!/bin/bash

# Environment suffix
suffix = "dev"

# GCS bucket name
gcs_buckets = ("fm-backet-${suffix}", "gim-terraform-backend-state-${suffix}", "gim-deploy-cloud-functions")

# import service account
terraform import google_service_account.workflows_service_account workflows-sa@facility-master.iam.gserviceaccount.com

# Import GCS Bucket
for bucket in "${gcs_buckets[@]}"
do
  terraform import google_storage_bucket.${bucket} ${bucket}
done
