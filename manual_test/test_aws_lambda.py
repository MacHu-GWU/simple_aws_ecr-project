# -*- coding: utf-8 -*-

"""
ECR Cross-Account Replication and Lambda Deployment Test Script

This script demonstrates and tests the capabilities of the aws_ecr Python library
for managing Amazon Elastic Container Registry (ECR) across multiple AWS accounts.
It showcases ECR repository creation, cross-account replication, image building and
pushing, cross-account permissions, and Lambda function deployment using ECR images.

Test Scenario
------------------------------------------------------------------------------
1. Two AWS accounts are used:
   - Devops account (source)
   - Sandbox (SBX) account (destination)

2. Process Flow:
   a. Create an ECR repository in the Devops account
   b. Set up replication from Devops to SBX account
   c. Build and push a Docker image to the Devops ECR repository
   d. Configure cross-account permissions for Lambda access
   e. Deploy two Lambda functions:
      - One in SBX using the image from Devops ECR
      - One in SBX using the replicated image in SBX ECR
   f. Test both Lambda functions to verify proper setup and permissions
   g. Clean up all created resources

Key Components
------------------------------------------------------------------------------
1. ECR Repository Management
2. Cross-Account ECR Replication
3. Docker Image Building and Pushing
4. Cross-Account Lambda Deployment from ECR
5. AWS Lambda Function Creation and Invocation
6. Resource Cleanup

Usage
------------------------------------------------------------------------------
1. Update the configuration section at the top of the script:
   - Set appropriate AWS profile names
   - Configure repository and Lambda function names
2. Ensure the required AWS permissions are set for both accounts
3. Uncomment the desired function calls in the __main__ section
4. Run the script to execute the selected operations

Dependencies
------------------------------------------------------------------------------
- boto3
- boto_session_manager
- rich
- simple_aws_ecr (this library)

Note
------------------------------------------------------------------------------
This script is intended for testing and demonstration purposes. Ensure you
understand the AWS costs associated with creating and managing these resources.
Always clean up resources after testing to avoid unnecessary charges.

Author: Sanhe Hu
Date: 2024-10-01
Version: 1.0
"""


import json
from pathlib import Path

from boto_session_manager import BotoSesManager
from rich import print as rprint

import simple_aws_ecr.api as aws_ecr


# ------------------------------------------------------------------------------
# Update configuration here
# ------------------------------------------------------------------------------
aws_profile_devops = "bmt_app_devops_us_east_1"
aws_profile_sbx = "bmt_app_dev_us_east_1"
repo_name = "aws_ecr_test_lbd_image"
lbd_func_name_1 = "aws_ecr_test_lbd_1"
lbd_func_name_2 = "aws_ecr_test_lbd_2"


# ------------------------------------------------------------------------------
# Don't change anything below
# ------------------------------------------------------------------------------
bsm_devops = BotoSesManager(profile_name=aws_profile_devops)
bsm_sbx = BotoSesManager(profile_name=aws_profile_sbx)
dir_here = Path(__file__).absolute().parent
path_dockerfile = dir_here.joinpath("Dockerfile")
lbd_func_role = f"arn:aws:iam::{bsm_sbx.aws_account_id}:role/lambda-power-user-role"  # manually prepare this role


def create_repo():
    if (
        aws_ecr.Repository.get(
            ecr_client=bsm_devops.ecr_client, repository_name=repo_name
        )
        is None
    ):
        bsm_devops.ecr_client.create_repository(repositoryName=repo_name)


def setup_replication():
    aws_ecr.configure_replication_for_source_registry(
        ecr_client=bsm_devops.ecr_client,
        rules=[
            aws_ecr.ReplicationRule(
                destinations=[
                    aws_ecr.Destination(
                        region=bsm_sbx.aws_region,
                        registryId=bsm_sbx.aws_account_id,
                    ),
                ],
                repositoryFilters=[
                    aws_ecr.RepositoryFilter(
                        filter=repo_name,
                    ),
                ],
            )
        ],
    )

    aws_ecr.configure_replication_for_destination_registry(
        ecr_client=bsm_sbx.ecr_client,
        source_account_id_list=[bsm_devops.aws_account_id],
        target_account_id=bsm_sbx.aws_account_id,
        target_region=bsm_sbx.aws_region,
    )


def build_and_push_image():
    ecr_context = aws_ecr.EcrContext(
        aws_account_id=bsm_devops.aws_account_id,
        aws_region=bsm_devops.aws_region,
        repo_name=repo_name,
        path_dockerfile=path_dockerfile,
    )
    ecr_context.build_image(
        image_tag_list=["latest", "0.1.1"], additional_args=["--platform=linux/amd64"]
    )

    aws_ecr.ecr_login(
        ecr_client=bsm_devops.ecr_client,
        aws_account_id=bsm_devops.aws_account_id,
        aws_region=bsm_devops.aws_region,
    )
    ecr_context.push_image(image_tag_list=["latest", "0.1.1"])


def setup_cross_account_permission():
    aws_ecr.configure_cross_account_lambda_get(
        ecr_client=bsm_devops.ecr_client,
        repo_name=repo_name,
        aws_account_id_list=[bsm_sbx.aws_account_id],
        lbd_func_name_prefix="",
    )


def deploy_lambda_from_devops():
    bsm_sbx.lambda_client.create_function(
        FunctionName=lbd_func_name_1,
        Role=lbd_func_role,
        Code=dict(
            ImageUri=aws_ecr.get_ecr_image_uri(
                aws_account_id=bsm_devops.aws_account_id,
                aws_region=bsm_devops.aws_region,
                ecr_repo_name=repo_name,
                tag="latest",
            )
        ),
        PackageType="Image",
    )


def test_lbd_func_1():
    response = bsm_sbx.lambda_client.invoke(
        FunctionName=lbd_func_name_1,
        InvocationType="RequestResponse",
    )
    res = json.loads(response["Payload"].read().decode("utf-8"))
    rprint(res)


def deploy_lambda_from_sbx():
    bsm_sbx.lambda_client.create_function(
        FunctionName=lbd_func_name_2,
        Role=lbd_func_role,
        Code=dict(
            ImageUri=aws_ecr.get_ecr_image_uri(
                aws_account_id=bsm_sbx.aws_account_id,
                aws_region=bsm_sbx.aws_region,
                ecr_repo_name=repo_name,
                tag="latest",
            )
        ),
        PackageType="Image",
    )


def test_lbd_func_2():
    response = bsm_sbx.lambda_client.invoke(
        FunctionName=lbd_func_name_2,
        InvocationType="RequestResponse",
    )
    res = json.loads(response["Payload"].read().decode("utf-8"))
    rprint(res)


def clean_up():
    try:
        bsm_sbx.lambda_client.delete_function(FunctionName=lbd_func_name_1)
    except:
        pass
    try:
        bsm_sbx.lambda_client.delete_function(FunctionName=lbd_func_name_2)
    except:
        pass
    try:
        bsm_devops.ecr_client.delete_repository(repositoryName=repo_name, force=True)
    except:
        pass
    try:
        bsm_sbx.ecr_client.delete_repository(repositoryName=repo_name, force=True)
    except:
        pass


if __name__ == "__main__":
    """
    This works!

    slim build --target 862612136886.dkr.ecr.us-east-1.amazonaws.com/aws_ecr_test_lbd_image:0.1.1 --tag 862612136886.dkr.ecr.us-east-1.amazonaws.com/aws_ecr_test_lbd_image:0.1.1 --http-probe=false
    """
    # create_repo()
    # setup_replication()
    # build_and_push_image()
    # setup_cross_account_permission()
    # deploy_lambda_from_devops()
    # test_lbd_func_1()
    # deploy_lambda_from_sbx()
    # test_lbd_func_2()
    # clean_up()
