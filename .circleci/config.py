import logging
import os

DEBUG = os.getenv("DEBUG", "false")
# Enable Requests debugging by setting this variable to "true"

if os.getenv("CIRCLECI") == "true":
    print("CIRCLECI")

    USERS = {
        # "service": "SERVICE_API_KEY",
        # "developers":"DEVELOPERS_API_KEY",
        # "criddyp": "CRIDDYP_API_KEY",
        "tobinngo": "TOBINNGO_API_KEY",
        "dev1": "DEV1_API_KEY",
        "dev2": "DEV2_API_KEY",
        "dev3": "DEV3_API_KEY",
        "admin": "ADMIN_API_KEY",
    }
    # USERS maps your developer usernames to their corresponding API key store 
    # as environment variable in your CircleCI Project Settings.

    SERVICE_USERNAME = "admin"

    USERNAME = "admin"
    # USERNAME is the Dash Enterprise username that will author the 
    # initialized apps. Make sure that this user has permission to view 
    # TARGET_APP or the app's initialization will fail.

    REPONAME = os.getenv("CIRCLE_PROJECT_REPONAME")
    # REPONAME is the name of the repository that will hold the review app 
    # branches.

    BRANCHNAME = os.getenv("CIRCLE_BRANCH")
    # BRANCHNAME is the name of the branch you will initialize your Dash apps 
    # from. This will be pulled from the CircleCI's environment. BRANCHNAME 
    # must not exceed 30 characters in length.
    
    TRUNK_BRANCHNAME = "main"
    # TRUNK_BRANCHNAME is the name of your repositories "main" or "master" 
    # branch.

    TARGET_APPNAME = "target-dev2"
    # TARGET_APPNAME is the name the Dash App that will serve as a review app
    # template. This script will copy that apps configuration settings and 
    # apply them to all review apps. You must have permission to view the 
    # TARGET_APP or the app's initialization will fail.

    APPNAME = f"{TARGET_APPNAME}-rev-{BRANCHNAME}"[0:30]
    # APPNAME determines how your review apps will be named. APPNAME must not
    # exceed 30 characters in length.

    DASH_ENTERPRISE_HOST = "qa-de-410.plotly.host" 
    # DASH_ENTERPRISE_HOST is your Dash Enterprise Server's host address.

    SSH_CONFIG = f"Host {DASH_ENTERPRISE_HOST},    HostName {DASH_ENTERPRISE_HOST},    User {USERNAME},    Port 3022,    IdentityFile ~/.ssh/id_rsa,    StrictHostKeyChecking no,    UserKnownHostsFile /dev/null"
    # SSH_CONFIG contains your SSH settings for Dash app deployment.

    SERVICE_PRIVATE_SSH_KEY = os.getenv("ADMIN_PRIVATE_SSH_KEY")
    # SERVICE_PRIVATE_SSH_KEY belongs to a Dash Enterprise user with admin
    # privileges. This user will handle all of the server deployment tasks.

    SERVICE_PUBLIC_SSH_KEY = os.getenv("ADMIN_PUBLIC_SSH_KEY")
    # SERVICE_PUBLIC_SSH_KEY used to authenticate the SSH hot.

    print("Fetching API key...", end=" ")

    if USERNAME in USERS and os.getenv(USERS.get(USERNAME)) != None:
        print("OK")
        print(f"    {USERNAME}")
        USERNAME_API_KEY = os.getenv(USERS.get(USERNAME))
    else:
        print("FAILED")
        print(
            f"""

            {USERNAME} is missing from \"config.py\" USERS dictionary.

            See Getting Started section in Continuous Integration Docs
            (https://{DASH_ENTERPRISE_HOST}/Docs/continuous-integration)
            for more information or contact your Dash Enterprise
            administrator.
            """
        )
        raise ValueError
