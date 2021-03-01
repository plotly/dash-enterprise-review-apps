"""
This script is run after initialize.py, and is reposible for deploying Review
Apps on  your Dash Enterprise host
"""

import sys
import subprocess
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from settings import (
    SERVICE_PRIVATE_SSH_KEY,
    DASH_ENTERPRISE_HOST,
    APPNAME,
    TARGET_APPNAME,
    BRANCHNAME,
    TRUNK_BRANCHNAME,
    SERVICE_USERNAME,
    SERVICE_API_KEY,
)

if sys.version_info[0] < 3.6 and sys.version_info[0] > 3.7:
    raise Exception(
        "This script has only been tested on Python 3.6."
        + "You are using {version}.".format(version=sys.version_info[0])
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
    print(
        """
        You Dash app has been deployed.

        Preview {APPNAME}:

        https://{DASH_ENTERPRISE_HOST}/{APPNAME}/
        https://{DASH_ENTERPRISE_HOST}/Manager/apps/{APPNAME}/settings
        """.format(
            APPNAME=APPNAME,
            DASH_ENTERPRISE_HOST=DASH_ENTERPRISE_HOST,
        )
    )
    sys.exit()


def zip_list_index(index_list, index_a, index_b):
    """
    Accepts two indices, from a single list, with values equivalent to a list
    and zips them together, resulting in a dictionary.
    """
    index_key = [index_list[i][index_a] for i in range(len(index_list))]
    index_value = [index_list[i][index_b] for i in range(len(index_list))]
    return dict(zip(index_key, index_value))


def handle_error(query_result, detected_error=None):
    """
    Raise error if error is not an accepted error
    """
    if detected_error is not None:
        for accepted_error, error_message in accepted_errors.items():
            if accepted_error in query_result and "error" in result[accepted_error]:
                if query_result[accepted_error]["error"] in error_message:
                    pass
                else:
                    raise Exception(result[accepted_error]["error"])


apps_query_errors = [
    "[]",
]

accepted_errors = {
    "apps": apps_query_errors,
}


print("Deploying review app...\n")
if TRUNK_BRANCHNAME == BRANCHNAME:
    DEPLOY_APPNAME = TARGET_APPNAME
else:
    DEPLOY_APPNAME = APPNAME
subprocess.run(
    """
    echo "{SERVICE_PRIVATE_SSH_KEY}" | base64 --decode -i > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_rsa
    echo "Host {DASH_ENTERPRISE_HOST},\
        HostName {DASH_ENTERPRISE_HOST},\
        User {SERVICE_USERNAME},\
        Port 3022,\
        IdentityFile ~/.ssh/id_rsa,\
        StrictHostKeyChecking no,\
        UserKnownHostsFile /dev/null\
    | tr ',' '\n' > ~/.ssh/config
    git config remote.plotly.url >&- || git remote add plotly dokku@\
    {DASH_ENTERPRISE_HOST}:{DEPLOY_APPNAME}
    git push --force plotly HEAD:master
    """.format(
        SERVICE_PRIVATE_SSH_KEY=SERVICE_PRIVATE_SSH_KEY,
        DASH_ENTERPRISE_HOST=DASH_ENTERPRISE_HOST,
        SERVICE_USERNAME=SERVICE_USERNAME,
        DEPLOY_APPNAME=DEPLOY_APPNAME,
    ),
    shell=True,
    check=True,
)

print("\n")

if TRUNK_BRANCHNAME == BRANCHNAME:
    exit_message()
else:
    print("Querying target app...")
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
                }
            }
        }
        """
    )
    params = {"name": TARGET_APPNAME}
    result = client_service.execute(query, variable_values=params)
    handle_error(result, accepted_errors)

if len(result["apps"]["apps"]) != 0:
    apps_owner = result["apps"]["apps"][0]["owner"]["username"]
    apps_status = result["apps"]["apps"][0]["status"]["running"]
    apps_permissionLevels = result["apps"]["apps"][0]["metadata"]

    permissionLevels = apps_permissionLevels

    print(
        "Updating app permission level to {permissionLevel}...".format(
            permissionLevel=permissionLevels["permissionLevel"]
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
        "permissionLevel": permissionLevels["permissionLevel"],
        "appname": APPNAME,
    }
    result = client_service.execute(query, variable_values=params)
    handle_error(result, accepted_errors)

    if permissionLevels["permissionLevel"] == "restricted" and apps_status == "true":
        print("Adding {apps_owner} as app viewer...".format(apps_owner=apps_owner))
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
        params = {"appname": APPNAME, "users": apps_owner}
        result = client_service.execute(query, variable_values=params)
        handle_error(result, accepted_errors)

        print("  {apps_owner}".format(apps_owner=apps_owner))
    else:
        print("No app viewers were added")
else:
    exit_message()
