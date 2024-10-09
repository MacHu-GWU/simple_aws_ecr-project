# -*- coding: utf-8 -*-

"""
A Toolkit for AWS Elastic Container Registry Operations

This module provides a collection of utility functions and classes for common
operations on AWS Elastic Container Registry (ECR). It serves as a "recipe book"
for ECR-related tasks, offering pre-built solutions for frequent use cases.
"""

import typing as T
import json
import hashlib
import dataclasses
from datetime import timezone

import botocore.exceptions
from boto3 import Session

from .model import Image, ReplicationRule, Destination, RepositoryFilter
from .utils import get_utc_now

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ecr.client import ECRClient


# ------------------------------------------------------------------------------
# Cross Account
# ------------------------------------------------------------------------------
SID_ALLOW_CROSS_ACCOUNT_GET = "AllowCrossAccountGet"
SID_ALLOW_CROSS_ACCOUNT_LBD_GET = "AllowCrossAccountLambdaGet"


@dataclasses.dataclass
class Policy:
    """
    Represents and manages an ECR registry or repository permission policy.

    This class provides methods to create, modify, and convert ECR repository
    permission policies.

    :param document: The full policy document.
    :param statements: A dictionary of policy statements, keyed by their Sid.
    """

    # fmt: off
    document: T.Dict[str, T.Dict[str, T.Any]] = dataclasses.field()
    statements: T.Dict[str, T.Dict[str, T.Any]] = dataclasses.field(default_factory=dict)
    # fmt: on

    @classmethod
    def from_policy_document(
        cls,
        policy_document: T.Dict[str, T.Any],
    ):
        """
        Create a RepositoryPermissionPolicy instance from a policy document.

        :param policy_document: The policy document as a dictionary from the
            ``get_repository_policy`` API.
        """
        return cls(
            document=policy_document,
            statements={
                dct["Sid"]: dct for dct in policy_document.get("Statement", [])
            },
        )

    def to_policy_document(self) -> T.Dict[str, T.Any]:
        """
        Convert the RepositoryPermissionPolicy to a policy document dictionary.
        """
        new_document = json.loads(json.dumps(self.document))
        new_document["Statement"] = list(
            sorted(
                self.statements.values(),
                key=lambda dct: dct["Sid"],
            )
        )
        return new_document


def build_cross_account_get_statement(
    aws_account_id_list: T.List[str],
) -> T.Dict[str, T.Any]:
    """
    Build a policy statement allowing cross-account access to ECR images.

    :param aws_account_id_list: List of AWS account IDs to grant access.
    """
    return {
        "Sid": SID_ALLOW_CROSS_ACCOUNT_GET,
        "Effect": "Allow",
        "Principal": {
            "AWS": [
                f"arn:aws:iam::{aws_account_id}:root"
                for aws_account_id in aws_account_id_list
            ]
        },
        "Action": [
            "ecr:BatchGetImage",
            "ecr:GetDownloadUrlForLayer",
        ],
    }


def build_cross_account_lbd_get_statement(
    aws_account_id_list: T.List[str],
    aws_region: str = "*",
    lbd_func_name_prefix: str = "",
):
    """
    Build a policy statement allowing cross-account Lambda function access to ECR images.

    .. note::

        You also need to add the permission defined in
        :func:`build_cross_account_get_statement`

    :param aws_account_id_list: List of AWS account IDs to grant access.
    :param aws_region: AWS region for Lambda functions. Defaults to "*" (all regions).
    :param lbd_func_name_prefix: Prefix for allowed Lambda function names.
        Defaults to "" (all Lambda functions).
    """
    return {
        "Sid": SID_ALLOW_CROSS_ACCOUNT_LBD_GET,
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": [
            "ecr:BatchGetImage",
            "ecr:GetDownloadUrlForLayer",
        ],
        "Condition": {
            "StringLike": {
                "aws:sourceARN": [
                    f"arn:aws:lambda:{aws_region}:{aws_account_id}:function:{lbd_func_name_prefix}*"
                    for aws_account_id in aws_account_id_list
                ]
            }
        },
    }


def configure_cross_account_lambda_get(
    ecr_client: "ECRClient",
    repo_name: str,
    aws_account_id_list: T.List[str],
    aws_region: str = "*",
    lbd_func_name_prefix: str = "",
) -> bool:
    """
    Configure cross-account access for Lambda functions to an ECR repository.

    This function updates the repository policy to allow specified AWS accounts
    and their Lambda functions to pull images from the repository.

    :param ecr_client: The boto3 ECR client of the ECR repository owner.
    :param repo_name: Name of the ECR repository.
    :param aws_account_id_list: List of AWS account IDs to grant access.
    :param aws_region: AWS region for Lambda functions. Defaults to "*" (all regions).
    :param lbd_func_name_prefix: Prefix for allowed Lambda function names.
        Defaults to "" (all Lambda functions).

    :return: True if the policy was changed, False otherwise.
    """
    # get existing
    try:
        response = ecr_client.get_repository_policy(
            repositoryName=repo_name,
        )
        policy_document = json.loads(response["policyText"])
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "RepositoryPolicyNotFoundException":
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [],
            }
        else:  # pragma: no cover
            raise e

    policy = Policy.from_policy_document(policy_document)
    is_policy_changed = False

    # acc statement
    # NOTE: even though it sounds like we only need the lambda function service
    # as principal, but we still need the root account as principal to allow
    # the lambda function to pull images from the ECR repository
    acc_stmt = policy.statements.get(
        SID_ALLOW_CROSS_ACCOUNT_GET,
        build_cross_account_get_statement(
            aws_account_id_list=[],
        ),
    )
    arn_list: T.List[str] = acc_stmt["Principal"]["AWS"]
    if isinstance(arn_list, str):
        arn_list = [arn_list]
    for aws_account_id in aws_account_id_list:
        arn = f"arn:aws:iam::{aws_account_id}:root"
        if arn not in arn_list:
            arn_list.append(arn)
            is_policy_changed = True
    acc_stmt["Principal"]["AWS"] = arn_list
    if aws_account_id_list:
        policy.statements[SID_ALLOW_CROSS_ACCOUNT_GET] = acc_stmt

    # lbd statement
    lbd_stmt = policy.statements.get(
        SID_ALLOW_CROSS_ACCOUNT_LBD_GET,
        build_cross_account_lbd_get_statement(
            aws_account_id_list=[],
        ),
    )
    arn_list: T.List[str] = lbd_stmt["Condition"]["StringLike"]["aws:sourceARN"]
    if isinstance(arn_list, str):
        arn_list = [arn_list]
    for aws_account_id in aws_account_id_list:
        arn = f"arn:aws:lambda:{aws_region}:{aws_account_id}:function:{lbd_func_name_prefix}*"
        if arn not in arn_list:
            arn_list.append(arn)
            is_policy_changed = True
    lbd_stmt["Condition"]["StringLike"]["aws:sourceARN"] = arn_list
    if aws_account_id_list:
        policy.statements[SID_ALLOW_CROSS_ACCOUNT_LBD_GET] = lbd_stmt

    # make change
    if is_policy_changed:
        ecr_client.set_repository_policy(
            repositoryName=repo_name,
            policyText=json.dumps(policy.to_policy_document(), indent=4),
        )

    return is_policy_changed


# ------------------------------------------------------------------------------
# Replication
# ------------------------------------------------------------------------------
def configure_replication_for_source_registry(
    ecr_client: "ECRClient",
    rules: T.List["ReplicationRule"],
):
    """
    Configure ECR replication rules for a source registry.

    This function retrieves existing replication rules, merges them with the provided
    rules, and updates the registry's replication configuration.

    .. note::

        This function retrieves existing replication rules, merges them with the provided
        rules, and updates the registry's replication configuration. It is an idempotent
        operation that adds new rules and updates existing ones without removing any
        rules not present in the input.

    :param ecr_client: The boto3 ECR client of the source registry.
    :param rules: A list of :class:`aws_ecr.model.ReplicationRule` objects to be applied.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/put_replication_configuration.html
    """
    res = ecr_client.describe_registry()
    existing_rule_list = [
        ReplicationRule.from_dict(dct)
        for dct in res.get("replicationConfiguration", {}).get("rules", [])
    ]
    existing_rule_dict = {rule.fingerprint: rule for rule in existing_rule_list}

    for rule in rules:
        existing_rule_dict[rule.fingerprint] = rule

    ecr_client.put_replication_configuration(
        replicationConfiguration={
            "rules": [rule.to_dict() for rule in existing_rule_dict.values()],
        },
    )


def configure_replication_for_destination_registry(
    ecr_client: "ECRClient",
    source_account_id_list: T.List[str],
    target_account_id: str,
    target_region: str,
):
    """
    Configure the registry policy for an ECR destination registry to allow replication.

    This function creates or updates the registry policy to permit specified source
    accounts to replicate images to the destination registry.

    :param ecr_client: The boto3 ECR client for the destination registry.
    :param source_account_id_list: List of AWS account IDs allowed to replicate to this registry.
    :param target_account_id: The AWS account ID of the destination registry.
    :param target_region: The AWS region of the destination registry.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/get_registry_policy.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/put_registry_policy.html
    """
    # get existing
    try:
        response = ecr_client.get_registry_policy()
        policy_document = json.loads(response["policyText"])
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "RegistryPolicyNotFoundException":
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [],
            }
        else:  # pragma: no cover
            raise e

    policy = Policy.from_policy_document(policy_document)

    source_account_id_list.sort()
    key = "{}-{}-{}".format(
        ",".join(source_account_id_list),
        target_account_id,
        target_region,
    )
    sid = "Replication{}".format(hashlib.md5(key.encode("utf8")).hexdigest())
    statement = {
        "Sid": sid,
        "Effect": "Allow",
        "Principal": {
            "AWS": [
                f"arn:aws:iam::{account_id}:root"
                for account_id in source_account_id_list
            ],
        },
        "Action": [
            "ecr:CreateRepository",
            "ecr:ReplicateImage",
        ],
        "Resource": [f"arn:aws:ecr:{target_region}:{target_account_id}:repository/*"],
    }
    policy.statements[sid] = statement
    ecr_client.put_registry_policy(
        policyText=json.dumps(policy.to_policy_document(), indent=4),
    )


def switch_boto_ses_region(
    boto_ses: "Session",
    aws_region: str,
) -> "Session":
    """
    Switch the boto3 session to another region, using the same credentials.

    :param boto_ses: The boto3 session.
    :param aws_region: The target region.

    :return: The new boto3 session.
    """
    cred = boto_ses.get_credentials()
    kwargs = dict(
        region_name=aws_region,
        aws_access_key_id=cred.access_key,
        aws_secret_access_key=cred.secret_key,
    )
    try:  # pragma: no cover
        if cred.token is not None:
            kwargs["aws_session_token"] = cred.token
    except:  # pragma: no cover
        pass
    return Session(**kwargs)


@dataclasses.dataclass
class DestinationInfo:
    """
    The destination information for the replication rule.

    :param target_boto_ses: The boto3 session for the replication target AWS account.
    :param target_aws_account_id: The target AWS account ID.
    :param target_aws_region: The target AWS region.
    """

    target_boto_ses: "Session" = dataclasses.field()
    target_aws_account_id: str = dataclasses.field()
    target_aws_region: str = dataclasses.field()


def configure_cross_account_replication(
    repo_prefix_filter: str,
    source_aws_account_id: str,
    source_boto_ses: "Session",
    dest_info_list: T.List[DestinationInfo],
):
    """
    Configure both source account and many target account ECR registry policy
    for cross-account replication.

    :param repo_prefix_filter: The repository prefix filter.
    :param source_aws_account_id: The source AWS account ID.
    :param source_boto_ses: The boto3 session for the source AWS account.
    :param dest_info_list: The list of destination information. Each item is a
        :class:`DestinationInfo` object.
    """
    # configure replication rules in the source account ECR registry
    rule = ReplicationRule(
        destinations=[
            Destination(
                region=dest_info.target_aws_region,
                registryId=dest_info.target_aws_account_id,
            )
            for dest_info in dest_info_list
        ],
        repositoryFilters=[
            RepositoryFilter(
                filter=repo_prefix_filter,
            ),
        ],
    )
    # this API is idempotent, so it's safe to call multiple times
    configure_replication_for_source_registry(
        ecr_client=source_boto_ses.client("ecr"),
        rules=[rule],
    )

    # configure target account ECR registry to accept the replication
    for dest_info in dest_info_list:
        new_boto_ses = switch_boto_ses_region(
            boto_ses=dest_info.target_boto_ses,
            aws_region=dest_info.target_aws_region,
        )
        # this API is idempotent, so it's safe to call multiple times
        configure_replication_for_destination_registry(
            ecr_client=new_boto_ses.client("ecr"),
            source_account_id_list=[source_aws_account_id],
            target_account_id=dest_info.target_aws_account_id,
            target_region=dest_info.target_aws_region,
        )


def delete_untagged_image(
    ecr_client: "ECRClient",
    repo_name: str,
    expire: int = 90 * 24 * 60 * 60,
) -> T.List[Image]:  # pragma: no cover
    """
    Delete untagged images from an ECR repository.

    This function lists all untagged images in the repository and deletes them.

    :param ecr_client: The boto3 ECR client.
    :param repo_name: Name of the ECR repository.
    :param expire: The number of seconds after which untagged images are deleted.
    """
    to_delete_image_list = list()
    utc_now = get_utc_now()
    for image in Image.list(
        ecr_client=ecr_client,
        repository_name=repo_name,
        filter={"tagStatus": "UNTAGGED"},
    ):
        image_pushed_at = image.image_pushed_at
        if image_pushed_at.tzinfo is None:
            image_pushed_at = image_pushed_at.replace(tzinfo=timezone.utc)
        elapse = (image_pushed_at - utc_now).total_seconds()
        if elapse > expire:
            to_delete_image_list.append(image)
        if to_delete_image_list:
            ecr_client.batch_delete_image(
                repositoryName=repo_name,
                imageIds=[
                    {"imageDigest": img.image_digest} for img in to_delete_image_list
                ],
            )
        return to_delete_image_list
