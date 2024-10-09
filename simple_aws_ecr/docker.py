# -*- coding: utf-8 -*-

"""
Make docker cli easier to work with AWS ECR.
"""

import typing as T
import json
import base64
import subprocess
import dataclasses
from pathlib import Path

from .vendor.better_pathlib import temp_cwd
from .model import Repository

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    from mypy_boto3_ecr.client import ECRClient


def get_ecr_registry_url(
    aws_account_id: str,
    aws_region: str,
):  # pragma: no cover
    """
    Get the full ECR registry URL.

    :param aws_account_id: The AWS account id of your ECR repo.
    :param aws_region: The AWS region of your ECR repo
    """
    return f"https://{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com"


def get_ecr_image_uri(
    aws_account_id: str,
    aws_region: str,
    ecr_repo_name: str,
    tag: str,
) -> str:  # pragma: no cover
    """
    Get the full ECR repo URI with image tag.

    :param aws_account_id: The AWS account id of your ECR repo.
    :param aws_region: The AWS region of your ECR repo
    :param ecr_repo_name: the ECR repo name
    :param tag: the image tag
    """
    return f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{ecr_repo_name}:{tag}"


def get_ecr_auth_token(
    ecr_client: "ECRClient",
) -> T.Tuple[str, str]:  # pragma: no cover
    """
    Get ECR auth token using boto3 SDK.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/get_authorization_token.html

    :return: username and password
    """
    res = ecr_client.get_authorization_token()
    b64_token = res["authorizationData"][0]["authorizationToken"]
    user_pass = base64.b64decode(b64_token.encode("utf-8")).decode("utf-8")
    username, password = user_pass.split(":", 1)
    return username, password


def docker_login(
    username: str,
    password: str,
    registry_url: str,
) -> bool:  # pragma: no cover
    """
    Login docker cli to AWS ECR. Run:

    .. code-block:: bash

        echo ${password} | docker login -u ${username} --password-stdin ${registry_url}

    Reference:

    - https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html#registry-auth-token

    :return: a boolean flag to indicate if the login is successful.
    """
    args = ["echo", password]
    pipe = subprocess.Popen(args, stdout=subprocess.PIPE)
    args = ["docker", "login", "-u", username, registry_url, "--password-stdin"]
    response = subprocess.run(args, stdin=pipe.stdout, capture_output=True)
    text = response.stdout.decode("utf-8")
    is_succeeded = "Login Succeeded" in text
    return is_succeeded


def ecr_login(
    ecr_client: "ECRClient",
    aws_account_id: str,
    aws_region: str,
) -> bool:  # pragma: no cover
    """
    Login docker cli to AWS ECR using boto3 SDK and AWS CLI.

    :return: a boolean flag to indicate if the login is successful.
    """
    registry_url = get_ecr_registry_url(
        aws_account_id=aws_account_id,
        aws_region=aws_region,
    )
    username, password = get_ecr_auth_token(ecr_client=ecr_client)
    return docker_login(username, password, registry_url)


@dataclasses.dataclass
class EcrContext:
    """
    A utility class to help build and push docker image to ECR.

    :param aws_account_id: The AWS account id of your ECR repo.
    :param aws_region: The AWS region of your ECR repo
    :param repo_name: the repo name
    :param dir_dockerfile: the directory where the Dockerfile is located.
    """

    aws_account_id: str = dataclasses.field()
    aws_region: str = dataclasses.field()
    repo_name: str = dataclasses.field()
    path_dockerfile: Path = dataclasses.field()

    @classmethod
    def from_bsm(
        cls,
        bsm: "BotoSesManager",
        repo_name: str,
        path_dockerfile: Path,
    ):  # pragma: no cover
        """
        Create a new instance of EcrContext.

        :param bsm: ``boto_session_manager.BotoSesManager`` object.
        :param repo_name: ECR repo name.
        :param path_dockerfile: the path to the Dockerfile.
        """
        return cls(
            aws_account_id=bsm.aws_account_id,
            aws_region=bsm.aws_region,
            repo_name=repo_name,
            path_dockerfile=path_dockerfile,
        )

    @property
    def dir_dockerfile(self) -> Path:  # pragma: no cover
        return self.path_dockerfile.parent

    def get_image_uri(self, tag: str) -> str:  # pragma: no cover
        """
        Get the ECR container image URI.

        :param tag: the container image tag.
        """
        return get_ecr_image_uri(
            aws_account_id=self.aws_account_id,
            aws_region=self.aws_region,
            ecr_repo_name=self.repo_name,
            tag=tag,
        )

    def build_image(
        self,
        image_tag_list: T.Optional[T.List[str]] = None,
        additional_args: T.Optional[T.List[str]] = None,
    ):  # pragma: no cover
        """
        Build docker image.

        :param image_tag_list: the list of tag you want to give to the built image,
            e.g. ["latest", "0.1.1"]
        :param additional_args: additional command line arguments for ``docker build ...``

        .. note::

            If you are trying to build a linux/amd64 compatible image on an ARM chip Mac
            you need to set ``"--platform=linux/amd64"`` in the ``additional_args``.
        """
        if image_tag_list is None:
            image_tag_list = ["latest"]
        if additional_args is None:
            additional_args = []
        with temp_cwd(self.dir_dockerfile):
            args = ["docker", "build"]
            # Reference: https://docs.docker.com/engine/reference/commandline/build/#tag
            for tag in image_tag_list:
                args.extend(["-t", self.get_image_uri(tag)])
            args.extend(additional_args)
            args.append(".")
            # don't use check=True
            # the args may include sensitive information like aws credentials
            # we don't want to automatically print to the log
            # instead, we want to handle the error our self.
            result = subprocess.run(args)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode,
                    "'docker build' command did not exit successfully!",
                )

    def push_image(
        self,
        image_tag_list: T.Optional[T.List[str]] = None,
        additional_args: T.Optional[T.List[str]] = None,
    ):  # pragma: no cover
        """
        Push Docker image to ECR.
        """
        if image_tag_list is None:
            image_tag_list = ["latest"]
        if additional_args is None:
            additional_args = []
        with temp_cwd(self.dir_dockerfile):
            for tag in image_tag_list:
                args = [
                    "docker",
                    "push",
                    self.get_image_uri(tag),
                ]
                args.extend(additional_args)
                subprocess.run(args, check=True)

    def test_image(
        self,
        tag: T.Optional[str] = None,
        additional_args: T.Optional[T.List[str]] = None,
    ):  # pragma: no cover
        """
        Test the container image locally by running it.

        :param additional_args: additional command line arguments for ``docker run ...``
        """
        if tag is None:
            tag = "latest"
        if additional_args is None:
            additional_args = []
        with temp_cwd(self.dir_dockerfile):
            image_uri = self.get_image_uri(tag)
            args = [
                "docker",
                "run",
                "--rm",
                image_uri,
            ]
            args.extend(additional_args)
            subprocess.run(args, check=True)


@dataclasses.dataclass
class EcrRepoRelease:  # pragma: no cover
    """
    This class manages the workflow of Docker image promotion from development
    to production in an AWS ECR environment.

    The primary workflow involves:

    1. Continuous deployment of new image versions to a development ECR repository.
    2. Selection and promotion of mature versions to a production ECR repository.

    Other that, we will replicate production images across multiple AWS accounts
    and regions. This capability is provided by the
    :mod:`esc_docker_image_porter.replicate` module.

    This class defines relation between the develop repository and the release repository.
    They have to be in the same AWS account and same AWS region.
    """

    develop_repo_name: str = dataclasses.field()
    release_repo_name: str = dataclasses.field()

    def create_release_repo(
        self,
        ecr_client: "ECRClient",
        untagged_image_expire_time: int = 30,
        tags: T.Dict[str, str] = None,
    ):
        """
        Create a release repository and set the lifecycle policy.

        :param ecr_client: The boto3 ECR client.
        :param untagged_image_expire_time: The time (in days) to expire the untagged image.
        :param tags: The tags for the repository.
        """
        repo = Repository.get(
            ecr_client=ecr_client,
            repository_name=self.release_repo_name,
        )
        if tags is None:
            tags = dict()
        if repo is None:
            ecr_client.create_repository(
                repositoryName=self.release_repo_name,
                imageTagMutability="MUTABLE",
                tags=[dict(Key=k, Value=v) for k, v in tags.items()],
            )
            life_cycle_policy = {
                "rules": [
                    {
                        "rulePriority": 1,
                        "description": "string",
                        "selection": {
                            "tagStatus": "untagged",
                            "countType": "sinceImagePushed",
                            "countUnit": "days",
                            "countNumber": untagged_image_expire_time,
                        },
                        "action": {"type": "expire"},
                    }
                ]
            }
            ecr_client.put_lifecycle_policy(
                repositoryName=self.release_repo_name,
                lifecyclePolicyText=json.dumps(life_cycle_policy),
            )

    def release_image(
        self,
        ecr_client: "ECRClient",
        aws_account_id: str,
        aws_region: str,
        tag: str,
    ):
        """
        Release an image from the develop repository to the release repository.

        :param ecr_client: The boto3 ECR client.
        :param aws_account_id: The AWS account id of the release ECR repo.
        :param aws_region: The AWS region of the release ECR repo.
        :param tag: The image tag.
        """
        ecr_login(
            ecr_client=ecr_client,
            aws_account_id=aws_account_id,
            aws_region=aws_region,
        )
        uri_source = get_ecr_image_uri(
            aws_account_id=aws_account_id,
            aws_region=aws_region,
            ecr_repo_name=self.develop_repo_name,
            tag=tag,
        )
        uri_target = get_ecr_image_uri(
            aws_account_id=aws_account_id,
            aws_region=aws_region,
            ecr_repo_name=self.release_repo_name,
            tag=tag,
        )

        args = ["docker", "pull", uri_source]
        subprocess.run(args, check=True)

        args = ["docker", "tag", uri_source, uri_target]
        subprocess.run(args, check=True)

        args = ["docker", "push", uri_target]
        subprocess.run(args, check=True)
