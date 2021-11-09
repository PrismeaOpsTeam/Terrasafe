resource "aws_s3_bucket" "other_bucket" {
  bucket = "tf-test-bucket"
  acl    = "private"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

//resource "aws_type" "abc" {
//  attribute = "test"
//}

# resource "aws_type2" "def" {
#   attribute = "test"
# }