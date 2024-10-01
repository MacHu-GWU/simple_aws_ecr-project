# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from rich import print as rprint
from simple_aws_ecr.model import Repository, Image
from simple_aws_ecr.recipe import delete_untagged_image


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
aws_profile = "bmt_app_devops_us_east_1"
repo_name = "dynamodbsnaplake_image"
digest = "sha256:2f6c2354fb1371ffc7a951cc69efe75b4819a79b8cd19396c24cc5a343d2199b"
tag = "0.1.16"

bsm = BotoSesManager(profile_name=aws_profile)
ecr_client = bsm.ecr_client


def test_repo():
    repo_list = Repository.list(ecr_client=ecr_client)
    rprint(list(repo_list))


def test_image():
    image = Image.get_by_digest(
        ecr_client=ecr_client,
        repository_name=repo_name,
        image_digest=digest,
    )
    # rprint(image)

    image = Image.get_by_tag(
        ecr_client=ecr_client,
        repository_name=repo_name,
        image_tag=tag,
    )
    # rprint(image)

    image = Image.get_by_digest(
        ecr_client=ecr_client,
        repository_name=repo_name,
        image_digest="sha256:1a2b3c",
    )
    assert image is None

    image = Image.get_by_tag(
        ecr_client=ecr_client,
        repository_name=repo_name,
        image_tag="0.0.0",
    )
    assert image is None

    image_list = list(Image.list(ecr_client=ecr_client, repository_name=repo_name))
    rprint(image_list)

    delete_untagged_image(
        ecr_client=ecr_client,
        repo_name=repo_name,
        expire=20 * 365 * 24 * 60 * 60,
    )


# test_repo()
# test_image()
