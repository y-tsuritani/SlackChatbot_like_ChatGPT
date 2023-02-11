terraform {

// 1. バックエンドをローカルで管理する場合の記述
#   backend "local" {}

// 2. バックエンドをGCSで管理する場合の記述 //

  backend "gcs" {
    bucket = "app-terraform-backend"
    prefix  = "slackbot_chatgpt/state"
  }
}
resource "google_storage_bucket" "terraform_state" {
  name     = "app-terraform-backend"
  location = var.region
  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 20
    }
  }
}
