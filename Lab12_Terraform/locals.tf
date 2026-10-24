locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "IPA-Student"
    },
    var.extra_tags
  )

  is_production = var.environment == "prod"
}
