# -*- coding: utf-8 -*-

import json
from simple_aws_ecr.model import ReplicationRule, Destination, RepositoryFilter
from simple_aws_ecr.recipe import (
    Policy,
    configure_cross_account_lambda_get,
    configure_replication_for_source_registry,
    configure_replication_for_destination_registry,
    DestinationInfo,
    configure_cross_account_replication,
)
from simple_aws_ecr.tests.mock_aws import BaseMockAwsTest


class Test1(BaseMockAwsTest):
    use_mock = True

    def test_replication(self):
        devops_aws_account_id = self.bsm.aws_account_id
        user_aws_account_id = "999988887777"

        configure_replication_for_source_registry(
            ecr_client=self.ecr_client,
            rules=[
                ReplicationRule(
                    destinations=[
                        Destination(
                            region=self.bsm.aws_region,
                            registryId=user_aws_account_id,
                        )
                    ],
                    repositoryFilters=[
                        RepositoryFilter(
                            filter="PREFIX_MATCH",
                            filterType="test",
                        ),
                    ],
                ),
            ],
        )
        configure_replication_for_source_registry(
            ecr_client=self.ecr_client,
            rules=[
                ReplicationRule(
                    destinations=[
                        Destination(
                            region=self.bsm.aws_region,
                            registryId=user_aws_account_id,
                        )
                    ],
                    repositoryFilters=[
                        RepositoryFilter(
                            filter="PREFIX_MATCH",
                            filterType="test",
                        ),
                    ],
                ),
            ],
        )

        configure_replication_for_destination_registry(
            ecr_client=self.ecr_client,
            source_account_id_list=[devops_aws_account_id],
            target_account_id=user_aws_account_id,
            target_region=self.bsm.aws_region,
        )
        configure_replication_for_destination_registry(
            ecr_client=self.ecr_client,
            source_account_id_list=[devops_aws_account_id],
            target_account_id=user_aws_account_id,
            target_region=self.bsm.aws_region,
        )


class Test2(BaseMockAwsTest):
    use_mock = True

    def test_configure_cross_account_replication(self):
        repo_name = "shared_test_repo"
        self.bsm.ecr_client.create_repository(repositoryName=repo_name)
        source_bsm = self.bsm
        target_bsm = self.bsm
        target_aws_account_id = "999999999999"
        configure_cross_account_replication(
            repo_prefix_filter="shared_",
            source_aws_account_id=source_bsm.aws_account_id,
            source_boto_ses=source_bsm.boto_ses,
            dest_info_list=[
                DestinationInfo(
                    target_boto_ses=target_bsm.boto_ses,
                    target_aws_account_id=target_aws_account_id,
                    target_aws_region="us-east-1",
                ),
                DestinationInfo(
                    target_boto_ses=target_bsm.boto_ses,
                    target_aws_account_id=target_aws_account_id,
                    target_aws_region="us-east-2",
                ),
            ],
        )
        policy_document = json.loads(
            source_bsm.ecr_client.get_registry_policy()["policyText"]
        )
        policy = Policy.from_policy_document(policy_document)
        assert len(policy.statements) == 1
        stat = policy_document["Statement"][0]
        assert stat["Principal"]["AWS"] == [
            f"arn:aws:iam::{source_bsm.aws_account_id}:root"
        ]
        assert stat["Resource"] == [
            f"arn:aws:ecr:{source_bsm.aws_region}:{target_aws_account_id}:repository/*"
        ]


class Test3(BaseMockAwsTest):
    use_mock = True

    def test_lambda_get(self):
        account_devops = self.bsm.aws_account_id
        account_user = "999988887777"
        repo_name = "test-repo"
        lbd_func_name_prefix = "test-lbd"

        self.ecr_client.create_repository(repositoryName=repo_name)
        configure_cross_account_lambda_get(
            ecr_client=self.ecr_client,
            repo_name=repo_name,
            aws_account_id_list=[account_user],
            aws_region=self.bsm.aws_region,
            lbd_func_name_prefix=lbd_func_name_prefix,
        )
        configure_cross_account_lambda_get(
            ecr_client=self.ecr_client,
            repo_name=repo_name,
            aws_account_id_list=[account_user],
            aws_region=self.bsm.aws_region,
            lbd_func_name_prefix=lbd_func_name_prefix,
        )


if __name__ == "__main__":
    from simple_aws_ecr.tests import run_cov_test

    run_cov_test(__file__, "simple_aws_ecr.recipe", preview=False)
