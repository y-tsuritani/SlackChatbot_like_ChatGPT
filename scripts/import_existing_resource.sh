#!/bin/bash

# Environment suffix
suffix = "dev"

# GCS bucket name
gcs_buckets = ("app-terraform-backend-state-${suffix}", "app-deploy-cloud-functions")

# import service account
terraform import google_service_account.func_service_account sa-name@davincibot-377306.iam.gserviceaccount.com

# Import tfstate GCS Bucket
terraform import google_storage_bucket.terraform_state app-terraform-backend

terraform import google_storage_bucket.src_cloud_functions davinci-bot_functions_src_eng

# Import GCS Bucket for loop
for bucket in "${gcs_buckets[@]}"
do
  terraform import google_storage_bucket.${bucket} ${bucket}
done
