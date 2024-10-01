# -*- coding: utf-8 -*-

import typing as T
import moto
import boto3
from boto_session_manager import BotoSesManager

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ecr.client import ECRClient


class BaseMockAwsTest:
    use_mock: bool = True

    mock_aws: "moto.mock_aws" = None
    bsm: BotoSesManager = None
    boto_ses: boto3.Session = None
    ecr_client: "ECRClient" = None

    @classmethod
    def setup_class(cls):
        if cls.use_mock:
            cls.mock_aws = moto.mock_aws()
            cls.mock_aws.start()

        if cls.use_mock:
            cls.bsm = BotoSesManager(region_name="us-east-1")
        else:
            cls.bsm = BotoSesManager(
                profile_name="bmt_app_dev_us_east_1",
                region_name="us-east-1",
            )

        cls.boto_ses = cls.bsm.boto_ses

        cls.ecr_client = cls.boto_ses.client("ecr")

        cls.setup_class_post_hook()

    @classmethod
    def setup_class_post_hook(cls):
        pass

    @classmethod
    def teardown_class(cls):
        if cls.use_mock:
            cls.mock_aws.stop()
