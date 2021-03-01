"""
This script imports all of the required environment variables. If you are
running it locally, update the .env file with the environment variables only
available on your ci playform and run source.

Usage: source .env && python3.6 initialize.py
"""

import os

# PREFIX is the prefix of the name of the review apps created and deleted
# by these scripts. PREFIX is used by `delete.py` to determine which apps
# to delete after inactivity. So, it's important to use a prefix that won't
# be used by Dash developers when creating apps manually, otherwise this
# script may delete those apps!
PREFIX = "review-app-"

# LAST_UPDATE is the allowed amount of time before review apps are
# deleted from the server.
LAST_UPDATE = {"minutes": 1}

# TRUNK_BRANCHNAME is the name of your repository's "main" or "master"
# branch.
TRUNK_BRANCHNAME = "main"

# BRANCHNAME is the name of the branch you will initialize your Dash apps
# from.
BRANCHNAME = os.getenv("CIRCLE_BRANCH")

# REPONAME is the name of the repository that will hold the review app
# branches.
REPONAME = os.getenv("CIRCLE_PROJECT_REPONAME")

# TARGET_APPNAME is the name the Dash App that will serve as a review app
# template. This script will copy that apps configuration settings and
# apply them to all review apps.
TARGET_APPNAME = "qa-1"

# APPNAME determines how your review apps will be named.
APPNAME = f"{TARGET_APPNAME}-rev-{BRANCHNAME}"[0:30]

# DASH_ENTERPRISE_HOST is your Dash Enterprise Server's host address.
DASH_ENTERPRISE_HOST = "qa-de-410.plotly.host"

# SERVICE_USERNAME can be the username of any account that has admin privileges.
# That account will be used as a "Service Account" for app
# deployment and configuration.
SERVICE_USERNAME = "chris@plot.ly"

# SERVICE_API_KEY is the "Machine User's" API key used to access your Dash
# Enterprise server.
SERVICE_API_KEY = os.getenv("ADMIN_API_KEY")

# DASH_ENTERPRISE_USERNAME_TO_CI_USERNAME maps your developer
# usernames to the Version Control Platform username used to push changes to
# your review app repository. If you use the same SSO for both Dash Enterprise
# and your CI platform, then this mapping will be 1-1: the same SSO username
# will be the key and the value. In this case, you could delete this
# dictionary and use a list instead.
DASH_ENTERPRISE_USERNAME_TO_CI_USERNAME = {
    "criddyp": "criddyp",
    "tobinngo": "tobinngo",
}

# DASH_ENTERPRISE_USERNAME_TO_CI_API_KEY maps your developer
# usernames to their corresponding API key stored as environment variable
# in your CI platform settings.
DASH_ENTERPRISE_USERNAME_TO_CI_API_KEY = {
    "criddyp": "CRIDDYP_API_KEY",
    "tobinngo": "TOBINNGO_API_KEY",
}

# USERNAME is the Version Control Platform login of the user who pushed the
# code to Version Control Platform.
# It is mapped to a Dash Enterprise username that will author the
# initialized apps. (Make sure that this user has permission to view
# TARGET_APP or the app's initialization will fail)
CI_USERNAME = os.getenv("CIRCLE_USERNAME")

USERNAME = DASH_ENTERPRISE_USERNAME_TO_CI_USERNAME[CI_USERNAME]

# SERVICE_PRIVATE_SSH_KEY belongs to a Dash Enterprise user with admin
# privileges. This user will handle server deployment tasks.
SERVICE_PRIVATE_SSH_KEY = os.getenv("ADMIN_PRIVATE_SSH_KEY")

if (
    USERNAME in DASH_ENTERPRISE_USERNAME_TO_CI_USERNAME
    and DASH_ENTERPRISE_USERNAME_TO_CI_API_KEY
):
    print(
        "Reading the API key for {USERNAME} under the environment".format(
            USERNAME=USERNAME
        )
        + "variable {username_ci_api}\n".format(
            username_ci_api=(DASH_ENTERPRISE_USERNAME_TO_CI_API_KEY.get(USERNAME))
        )
    )

    USERNAME_API_KEY = os.getenv(DASH_ENTERPRISE_USERNAME_TO_CI_API_KEY.get(USERNAME))
else:
    print("API key was not fetched")
    print(
        """
        {USERNAME} is missing from
        DASH_ENTERPRISE_USERNAME_TO_CI_USERNAME and
        DASH_ENTERPRISE_USERNAME_TO_CI_API_KEY dictionaries.

        See Getting Started section in Continuous Integration Docs
        (https://{DASH_ENTERPRISE_HOST}/Docs/continuous-integration)
        for more information or contact your Dash Enterprise
        administrator.

        """.format(
            USERNAME=USERNAME,
            DASH_ENTERPRISE_HOST=DASH_ENTERPRISE_HOST,
        )
    )
