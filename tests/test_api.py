# -*- coding: utf-8 -*-

from simple_aws_ecr import api


def test():
    _ = api
    _ = api.ImageTagMutability
    _ = api.Repository
    _ = api.Image
    _ = api.Destination
    _ = api.RepositoryFilter
    _ = api.ReplicationRule
    _ = api.get_ecr_registry_url
    _ = api.get_ecr_image_uri
    _ = api.get_ecr_auth_token
    _ = api.docker_login
    _ = api.ecr_login
    _ = api.EcrContext
    _ = api.EcrRepoRelease
    _ = api.SID_ALLOW_CROSS_ACCOUNT_GET
    _ = api.SID_ALLOW_CROSS_ACCOUNT_LBD_GET
    _ = api.Policy
    _ = api.build_cross_account_get_statement
    _ = api.build_cross_account_lbd_get_statement
    _ = api.configure_cross_account_lambda_get
    _ = api.configure_replication_for_source_registry
    _ = api.configure_replication_for_destination_registry
    _ = api.switch_boto_ses_region
    _ = api.DestinationInfo
    _ = api.configure_cross_account_replication
    _ = api.delete_untagged_image


if __name__ == "__main__":
    from simple_aws_ecr.tests import run_cov_test

    run_cov_test(__file__, "simple_aws_ecr.api", preview=False)
