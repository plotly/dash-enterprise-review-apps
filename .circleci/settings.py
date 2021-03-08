"""
This script imports all of the required environment variables. If you are
running it locally, update  .env file with the environment variables added your ci playform and run source.

Usage: source .env && python3.6 initialize.py; python3.6 deploy.py; python3.6 delete.py
"""
import os
import subprocess

# LAST_UPDATE is the allowed amount of time since a review app was last viewed
# or updated, before it is deleted from the server
# Typically this is {"days": 5}
TIME_UNIT = "hours"  # "minutes", "hours", "days"
TIMESPAN = 1
LAST_UPDATE = {TIME_UNIT: TIMESPAN}

# MAIN_BRANCHNAME refers to the main app.source branch. When
# MAIN_BRANCHNAME is equivalent to REVIEW_BRANCHNAME, the script will deploy the
# changes to the main app. Otherwise, the script will create a new review app.
# This branch is usually called "main", "master" or "production".
MAIN_BRANCHNAME = "main"

# REVIEW_BRANCHNAME refers to the review app's source branch.
# This branch is used when creating the name of the review app
# Set this to the branch name provided by your CI system's environment
# variables. For example, in CircleCI this is CIRCLE_BRANCH, and in Bitbucket
# it is BITBUCKET_BRANCH.
REVIEW_BRANCHNAME = os.getenv("CIRCLE_BRANCH", LOCAL_BRANCHNAME)

# LOCAL_BRANCHNAME refers to your current branch and is used only when running
# the scripts locally.
LOCAL_BRANCHNAME = subprocess.getoutput("echo | git branch --show-current")

# MAIN_APPNAME is the name the Dash app that will serve as a review app
# template. This script will copy that app's configuration settings and
# apply them to all review apps. When REVIEW_BRANCHNAME is equivalent to
# MAIN_BRANCHNAME, the changes on the review branch will get deployed to this
# app.
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
    "YOUR_DEVELOPER_USERNAME": "YOUR_DEVELOPER_USERNAME",
    "tobinngo": "tobinngo",
    "service": "service",
}

# DE_USERNAME_TO_CI_API_KEY maps your Dash Enterprise developer
# usernames to the name of a CI environment variable in your CI platform that
# contains their Dash Enterprise API key.
DE_USERNAME_TO_CI_API_KEY = {
    "YOUR_DEVELOPER_USERNAME": "YOUR_DEVELOPER_API_KEY",
    "tobinngo": "TNGO_API_KEY",
    "service": "SERVICE_API_KEY",
}

# CI_USERNAME is the CI platform login of the user pushing app
# code to your Version Control platform. For example, in CircleCI this is
# CIRCLE_USERNAME.
CI_USERNAME = os.getenv("CIRCLE_USERNAME", "service")

# DE_USERNAME is the Dash Enterprise login of your developers
DE_USERNAME = DE_USERNAME_TO_CI_USERNAME[CI_USERNAME]
# DE_USERNAME = CI_USERNAME

# SERVICE_PRIVATE_SSH_KEY belongs to a Dash Enterprise user with admin
# privileges. This user will handle server deployment tasks.
SERVICE_PRIVATE_SSH_KEY = os.getenv("SERVICE_PRIVATE_SSH_KEY")

# SERVICE_SSH_CONFIG is a base64-encoded SSH configuration file.
SERVICE_SSH_CONFIG = os.getenv("SERVICE_SSH_CONFIG")

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

        See Getting Started section in Review Apps Docs
        (https://{DASH_ENTERPRISE_HOST}/Docs/review-apps)
        for more information or contact your Dash Enterprise
        administrator.

        """.format(
            DE_USERNAME=DE_USERNAME,
            DASH_ENTERPRISE_HOST=DASH_ENTERPRISE_HOST,
        )
    )
