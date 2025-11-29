terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_vpc" "vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.environment}-vpc"
  }
}

resource "aws_subnet" "vpc-public" {
  count             = length(var.azs)
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.azs[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-subnet-${count.index + 1}"
  }
}

resource "aws_internet_gateway" "k8s-api-igw" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.environment}-igw"
  }
}

resource "aws_route_table" "vpc-public-rt" {
    vpc_id = aws_vpc.vpc.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.k8s-api-igw.id
    }

    tags = {
        Name = "${var.environment}-public-rt"
    }
}

resource "aws_route_table_association" "vpc-public-rt-a" {
  count          = length(aws_subnet.vpc-public)
  subnet_id      = aws_subnet.vpc-public[count.index].id
  route_table_id = aws_route_table.vpc-public-rt.id
}
