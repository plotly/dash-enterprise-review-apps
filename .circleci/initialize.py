import logging
import os
import sys
from time import sleep
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from config import (
    APPNAME,
    TARGET_APPNAME,
    DEBUG,
    DASH_ENTERPRISE_HOST,
    SERVICE_USERNAME,
    SERVICE_API_KEY,
    USERNAME,
    USERNAME_API_KEY,
)

if sys.version_info[0] < 3.6 and sys.version_info[0] > 3.7:
    raise Exception("Python 3.6 is required.")

if DEBUG == "false":
    logging.basicConfig(level=logging.DEBUG)

transport = RequestsHTTPTransport(
    url=f"https://{DASH_ENTERPRISE_HOST}/Manager/graphql",
    auth=(SERVICE_USERNAME, SERVICE_API_KEY),
    use_json=True,
    retries=3,
    method="POST",
)

client = Client(transport=transport)

def zip_list_index(l, a, b):
    k = [l[i][a] for i in range(len(l))]
    v = [l[i][b] for i in range(len(l))]
    return dict(zip(k,v))

def handle_error(result, d):
    for k, v in d.items():
        if k in result and "error" in result[k]:
            if result[k]["error"] in v:
                print(result[k]["error"])
                raise Exception(result)
            elif result[k]["error"] not in v:
                print(result[k]["error"])
                print("Skipping app initialization")
                print("Redeploying app instead")
                False



addApp_errors = [
    "Invalid app name. Names should be between 3 to 30 characters long, start with a letter, and only contain lower case letters, numbers, and -",
]

deleteApp_errors = [
    "App does not exist.",
    "Invalid app name. Names should be between 3 to 30 characters long, start with a letter, and only contain lower case letters, numbers, and -",
]

addEnvironmentVariable_errors = [
    "App does not exist.",
    "Invalid app name. Names should be between 3 to 30 characters long, start with a letter, and only contain lower case letters, numbers, and -",
]

addService_errors = [
    "A service with the given name already exists. Please choose a different name.",
    "Invalid service name. Names should be between 3 to 30 characters long, start with a letter, and only contain lower case letters, numbers, and -",
]

mountDirectory_errors = [
    "App does not exist.",
    "Only directories specified in the Allowed Directories for Mapping list of the Dash Enterprise configuration can be mapped to Dash apps. Please ask your administrator to add None to the list as shown in the documentation (https://dash.plot.ly/dash-enterprise/map-local-directories) and then try again.",
]

apps_query_errors = [
    "[]",
]
addApp_exceptions = [
    "An app with this name already exists in this Dash Server. Please choose a different name."
]

errors = {
    "addApp": addApp_errors,
    "deleteApp": deleteApp_errors,
    "addEnvironmentVariable": addEnvironmentVariable_errors,
    "addService": addService_errors,
    "mountDirectory": mountDirectory_errors,
    "apps": apps_query_errors,
}

exceptions = {
    "addApp": addApp_exceptions,
}

# Querying target app settings
query = gql(
    """
    query (
        $name: String
    ) {
        current {
            username
            isAdmin
        }
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
                collaborators {
                    users
                    teams
                }
                metadata {
                permissionLevel
                }
                linkedServices {
                    name
                    serviceType
                }
                mounts {
                    targetDir
                    hostDir
                }
                environmentVariables {
                    name
                    value
                }
            }
        }
    }
    """
)
params = {"name": TARGET_APPNAME}
result = client.execute(query, variable_values=params)
handle_error(result, errors)

if len(result["apps"]["apps"]) == 0:
    print(result["apps"]["apps"])
    print(
    "    App does not exist or you may not have been granted access."
    )
    raise Exception(result)


apps = result["apps"]["apps"]
apps_name = result["apps"]["apps"][0]["name"]
apps_owner = result["apps"]["apps"][0]["owner"]["username"]
apps_status = result["apps"]["apps"][0]["status"]["running"]
current_isAdmin = result["current"]["isAdmin"]
apps_collaborators = result["apps"]["apps"][0]["collaborators"]
apps_permissionLevels= result["apps"]["apps"][0]["metadata"]
apps_linkedServices = result["apps"]["apps"][0]["linkedServices"]
apps_mounts = result["apps"]["apps"][0]["mounts"]
apps_environmentVariables = result["apps"]["apps"][0]["environmentVariables"]

a = [apps[i]["name"] for i in range(len(apps))]
b = [apps[i]["owner"]["username"] for i in range(len(apps))]

owner = dict(zip(a, b))
permissionLevels = apps_permissionLevels
linkedServices = zip_list_index(apps_linkedServices, "serviceType", "name")
mounts = zip_list_index(apps_mounts, "hostDir", "targetDir")
environmentVariables = zip_list_index(apps_environmentVariables, "name", "value")

query = gql(
    """
    mutation (
        $appname: String
    ) {
        addApp(
            name: $appname
        ) {
            error
        }
    }
    """
)
params = {"appname": APPNAME}
result = client.execute(query, variable_values=params)
if handle_error(result, errors) == False:
    for k in linkedServices:
        query_addService = gql(
            """
            mutation (
                $serviceType: ServiceType=redis,
                $serviceName: String
            ) {
                addService (
                    name: $serviceName,
                    serviceType: $serviceType
                ) {
                    error
                }
            }  
            """
        )
        params_addService = {
            "serviceName": f"{APPNAME}-{k}", 
            "serviceType": k, 
        }

        print("add service...", end=" ")

        sleep(5)
        result = client.execute(
            query_addService, 
            variable_values=params_addService
        )
        handle_error(result, errors)

        print("OK")
        print(f"Adding service: {APPNAME}-{k}, {k}")

    for k in linkedServices:
        query_linkService = gql(
            """
            mutation (
                $appname: String
                $serviceType: ServiceType=redis,
                $serviceName: String
            ) {
                linkService (
                    appname: $appname,
                    serviceName: $serviceName, 
                    serviceType: $serviceType
                ) {
                    error
                }
            }
            """
        )
        params_linkService = {
            "appname": APPNAME,
            "serviceName": f"{APPNAME}-{k}", 
            "serviceType": k
        }

        print("link service...", end=" ")

        sleep(5)
        result = client.execute(
            query_linkService, 
            variable_values=params_linkService
        )
        handle_error(result, errors)

        print("OK")
        print(f"Linking service: {APPNAME}-{k}, {k}")
        

    for k, v in mounts.items():
        query = gql(
            """
            mutation (
                $hostDir: String, 
                $targetDir: String,
                $appname: String
            ) {
                mountDirectory(
                    hostDir: $hostDir,
                    targetDir: $targetDir, 
                    appname: $appname
                ) {
                    error
                }
            }
            """
        )
        params = {
            "hostDir": k,
            "targetDir": v,
            "appname": APPNAME,
        }

        result = client.execute(query, variable_values=params)
        handle_error(result, errors)

        print(f"Mapping hostDir: {k} to targetDir: {v}")


    for k, v in permissionLevels.items():
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
        params = {"permissionLevel": v, "appname": APPNAME}
        result = client.execute(query, variable_values=params)
        handle_error(result, errors)

        print(f"Copying permissionlevel from {TARGET_APPNAME} to {APPNAME}")
        print(f"    {k}: {v}")

        if (
            v == "restricted" and 
            current_isAdmin == "false" and 
            apps_status == "true"
        ):
            query = gql(
            """
            mutation (
                $appname: String,
                $users: [String],
            ) { 
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
            result = client.execute(query, variable_values=params)
            handle_error(result, errors)
        
            print(f"Adding  \"{apps_owner}\" as \"collaborator\"")

        print(
            f"""
            cannot add {apps_owner} as collaborator. {apps_owner} already has
            admin privileges, or app has not been deployed yet.
            """
        )

    for k, v in environmentVariables.items():
        environmentVariables_filter = tuple(
            [
                "DOKKU",
                "DASH",
                "DATABASE_URL",
                "GIT_REV",
                "REDIS_URL",
                "SCRIPT_NAME",
                "NO_VHOST",
            ]
        )
        if k.startswith(environmentVariables_filter) != True:
            query = gql(
                """
                mutation (
                    $environmentVariable: String, 
                    $value: String, 
                    $appname: String
                ) {
                    addEnvironmentVariable (
                        name: $environmentVariable,
                        value: $value,
                        appname: $appname
                    ) {
                        error
                    }
                }
                """
            )
            params = {
                "environmentVariable": k, 
                "value": v, 
                "appname": APPNAME
            }
            result = client.execute(query, variable_values=params)
            handle_error(result, errors)

            print(f"    {k} :", 5 * "*")

if SERVICE_USERNAME != USERNAME:
    query = gql(
        """
        mutation moveAppsAndServices(
            $sourceUsername: String, 
            $targetUsername: String,
        ){
            moveAppsAndServices(
                sourceUsername: $sourceUsername, 
                targetUsername: $targetUsername,
            ){
                error
            }
        }
        """
    )
    params = {
        "sourceUsername": SERVICE_USERNAME, 
        "targetUsername": APPNAME,
    }
    result = client.execute(query, variable_values=params)
    handle_error(result, errors)

print(
    f"""

    You Dash app has been deployed. 

    Preview {APPNAME}:

    https://{DASH_ENTERPRISE_HOST}/{APPNAME}/
    https://{DASH_ENTERPRISE_HOST}/Manager/apps/{APPNAME}/settings
    """
)

