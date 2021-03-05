"""
This script imports all of the required environment variables. If you are
running it locally, update the .env file with the environment variables only
available on your ci playform and run source.

Usage: source .env && python3.6 initialize.py
"""
import os

# LAST_UPDATE is the allowed amount of time since a review app was last viewed
# or updated, before it is deleted from the server.
# Typically this is {"days": 5}
PERIOD = "hours"  # "minutes", "hours", "days"
TIME = 1
LAST_UPDATE = {PERIOD: TIME}

# Set this to the branch that you'd like to have update your main app.
# When REVIEW_BRANCHNAME is MAIN_BRANCHNAME, the script will deploy the changes
# to the target app. Otherwise, the script will create a new review app. This
# branch is usually called "main", "master" or "dev".
MAIN_BRANCHNAME = "main"

# REVIEW_BRANCHNAME should refer to the branch of the code that the review apps
# are created from. It is used when creating the name of the review app
# Set this to the branch name provided by your CI system's environment
# variables. For example, in CircleCI this is CIRCLE_BRANCH
REVIEW_BRANCHNAME = os.getenv("CIRCLE_BRANCH")

# MAIN_APPNAME is the name the Dash App that will serve as a review app
# template. This script will copy that app's configuration settings and
# apply them to all review apps.
# When REVIEW_BRANCHNAME = MAIN_BRANCHNAME, the changes on the branch will get
# deployed to this app.
MAIN_APPNAME = "aa-tobin"

# PREFIX is the prefix of the review app name.
# It is used for creating review apps and determining which apps to delete.
PREFIX = "{MAIN_APPNAME}-rev-".format(MAIN_APPNAME=MAIN_APPNAME[:15])

# REVIEW_APPNAME is the name of the review app.
REVIEW_APPNAME = "{PREFIX}{REVIEW_BRANCHNAME}".format(
    PREFIX=PREFIX, REVIEW_BRANCHNAME=REVIEW_BRANCHNAME
)[:30]

# DASH_ENTERPRISE_HOST is your Dash Enterprise Server's host address.
DASH_ENTERPRISE_HOST = "dash-playground.plotly.host"

# SERVICE_USERNAME can be the username of any account that has admin privileges.
# That account will be used as a "Service Account" for app
# deployment and configuration.
SERVICE_USERNAME = "service"

# SERVICE_API_KEY is the "Service Account's" API key used to access your Dash
# Enterprise server.
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")

# DE_USERNAME_TO_CI_USERNAME maps your developer
# usernames to the CI platform username used to push changes to
# your review app repository. If you use the same SSO for both Dash Enterprise
# and your CI platform, then this mapping will be 1-1: the same SSO username
# will be the key and the value. In this case, you could delete this
# dictionary and assign USERNAME to CI_USERNAME: USERNAME = CI_USERNAME
DE_USERNAME_TO_CI_USERNAME = {
    "chriddyp": "chriddyp",
    "tobinngo": "tobinngo",
    "service": "service",
}

# DE_USERNAME_TO_CI_API_KEY maps your Dash Enterprise developer
# usernames to the name of a CI environment variable in your CI platform that
# contains their Dash Enterprise API key.
DE_USERNAME_TO_CI_API_KEY = {
    "chriddyp": "CHRIDDYP_API_KEY",
    "tobinngo": "TNGO_API_KEY",
    "service": "SERVICE_API_KEY",
}

# CI_USERNAME is the CI platform login of the user pushing app
# code to your Version Control platform. For example, in CircleCI this is
# CIRCLE_USERNAME.
CI_USERNAME = os.getenv("CIRCLE_USERNAME")

# DE_USERNAME is the Dash Enterprise login of your developers
DE_USERNAME = DE_USERNAME_TO_CI_USERNAME[CI_USERNAME]
# DE_USERNAME = CI_USERNAME

# SERVICE_PRIVATE_SSH_KEY belongs to a Dash Enterprise user with admin
# privileges. This user will handle server deployment tasks.
SERVICE_PRIVATE_SSH_KEY = os.getenv("SERVICE_PRIVATE_SSH_KEY")

if (
    DE_USERNAME in DE_USERNAME_TO_CI_USERNAME
    and DE_USERNAME in DE_USERNAME_TO_CI_API_KEY
):
    DE_USERNAME_API_KEY = os.getenv(DE_USERNAME_TO_CI_API_KEY.get(DE_USERNAME))
else:
    print("API key was not fetched")
    print(
        """
        {DE_USERNAME} is missing from
        DE_USERNAME_TO_CI_USERNAME and
        DE_USERNAME_TO_CI_API_KEY dictionaries.

        See Getting Started section in Continuous Integration Docs
        (https://{DASH_ENTERPRISE_HOST}/Docs/review-apps)
        for more information or contact your Dash Enterprise
        administrator.

        """.format(
            DE_USERNAME=DE_USERNAME,
            DASH_ENTERPRISE_HOST=DASH_ENTERPRISE_HOST,
        )
    )
