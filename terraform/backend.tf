terraform {
  backend "local" {}


// バックエンドをGCSで管理する場合のの記述 //

#   backend "gcs" {
#     bucket = "app-terraform-backend-state"
#   }
# }

# resource "google_storage_bucket" "terraform_state" {
#   name     = "app-terraform-backend-state"
#   location = var.region
#   versioning {
#     enabled = true
#   }

#   lifecycle_rule {
#     action {
#       type = "Delete"
#     }
#     condition {
#       num_newer_versions = 20
#     }
#   }
}
