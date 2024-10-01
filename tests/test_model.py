# -*- coding: utf-8 -*-

from simple_aws_ecr.model import Repository
from simple_aws_ecr.tests.mock_aws import BaseMockAwsTest


class Test(BaseMockAwsTest):
    def test(self):
        repo_name = "test-repo"
        repo = Repository.get(
            ecr_client=self.ecr_client,
            repository_name=repo_name,
        )
        assert repo is None

        self.ecr_client.create_repository(repositoryName=repo_name)

        repo = Repository.get(
            ecr_client=self.ecr_client,
            repository_name=repo_name,
        )

        repo_list = list(Repository.list(ecr_client=self.ecr_client))
        assert len(repo_list) == 1
        assert repo_list[0].repository_name == repo_name


if __name__ == "__main__":
    from simple_aws_ecr.tests import run_cov_test

    run_cov_test(__file__, "simple_aws_ecr.model", preview=False)
