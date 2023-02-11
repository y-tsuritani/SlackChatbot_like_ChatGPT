variable "project_id" {
  description = "GCP project id"
  default     = "gcp-engineering-358313"
}

variable "region" {
  description = "region"
  default     = "asia-northeast1"
}

variable "function_name" {
  description = "my function name"
  default     = "davinci-bot"
}

variable "env" {
  description = "select environment"
  default     = "dev"
}
