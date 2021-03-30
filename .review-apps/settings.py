# This script imports environment variables for Review Apps.

# Required:
# MAIN_APPNAME
# DASH_ENTERPRISE_HOST
# SERVICE_USERNAME
# SERVICE_API_KEY
# SERVICE_PRIVATE_SSH_KEY (base64)
# SERVICE_SSH_CONFIG (base64)
# DE_USERNAME
# DE_USERNAME_API_KEY

# Optional:
# TIME_UNIT
# TIMESPAN
# MAIN_BRANCHNAME
# REVIEW_BRANCHNAME

# When running Review Apps locally you may run bootstrap.sh
# to generate a .env file. Set required variable values.

# Usage: source .env && python3.6 initialize.py; python3.6 deploy.py; python3.6
# delete.py

import os
import subprocess

# LAST_UPDATE is the allowed amount of time since a Review App was last viewed
# or updated, before it is deleted from the server
# Typically this is {"days": 5}
TIME_UNIT = os.getenv("TIME_UNIT", "days")  # "minutes", "hours", "days"
TIMESPAN = os.getenv("TIMESPAN", "5")
LAST_UPDATE = {TIME_UNIT: int(TIMESPAN)}

# _MAIN_BRANCHNAME refers to Main App's source source
# branch.
_MAIN_BRANCHNAME = subprocess.getoutput(
    "git remote show origin | grep 'HEAD branch' | cut -d' ' -f5"
)
# MAIN_BRANCHNAME refers to the Main App's source branch. When
# MAIN_BRANCHNAME is equivalent to REVIEW_BRANCHNAME, the script will deploy the
# changes to the Main App. Otherwise, the script will create a new Review App.
# This branch is usually called "main", "master" or "production".
MAIN_BRANCHNAME = os.getenv("MAIN_BRANCHNAME", _MAIN_BRANCHNAME)

# LOCAL_BRANCHNAME refers to your current branch.
_LOCAL_BRANCHNAME = subprocess.getoutput("git branch --show-current")

# REVIEW_BRANCHNAME refers to the source branch of your Review App.
# This branch is used when creating the name of your Review App
# You may set this to the branch name provided by your CI system's environment
# variables. For example, in CircleCI this is CIRCLE_BRANCH, and in Bitbucket
# it is BITBUCKET_BRANCH.
REVIEW_BRANCHNAME = os.getenv("REVIEW_BRANCHNAME", _LOCAL_BRANCHNAME)

# REVIEW_BRANCHNAME is sanitized when it is appended to MAIN_APPNAME to compose your REVIEW_APPNAME.
SANITIZE_BRANCHNAME = subprocess.getoutput(
    """
    echo "{REVIEW_BRANCHNAME}" \
    | iconv -t ascii//TRANSLIT | \
    sed -r s/[^a-zA-Z0-9\.]+/"-underscore-"/g | \
    sed -r s/^-+\|-+$//g | tr A-Z a-z
    """.format(REVIEW_BRANCHNAME=REVIEW_BRANCHNAME)
)

# MAIN_APPNAME is the name the deployed Dash app that will serve as a Review App
# template. This script will copy that app's configuration settings and
# apply them to all review apps. When REVIEW_BRANCHNAME is equivalent to
# MAIN_BRANCHNAME, the changes on the review branch will get deployed to this
# app.
MAIN_APPNAME = os.getenv("MAIN_APPNAME", "your-main-appname")

# PREFIX is the prefix of the Review App name.
# It is used for initializing Review Apps, and determining which apps to delete.
PREFIX = "{MAIN_APPNAME}-".format(MAIN_APPNAME=MAIN_APPNAME[:15])

# REVIEW_APPNAME is the name of the Review App.
REVIEW_APPNAME = "{PREFIX}{SANITIZE_BRANCHNAME}".format(
    PREFIX=PREFIX, SANITIZE_BRANCHNAME=SANITIZE_BRANCHNAME
)[:30]


# DEPLOY_APPNAME is the name of the deployed app.
DEPLOY_APPNAME = (
    MAIN_APPNAME if MAIN_BRANCHNAME == REVIEW_BRANCHNAME else REVIEW_APPNAME
)

# Set DEPLOY_APPNAME as environment variable for use with GitHub API. $BASH_ENV
# points to a temporary file that persists between CircleCI job steps, and must # be sourced at every run step to set stored variables.
subprocess.run(
    """
    echo 'export DEPLOY_APPNAME={DEPLOY_APPNAME}' >> $BASH_ENV 
    """.format(
        DEPLOY_APPNAME=DEPLOY_APPNAME
    ),
    shell=True,
    check=True,
)

# DASH_ENTERPRISE_HOST is your Dash Enterprise Server's host address.
DASH_ENTERPRISE_HOST = os.getenv("DASH_ENTERPRISE_HOST", "your-dash-enterprise-host")

# SERVICE_USERNAME can be the username of any account that has admin privileges.
# That account will be used as a "Service Account" for app
# deployment and configuration.
SERVICE_USERNAME = os.getenv("SERVICE_USERNAME", "your-service-username")

# SERVICE_API_KEY is the API key used to access your Dash
# Enterprise server.
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "your-service-api-key")

# SERVICE_PRIVATE_SSH_KEY is a base64-encoded key belonging to a Dash
# Enterprise user with admin privileges. This user will handle server
# deployment tasks.
SERVICE_PRIVATE_SSH_KEY = os.getenv(
    "SERVICE_PRIVATE_SSH_KEY", "your-service-private-ssh-key",
)

# SERVICE_SSH_CONFIG is a base64-encoded SSH configuration file.
SERVICE_SSH_CONFIG = os.getenv("SERVICE_SSH_CONFIG", "your-service-ssh-config")

# DE_USERNAME is your Dash Enterprise login
DE_USERNAME = os.getenv("DE_USERNAME", "your-de-username")

# DE_USERNAME_API_KEY is API key associated with your DE_USERNAME.
DE_USERNAME_API_KEY = os.getenv("DEV_API_KEY", "your-de-username-api-key")
