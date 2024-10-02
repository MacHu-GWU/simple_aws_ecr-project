.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.1.4 (2024-10-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- Fix a bug that when AWS automatically convert single principal to str, this library cannot handle it problem.


0.1.3 (2024-10-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Miscellaneous**

- House keeping work.


0.1.2 (2024-10-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Miscellaneous**

- House keeping work.


0.1.1 (2024-10-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release.
- Add the following public API:
    - ``simple_aws_ecr.api.get_ecr_registry_url``
    - ``simple_aws_ecr.api.get_ecr_image_uri``
    - ``simple_aws_ecr.api.get_ecr_auth_token``
    - ``simple_aws_ecr.api.docker_login``
    - ``simple_aws_ecr.api.ecr_login``
    - ``simple_aws_ecr.api.EcrContext``
    - ``simple_aws_ecr.api.Repository``
    - ``simple_aws_ecr.api.Image``
    - ``simple_aws_ecr.api.Destination``
    - ``simple_aws_ecr.api.RepositoryFilter``
    - ``simple_aws_ecr.api.ReplicationRule``
    - ``simple_aws_ecr.api.configure_replication_for_source_registry``
    - ``simple_aws_ecr.api.configure_replication_for_destination_registry``
    - ``simple_aws_ecr.api.SID_ALLOW_CROSS_ACCOUNT_GET``
    - ``simple_aws_ecr.api.SID_ALLOW_CROSS_ACCOUNT_LBD_GET``
    - ``simple_aws_ecr.api.configure_cross_account_lambda_get``
    - ``simple_aws_ecr.api.delete_untagged_image``


0.0.1 (2024-10-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Check if the name is already taken.
