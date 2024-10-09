# -*- coding: utf-8 -*-

"""
AWS ECR (Elastic Container Registry) Object-Oriented Interface

This module provides an object-oriented interface for interacting with AWS ECR
(Elastic Container Registry) repositories and images. It offers a higher-level
abstraction over the boto3 ECR client, making it easier to manage ECR resources.
"""

import typing as T
import enum
import hashlib
import dataclasses
from datetime import datetime

import botocore.exceptions

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ecr.client import ECRClient


@dataclasses.dataclass
class Base:
    def to_dict(self) -> T.Dict[str, T.Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: T.Dict[str, T.Any]) -> "Base":
        return cls(**data)

    @property
    def hash_key(self) -> str:  # pragma: no cover
        """
        Return a unique hash key for the object.
        """
        raise NotImplementedError

    @property
    def fingerprint(self) -> str:  # pragma: no cover
        """
        Return a unique fingerprint for the object.
        """
        return hashlib.md5(self.hash_key.encode("utf-8")).hexdigest()


class ImageTagMutability(str, enum.Enum):
    """
    The tag mutability setting for an ECR repository.
    """
    MUTABLE = "MUTABLE"
    IMMUTABLE = "IMMUTABLE"


@dataclasses.dataclass
class Repository(Base):
    """
    Represents an ECR repository with its properties and methods for retrieval and listing.

    :param registry_id: The AWS account ID associated with the registry.
    :param repository_name: The name of the repository.
    :param repository_uri: The URI of the repository.
    :param repository_arn: The Amazon Resource Name (ARN) of the repository.
    :param created_at: The date and time when the repository was created.
    :param image_tag_mutability: The tag mutability setting for the repository.
    :param image_scanning_configuration: The image scanning configuration for the repository.
    :param encryption_configuration: The encryption configuration for the repository.
    :param response: The full response from the ECR API call.
    """

    registry_id: str = dataclasses.field()
    repository_name: str = dataclasses.field()
    repository_uri: str = dataclasses.field(default=None)
    repository_arn: str = dataclasses.field(default=None)
    created_aAt: datetime = dataclasses.field(default=None)
    image_tag_mutability: str = dataclasses.field(default=None)
    image_scanning_configuration: dict = dataclasses.field(default=None)
    encryption_configuration: dict = dataclasses.field(default=None)
    response: T.Optional[dict] = dataclasses.field(default=None)

    @classmethod
    def from_describe_repositories_response(
        cls,
        response: T.Dict[str, T.Any],
    ):
        """
        Create a Repository instance from the ECR describe_repositories API response.

        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/describe_repositories.html
        """
        return cls(
            registry_id=response["registryId"],
            repository_name=response["repositoryName"],
            repository_uri=response.get("repositoryUri"),
            repository_arn=response.get("repositoryArn"),
            created_aAt=response.get("createdAt"),
            image_tag_mutability=response.get("imageTagMutability"),
            image_scanning_configuration=response.get("imageScanningConfiguration"),
            encryption_configuration=response.get("encryptionConfiguration"),
            response=response,
        )

    @classmethod
    def get(
        cls,
        ecr_client: "ECRClient",
        repository_name: str,
        registry_id: T.Optional[str] = None,
    ) -> T.Optional["Repository"]:
        """
        Retrieve a single repository by name.

        :param ecr_client: The boto3 ECR client.
        :param repository_name: The name of the repository to retrieve.
        :param registry_id: The AWS account ID associated with the registry.
        """
        kwargs = dict(repositoryNames=[repository_name])
        if registry_id:  # pragma: no cover
            kwargs["registryId"] = registry_id
        try:
            res = ecr_client.describe_repositories(**kwargs)
            return cls.from_describe_repositories_response(res["repositories"][0])
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "RepositoryNotFoundException":
                return None
            else:  # pragma: no cover
                raise e

    @classmethod
    def list(
        cls,
        ecr_client: "ECRClient",
        repository_names: T.Optional[T.List[str]] = None,
        registry_id: T.Optional[str] = None,
    ) -> T.Iterator["Repository"]:
        """
        Based on AWS service quota document https://docs.aws.amazon.com/AmazonECR/latest/userguide/service-quotas.html,
        the maximum number of repositories per account is 10,000 per region.

        :param ecr_client: The boto3 ECR client.
        :param repository_names: List of repository names to filter by.
        :param registry_id: The AWS account ID associated with the registry.
        """
        paginator = ecr_client.get_paginator("describe_repositories")
        kwargs = dict(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 1000,
            }
        )
        if registry_id:  # pragma: no cover
            kwargs["registryId"] = registry_id
        if repository_names:
            kwargs["repositoryNames"] = repository_names
        response_iterator = paginator.paginate(**kwargs)
        for response in response_iterator:
            for repo in response.get("repositories", []):
                yield cls.from_describe_repositories_response(repo)


@dataclasses.dataclass
class Image(Base):
    """
    Represents an ECR image with its properties and methods for retrieval and listing.

    :param registry_id: The AWS account ID associated with the registry.
    :param repository_name: The name of the repository containing the image.
    :param image_digest: The sha256 digest of the image manifest.
    :param image_tagsof str): The tags associated with the image.
    :param image_size_in_bytes: The size of the image in bytes.
    :param image_pushed_at: The date and time when the image was pushed.
    :param image_scan_status: The status of the image scan.
    :param image_scan_findings_summary: A summary of findings from the image scan.
    :param image_manifest_media_type: The media type of the image manifest.
    :param artifact_media_type: The media type of the image artifact.
    :param last_recorded_pull_time: The last time the image was pulled.
    :param response: The full response from the ECR API call.
    """

    registry_id: str = dataclasses.field()
    repository_name: str = dataclasses.field()
    image_digest: str = dataclasses.field()
    image_tags: T.List[str] = dataclasses.field(default=None)
    image_size_in_bytes: int = dataclasses.field(default=None)
    image_pushed_at: datetime = dataclasses.field(default=None)
    image_scan_status: dict = dataclasses.field(default=None)
    image_scan_findings_summary: dict = dataclasses.field(default=None)
    image_manifest_media_type: str = dataclasses.field(default=None)
    artifact_media_type: str = dataclasses.field(default=None)
    last_recorded_pull_time: datetime = dataclasses.field(default=None)
    response: T.Optional[dict] = dataclasses.field(default=None)

    @classmethod
    def from_describe_images_response(
        cls,
        response: T.Dict[str, T.Any],
    ):  # pragma: no cover
        """
        Create an Image instance from the ECR describe_images API response.

        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/describe_images.html
        """
        return cls(
            registry_id=response["registryId"],
            repository_name=response["repositoryName"],
            image_digest=response["imageDigest"],
            image_tags=response.get("imageTags"),
            image_size_in_bytes=response.get("imageSizeInBytes"),
            image_pushed_at=response.get("imagePushedAt"),
            image_scan_status=response.get("imageScanStatus"),
            image_scan_findings_summary=response.get("imageScanFindingsSummary"),
            image_manifest_media_type=response.get("imageManifestMediaType"),
            artifact_media_type=response.get("artifactMediaType"),
            last_recorded_pull_time=response.get("lastRecordedPullTime"),
            response=response,
        )

    @classmethod
    def get_by_digest(
        cls,
        ecr_client: "ECRClient",
        repository_name: str,
        image_digest: str,
        registry_id: T.Optional[str] = None,
    ) -> T.Optional["Image"]:  # pragma: no cover
        """
        Retrieve a single image by its digest.

        :param ecr_client: The boto3 ECR client.
        :param repository_name: The name of the repository containing the image.
        :param image_digest: The sha256 digest of the image manifest.
        :param registry_id: The AWS account ID associated with the registry.
        """
        if image_digest.startswith("sha256:") is False:
            image_digest = f"sha256:{image_digest}"
        kwargs = dict(
            repositoryName=repository_name, imageIds=[{"imageDigest": image_digest}]
        )
        if registry_id:
            kwargs["registryId"] = registry_id
        try:
            res = ecr_client.describe_images(**kwargs)
            return cls.from_describe_images_response(res["imageDetails"][0])
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ImageNotFoundException":
                return None
            else:  # pragma: no cover
                raise e

    @classmethod
    def get_by_tag(
        cls,
        ecr_client: "ECRClient",
        repository_name: str,
        image_tag: str,
        registry_id: T.Optional[str] = None,
    ) -> T.Optional["Image"]:  # pragma: no cover
        """
        Retrieve a single image by its tag.

        :param ecr_client: The boto3 ECR client.
        :param repository_name: The name of the repository containing the image.
        :param image_tag: The tag of the image to retrieve.
        :param registry_id: The AWS account ID associated with the registry.
        """
        kwargs = dict(
            repositoryName=repository_name,
            imageIds=[{"imageTag": image_tag}],
        )
        if registry_id:
            kwargs["registryId"] = registry_id
        try:
            res = ecr_client.describe_images(**kwargs)
            return cls.from_describe_images_response(res["imageDetails"][0])
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ImageNotFoundException":
                return None
            else:  # pragma: no cover
                raise e

    @classmethod
    def list(
        cls,
        ecr_client: "ECRClient",
        repository_name: str,
        registry_id: T.Optional[str] = None,
        filter: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> T.Iterator["Image"]:  # pragma: no cover
        """
        List images in an ECR repository.

        :param ecr_client: The boto3 ECR client.
        :param repository_name: The name of the repository containing the image.
        :param registry_id: The AWS account ID associated with the registry.
        :param filter: A dictionary of filters to apply to the list operation.
        """
        paginator = ecr_client.get_paginator("describe_images")
        kwargs = dict(
            repositoryName=repository_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 1000,
            },
        )
        if registry_id:
            kwargs["registryId"] = registry_id
        if filter:
            kwargs["filter"] = filter
        response_iterator = paginator.paginate(**kwargs)
        for response in response_iterator:
            for image in response.get("imageDetails", []):
                yield cls.from_describe_images_response(image)


@dataclasses.dataclass
class Destination(Base):
    """
    todo: add docstring
    """

    region: str = dataclasses.field()
    registryId: str = dataclasses.field()

    @property
    def hash_key(self) -> str:
        return f"registryId={self.registryId},region={self.region}"


@dataclasses.dataclass
class RepositoryFilter(Base):
    """
    todo: add docstring
    """

    filter: str = dataclasses.field()
    filterType: str = dataclasses.field(default="PREFIX_MATCH")

    @property
    def hash_key(self) -> str:
        return f"filterType={self.filterType},filter={self.filter}"


@dataclasses.dataclass
class ReplicationRule(Base):
    """
    Represents an ECR replication rule with its properties and methods for retrieval and listing.
    """

    destinations: T.List[Destination] = dataclasses.field()
    repositoryFilters: T.List[RepositoryFilter] = dataclasses.field()

    @classmethod
    def from_dict(cls, data: T.Dict[str, T.Any]):
        destinations = [Destination(**d) for d in data["destinations"]]
        repositoryFilters = [RepositoryFilter(**r) for r in data["repositoryFilters"]]
        return cls(destinations=destinations, repositoryFilters=repositoryFilters)

    @property
    def hash_key(self) -> str:
        destinations = [des.hash_key for des in self.destinations]
        destinations.sort()
        repositoryFilters = [rep.hash_key for rep in self.repositoryFilters]
        repositoryFilters.sort()
        return "{}|{}".format(
            "&".join(destinations),
            "&".join(repositoryFilters),
        )
