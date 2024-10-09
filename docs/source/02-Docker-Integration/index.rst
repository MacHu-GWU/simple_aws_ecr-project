Docker Integration
==============================================================================
- :func:`simple_aws_ecr.docker.get_ecr_registry_url`
- :func:`simple_aws_ecr.docker.get_ecr_image_uri`
- :func:`simple_aws_ecr.docker.get_ecr_auth_token`
- :func:`simple_aws_ecr.docker.docker_login`
- :func:`simple_aws_ecr.docker.ecr_login`
- :class:`~simple_aws_ecr.docker.EcrContext`
- :meth:`EcrContext.build_image <simple_aws_ecr.docker.EcrContext.build_image>`
- :meth:`EcrContext.push_image <simple_aws_ecr.docker.EcrContext.push_image>`
- :meth:`EcrContext.test_image <simple_aws_ecr.docker.EcrContext.test_image>`
- :class:`~simple_aws_ecr.docker.EcrRepoRelease`
- :meth:`EcrRepoRelease.create_release_repo <simple_aws_ecr.docker.EcrRepoRelease.create_release_repo>`
- :meth:`EcrRepoRelease.release_image <simple_aws_ecr.docker.EcrRepoRelease.release_image>`
