import logging
import os

DEBUG = os.getenv("DEBUG", "false")

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
    USERNAME = "admin"
    BRANCHNAME = os.getenv("CIRCLE_BRANCH")
    TRUNK_BRANCHNAME = "main"
    TARGET_APPNAME = "target-app"
    APPNAME = f"{TARGET_APPNAME}-rev-{BRANCHNAME}"[0:30]
    DASH_ENTERPRISE_HOST = "qa-de-410.plotly.host" 
    SSH_CONFIG = f"Host {DASH_ENTERPRISE_HOST},    HostName {DASH_ENTERPRISE_HOST},    User {USERNAME},    Port 3022,    IdentityFile ~/.ssh/id_rsa,    StrictHostKeyChecking no,    UserKnownHostsFile /dev/null"
    SERVICE_PRIVATE_SSH_KEY = (
        "SERVICE_PRIVATE_SSH_KEY" if os.getenv("ADMIN_PRIVATE_SSH_KEY") !=None
        else None
    )
    SERVICE_PUBLIC_SSH_KEY = (
        "SERVICE_PUBLIC_SSH_KEY" if os.getenv("ADMIN_PUBLIC_SSH_KEY") != None
        else None
    )
    print("Fetching API keys...", end=" ")
    if USERNAME in USERS and os.getenv(USERS.get(USERNAME)) != None:
        print("OK")
        USERNAME_API_KEY = os.getenv(USERS.get(USERNAME))
    else:
        print("FAILED")
        print(
            f"""

            Username is missing from \"config.py\" user dictionary.

            See Getting Started section in Continuous Integration Docs
            (https://{DASH_ENTERPRISE_HOST}/Docs/continuous-integration)
            for more information or contact your Dash Enterprise
            administrator.
            """
        )
        raise ValueError



