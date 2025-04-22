variable "aws_region" {
  description = "AWS region to deploy into"
  type    	= string
  default 	= "us-east-1"
}
variable "earthdata_username" {
  description = "earthdata username"
  type    	= string
  default 	= ""
}
variable "earthdata_password" {
  description = "earthdata password"
  type    	= string
  default 	= ""
}
variable "s3_bucket" {
  description = "bucket name"
  type = string
}