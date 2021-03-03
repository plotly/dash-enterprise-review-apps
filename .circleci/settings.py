"""
This script imports all of the required environment variables. If you are
running it locally, update the .env file with the environment variables only
available on your ci playform and run source.

Usage: source .env && python3.6 initialize.py
"""
import os

# LAST_UPDATE is the allowed amount of time since a review app was last viewed
#  or updated, before it is deleted from the server.
# Typically this is {"days": 5}
PERIOD = "minutes"  # "minutes", "hours", "days"
TIME = 1
LAST_UPDATE = {PERIOD: TIME}

# Set this to the trunk branch that you'd like to have update your target app.
# When BRANCHNAME is TRUNK_BRANCHNAME, the script will deploy the changes to
# the target app. Otherwise, the script will create a new review app. This is
# branch is usually called "main", "master" or "dev".
TRUNK_BRANCHNAME = "main"

# BRANCHNAME should refer to the branch of the code that the review apps are
# created from. It is used when creating the name of the review app.
# Set this to the branch name provided by your CI system's environment
# variables. For example, in CircleCI this is CIRCLE_BRANCH
BRANCHNAME = os.getenv("CIRCLE_BRANCH")

# TARGET_APPNAME is the name the Dash App that will serve as a review app
# template. This script will copy that apps configuration settings and
# apply them to all review apps.
# When BRANCHNAME = TRUNK_BRANCHNAME, the changes on the branch will get
# deployed to this app.
TARGET_APPNAME = "aa-chris"

# PREFIX is a filter for deleting review apps.
PREFIX = "{TARGET_APPNAME}-rev-".format(TARGET_APPNAME=TARGET_APPNAME[:15])

# APPNAME determines how the review apps will be named.
APPNAME = "{PREFIX}{BRANCHNAME}".format(PREFIX=PREFIX, BRANCHNAME=BRANCHNAME)[:30]

# DASH_ENTERPRISE_HOST is your Dash Enterprise Server's host address.
# DASH_ENTERPRISE_HOST = "qa-de-410.plotly.host"
DASH_ENTERPRISE_HOST = "dash-playground.plotly.host"

# SERVICE_USERNAME can be the username of any account that has admin privileges.
# That account will be used as a "Service Account" for app
# deployment and configuration.
SERVICE_USERNAME = "service"

# SERVICE_API_KEY is the "Machine User's" API key used to access your Dash
# Enterprise server.
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")

# DE_USERNAME_TO_CI_USERNAME maps your developer
# usernames to the CI platform username used to push changes to
# your review app repository. If you use the same SSO for both Dash Enterprise
# and your CI platform, then this mapping will be 1-1: the same SSO username
# will be the key and the value. In this case, you could delete this
# dictionary a USERNAME = CI_USERNAME
DE_USERNAME_TO_CI_USERNAME = {
    "criddyp": "criddyp",
    "tobinngo": "tobinngo",
    "service": "service",
}

# DE_USERNAME_TO_CI_API_KEY maps your Dash Enterprise developer
# usernames to the name of a CI environment variable in your CI platform that
# contains their Dash Enterprise API key.
DE_USERNAME_TO_CI_API_KEY = {
    "criddyp": "CRIDDYP_API_KEY",
    "tobinngo": "TOBINNGO_API_KEY",
    "service": "SERVICE_API_KEY",
}

# CI_USERNAME is the CI platform login of the user pushing app
# code to your Version Control platform. For example, in CircleCI this is
# CIRCLE_USERNAME.
CI_USERNAME = os.getenv("CIRCLE_USERNAME")


# USERNAME = DE_USERNAME_TO_CI_USERNAME[CI_USERNAME]
USERNAME = CI_USERNAME

# SERVICE_PRIVATE_SSH_KEY belongs to a Dash Enterprise user with admin
# privileges. This user will handle server deployment tasks.
SERVICE_PRIVATE_SSH_KEY = os.getenv("SERVICE_PRIVATE_SSH_KEY")

if USERNAME in DE_USERNAME_TO_CI_USERNAME and USERNAME in DE_USERNAME_TO_CI_API_KEY:
    USERNAME_API_KEY = os.getenv(DE_USERNAME_TO_CI_API_KEY.get(CI_USERNAME))
else:
    print("API key was not fetched")
    print(
        """
        {USERNAME} is missing from
        DE_USERNAME_TO_CI_USERNAME and
        DE_USERNAME_TO_CI_API_KEY dictionaries.

        See Getting Started section in Continuous Integration Docs
        (https://{DASH_ENTERPRISE_HOST}/Docs/continuous-integration)
        for more information or contact your Dash Enterprise
        administrator.

        """.format(
            USERNAME=USERNAME,
            DASH_ENTERPRISE_HOST=DASH_ENTERPRISE_HOST,
        )
    )
