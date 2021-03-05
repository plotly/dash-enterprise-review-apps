"""
This script is run after initialize.py, and is reponsible for deploying Review
Apps on your Dash Enterprise host
"""

import sys
import subprocess
from time import sleep
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from settings import (
    SERVICE_PRIVATE_SSH_KEY,
    DASH_ENTERPRISE_HOST,
    REVIEW_APPNAME,
    MAIN_APPNAME,
    REVIEW_BRANCHNAME,
    MAIN_BRANCHNAME,
    SERVICE_USERNAME,
    SERVICE_API_KEY,
)

if sys.version_info[0:2] < (3, 6) or sys.version_info[0:2] > (3, 7):
    raise Exception(
        "This script has only been tested on Python 3.6. "
        + "You are using {major}.{minor}.".format(
            major=sys.version_info[0], minor=sys.version_info[1]
        )
    )

transport_service = RequestsHTTPTransport(
    url=f"https://{DASH_ENTERPRISE_HOST}/Manager/graphql",
    auth=(SERVICE_USERNAME, SERVICE_API_KEY),
    use_json=True,
    retries=5,
)

client_service = Client(transport=transport_service)


def exit_message():
    """
    Prints out links to deployed app and app settings page before exiting
    script.
    """
    print("Your review app has been deployed...")
    print()
    print(
        "  Preview: https://{DASH_ENTERPRISE_HOST}/{REVIEW_APPNAME}/".format(
            REVIEW_APPNAME=REVIEW_APPNAME,
            DASH_ENTERPRISE_HOST=DASH_ENTERPRISE_HOST,
        )
    )
    print(
        "  Settings: https://"
        + "{DASH_ENTERPRISE_HOST}/Manager/apps/{REVIEW_APPNAME}/settings".format(
            REVIEW_APPNAME=REVIEW_APPNAME,
            DASH_ENTERPRISE_HOST=DASH_ENTERPRISE_HOST,
        )
    )
    sys.exit(0)


def zip_list_index(index_list, index_a, index_b):
    """
    Accepts two indices, from a single list, with values equivalent to a list
    and zips them together, resulting in a dictionary.
    """
    index_key = [index_list[i][index_a] for i in range(len(index_list))]
    index_value = [index_list[i][index_b] for i in range(len(index_list))]
    return dict(zip(index_key, index_value))


if MAIN_BRANCHNAME == REVIEW_BRANCHNAME:
    print()
    print("Deploying main app...")
    print()
    DEPLOY_APPNAME = MAIN_APPNAME
else:
    print()
    print("Deploying review app...")
    print()
    DEPLOY_APPNAME = REVIEW_APPNAME
subprocess.run(
    """
    echo '-----> Creating ssh key'
    echo "{SSH_KEY}" | base64 --decode -i > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    ssh-add -D
    eval "$(ssh-agent -s)"
    echo '-----> Adding keys to ssh-agent'
    ssh-add ~/.ssh/id_rsa
    echo '-----> Creating ssh config'
    echo "Host *,\
        Port 3022,\
        IdentityFile ~/.ssh/id_rsa,\
        StrictHostKeyChecking no,\
        UserKnownHostsFile /dev/null"\
    | tr ',' '\n' > ~/.ssh/config
    echo '-----> Adding git remote'
    git config remote.plotly.url >&- || git remote add plotly dokku@{HOST}:{APP}
    echo '-----> Deploying app'
    git push --force plotly HEAD:master
    """.format(
        SSH_KEY=SERVICE_PRIVATE_SSH_KEY,
        HOST=DASH_ENTERPRISE_HOST,
        APP=DEPLOY_APPNAME,
    ),
    shell=True,
    check=True,
)

print()

if MAIN_BRANCHNAME == REVIEW_BRANCHNAME:
    exit_message()
else:
    query = gql(
        """
        query (
            $name: String
        ) {
            apps(
                name: $name,
                allApps:true,
            ) {
                apps {
                    name
                    owner {
                        username
                    }
                    status {
                        running
                    }
                    metadata {
                        permissionLevel
                    }
                    collaborators {
                        users
                  }
                }
            }
        }
        """
    )
    params = {"name": MAIN_APPNAME}
    result = client_service.execute(query, variable_values=params)

if len(result["apps"]["apps"]) != 0:
    exit_message()

apps_owner = result["apps"]["apps"][0]["owner"]["username"]
apps_status = result["apps"]["apps"][0]["status"]["running"]
apps_permissionLevels = result["apps"]["apps"][0]["metadata"]["permissionLevel"]
apps_collaborators = result["apps"]["apps"][0]["collaborators"]["users"]

apps_viewers = [apps_owner] + apps_collaborators
print(
    "Updating review app permission level to {permissionLevel}...".format(
        permissionLevel=apps_permissionLevels
    )
)
query = gql(
    """
    mutation (
        $appname: String,
        $permissionLevel: PermissionLevels
    ) {
        updateApp(
            appname: $appname,
            metadata: {
                permissionLevel: $permissionLevel
            }
        ){
            error
        }
    }
    """
)
params = {
    "permissionLevel": apps_permissionLevels,
    "appname": REVIEW_APPNAME,
}
result = client_service.execute(query, variable_values=params)

if apps_permissionLevels == "restricted":
    print("Adding main app viewers to review app...")
    for viewer in range(apps_viewers):
        query = gql(
            """
        mutation (
            $appname: String,
            $users: [String],
        ){
            addCollaborators(
                appname: $appname,
                users: $users,
            ){
                error
            }
        }
        """
        )
        params = {"appname": REVIEW_APPNAME, "users": viewer}
        result = client_service.execute(query, variable_values=params)
        sleep(5)

        print("  {viewer}".format(viewer=viewer))
else:
    print("Main app is not restricted, not adding any additional viewers.")
