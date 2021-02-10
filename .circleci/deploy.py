import os
import subprocess
import base64
from config import (
    SERVICE_PRIVATE_SSH_KEY,
    SERVICE_PUBLIC_SSH_KEY,
    SSH_CONFIG,
    DASH_ENTERPRISE_HOST,
    APPNAME,
    TARGET_APPNAME,
    BRANCHNAME,
    TRUNK_BRANCHNAME,
    REPONAME,
)
print("Deploying Dash app...", end=" ")
if os.getenv("CIRCLECI") == "true":
    print("OK")
    if TRUNK_BRANCHNAME == BRANCHNAME:
        deploy_appname = TARGET_APPNAME
    else: 
        deploy_appname = APPNAME
    subprocess.run(
        f"""
        echo "{SERVICE_PRIVATE_SSH_KEY}" | base64 --decode -i > ~/.ssh/id_rsa
        chmod 600 ~/.ssh/id_rsa
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/id_rsa
        echo {SSH_CONFIG} | tr ',' '\n' > ~/.ssh/config
        git config remote.plotly.url >&- || git remote add plotly dokku@{DASH_ENTERPRISE_HOST}:{deploy_appname}
        git push --force plotly HEAD:master
        """, shell=True
    )
    print(
        f"""
        You Dash app has been deployed. 
        
        Preview {APPNAME}:
        
        https://{DASH_ENTERPRISE_HOST}/{APPNAME}/
        https://{DASH_ENTERPRISE_HOST}/Manager/apps/{APPNAME}/settings
        https://app.circleci.com/pipelines/github/plotly/{REPONAME}?branch={BRANCHNAME}
        """
    )
else:
    print("FAILED")
    raise Exception(
        f"""
        
        Deployment not authorized from this environment.
        Must push from main/master branch in
        CIRCLECI.

        See Getting Started section in Continuous Integration Docs
        (https://{DASH_ENTERPRISE_HOST}/Docs/continuous-integration)
        for more information or contact your Dash Enterprise
        administrator.    
        """
    )
