variable "project_id" {
  description = "GCP project id"
  default     = "gcp-engineering-358313"
}

variable "region" {
  description = "region"
  default     = "us-central1"
}

variable "function_name" {
  description = "my function name(_)"
  default     = "slackbot_chatgpt"
}

variable "function-name" {
  description = "my function name(-)"
  default     = "slackbot-chatgpt"
}

variable "env_code" {
  description = "select environment"
  default = "dev"
}