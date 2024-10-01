# -*- coding: utf-8 -*-

from simple_aws_ecr.model import ReplicationRule, Destination, RepositoryFilter
from simple_aws_ecr.recipe import (
    configure_cross_account_lambda_get,
    configure_replication_for_source_registry,
    configure_replication_for_destination_registry,
)
from simple_aws_ecr.tests.mock_aws import BaseMockAwsTest


class Test(BaseMockAwsTest):
    use_mock = True

    def test_replication(self):
        account_devops = self.bsm.aws_account_id
        account_user = "999988887777"

        configure_replication_for_source_registry(
            ecr_client=self.ecr_client,
            rules=[
                ReplicationRule(
                    destinations=[
                        Destination(
                            region=self.bsm.aws_region,
                            registryId=account_user,
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
                            registryId=account_user,
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
            source_account_id_list=[account_devops],
            target_account_id=account_user,
            target_region=self.bsm.aws_region,
        )
        configure_replication_for_destination_registry(
            ecr_client=self.ecr_client,
            source_account_id_list=[account_devops],
            target_account_id=account_user,
            target_region=self.bsm.aws_region,
        )

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
