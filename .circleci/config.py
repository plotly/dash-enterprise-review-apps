import logging
import os

DEBUG = os.getenv("DEBUG", "false")
# Enable Requests debugging by setting this variable to "true"

if os.getenv("CIRCLECI") == "true":
    print("CIRCLECI")

    PREFIX = "target"
    # PREFIX is a filter for purging review apps.

    LAST_UPDATE = {"minutes": 1}
    # LAST_UPDATE is the allowed amount of time before review apps are 
    # purged from the server.
    
    TRUNK_BRANCHNAME = "main"
    # TRUNK_BRANCHNAME is the name of your repository's "main" or "master" 
    # branch.

    BRANCHNAME = os.getenv("CIRCLE_BRANCH")
    # BRANCHNAME is the name of the branch you will initialize your Dash apps 
    # from. This will be pulled from the CircleCI's environment. BRANCHNAME 
    # must not exceed 30 characters in length.

    REPONAME = os.getenv("CIRCLE_PROJECT_REPONAME")
    # REPONAME is the name of the repository that will hold the review app 
    # branches.

    TARGET_APPNAME = "chris-qa-1"
    # TARGET_APPNAME is the name the Dash App that will serve as a review app
    # template. This script will copy that apps configuration settings and 
    # apply them to all review apps. App must exist and you must have 
    # permission to view the TARGET_APP or the app's initialization will fail.

    APPNAME = f"{TARGET_APPNAME}-rev-{BRANCHNAME}"[0:30]
    # APPNAME determines how your review apps will be named. APPNAME must not
    # exceed 30 characters in length.

    DASH_ENTERPRISE_HOST = "qa-de-410.plotly.host" 
    # DASH_ENTERPRISE_HOST is your Dash Enterprise Server's host address.

    SERVICE_API_KEY = os.getenv("ADMIN_API_KEY")
    # SERVICE_API_KEY is the "Machine User's" API key used to access your Dash
    # Enterprise server.

    SERVICE_USERNAME = "admin"
    # SERVICE_USERNAME is a "Machine User" that will handle all aspects of Dash 
    # app management.

    USERNAME = os.getenv("CIRCLE_USERNAME")
    # USERNAME is the GitHub login of the user who pushed the code to Github.
    # It is mapped to a Dash Enterprise username that will author the 
    # initialized apps. (Make sure that this user has permission to view 
    # TARGET_APP or the app's initialization will fail)

    DASH_ENTERPRISE_USERNAME_TO_CIRCLECI_USERNAME = {
        "criddyp" : "criddyp",
        "tobinngo": "tobinngo",
    }
    # DASH_ENTERPRISE_USERNAME_TO_CIRCLECI_USERNAME maps your developer 
    # usernames to the GitHub username used to push changes to your review app
    # repository.

    DASH_ENTERPRISE_USERNAME_TO_CIRCLE_CI_API_KEY = {
        "criddyp": "CRIDDYP_API_KEY",
        "tobinngo": "TOBINNGO_API_KEY",
    }
    # DASH_ENTERPRISE_USERNAME_TO_CIRCLE_CI_API_KEY maps your developer 
    # usernames to their corresponding API key stored as environment variable 
    # in your CircleCI Project Settings.

    # USERS = {
    #     # "service": "SERVICE_API_KEY",
    #     # "developers":"DEVELOPERS_API_KEY",
    #     "criddyp": "CRIDDYP_API_KEY",
    #     "tobinngo": "TOBINNGO_API_KEY",
    #     "dev1": "DEV1_API_KEY",
    #     "dev2": "DEV2_API_KEY",
    #     "dev3": "DEV3_API_KEY",
    #     "admin": "ADMIN_API_KEY",
    # }
    # # USERS maps your developer usernames to their corresponding API key store 
    # # as environment variable in your CircleCI Project Settings.

    SSH_CONFIG = f"Host {DASH_ENTERPRISE_HOST},    HostName {DASH_ENTERPRISE_HOST},    User {USERNAME},    Port 3022,    IdentityFile ~/.ssh/id_rsa,    StrictHostKeyChecking no,    UserKnownHostsFile /dev/null"
    # SSH_CONFIG contains your SSH settings for Dash app deployment.

    SERVICE_PRIVATE_SSH_KEY = os.getenv("ADMIN_PRIVATE_SSH_KEY")
    # SERVICE_PRIVATE_SSH_KEY belongs to a Dash Enterprise user with admin
    # privileges. This user will handle all of the server deployment tasks.

    SERVICE_PUBLIC_SSH_KEY = os.getenv("ADMIN_PUBLIC_SSH_KEY")
    # SERVICE_PUBLIC_SSH_KEY used to authenticate the SSH host

    print("Fetching API key...", end=" ")

    if (
        USERNAME in DASH_ENTERPRISE_USERNAME_TO_CIRCLECI_USERNAME and 
        DASH_ENTERPRISE_USERNAME_TO_CIRCLE_CI_API_KEY
    ):
        print("OK")
    else:
        print("FAILED")
        print(
            f"""
            {USERNAME} is missing from 
            DASH_ENTERPRISE_USERNAME_TO_CIRCLECI_USERNAME and
            DASH_ENTERPRISE_USERNAME_TO_CIRCLE_CI_API_KEY dictionaries.

            See Getting Started section in Continuous Integration Docs
            (https://{DASH_ENTERPRISE_HOST}/Docs/continuous-integration)
            for more information or contact your Dash Enterprise
            administrator.
            """
        )
    # Verifies that relevant usernames are found in both dictionaries

    # if USERNAME in USERS and os.getenv(USERS.get(USERNAME)) != None:
    #     print("OK")
    #     print(f"    {USERNAME}")
    #     USERNAME_API_KEY = os.getenv(USERS.get(USERNAME))
    # else:
    #     print("FAILED")
    #     print(
    #         f"""

    #         {USERNAME} is missing from \"config.py\" USERS dictionary.

    #         See Getting Started section in Continuous Integration Docs
    #         (https://{DASH_ENTERPRISE_HOST}/Docs/continuous-integration)
    #         for more information or contact your Dash Enterprise
    #         administrator.
    #         """
    #     )
    #     raise ValueError
