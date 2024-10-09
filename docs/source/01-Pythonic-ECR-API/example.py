# -*- coding: utf-8 -*-

import boto3
import simple_aws_ecr.api as simple_aws_ecr

ecr_client = boto3.client("ecr")

# get or create repository
repo = simple_aws_ecr.Repository.get(
    ecr_client=ecr_client,
    repository_name="my-repo",
)
if repo is None:  # not exists
    ecr_client.create_repository(repositoryName="my-repo")

# list repositories
repo_list = simple_aws_ecr.Repository.list(ecr_client=ecr_client)

# get image
image = simple_aws_ecr.Image.get_by_tag(
    ecr_client=ecr_client,
    repository_name="my-repo",
    image_tag="latest",
)

image = simple_aws_ecr.Image.get_by_digest(
    ecr_client=ecr_client,
    repository_name="my-repo",
    image_digest="sha256:123456",
)

# list images
image_list = simple_aws_ecr.Image.list(ecr_client=ecr_client, repository_name="my-repo")
