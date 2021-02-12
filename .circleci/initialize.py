import logging
import os
import sys
from time import sleep
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from settings import (
    DASH_ENTERPRISE_HOST,
    USERNAME,
    USERNAME_API_KEY,
    SERVICE_API_KEY,
    SERVICE_USERNAME,
    APPNAME,
    TARGET_APPNAME,
    DEBUG,
)

if sys.version_info[0] < 3.6 and sys.version_info[0] > 3.7:
    raise Exception("Python 3.6 is required.")

if DEBUG == "true":
    logging.basicConfig(level=logging.DEBUG)

transport_service = RequestsHTTPTransport(
    url=f"https://{DASH_ENTERPRISE_HOST}/Manager/graphql",
    auth=(SERVICE_USERNAME, SERVICE_API_KEY),
    use_json=True,
)

transport_user = RequestsHTTPTransport(
    url=f"https://{DASH_ENTERPRISE_HOST}/Manager/graphql",
    auth=(USERNAME, USERNAME_API_KEY),
    use_json=True,
)

client_service = Client(transport=transport_service)
client_user = Client(transport=transport_user)

def zip_list_index(l, a, b):
    k = [l[i][a] for i in range(len(l))]
    v = [l[i][b] for i in range(len(l))]
    return dict(zip(k,v))

def handle_error(result, er=None):
    """
    Raise error if error is not an accepted error
    """
    if er != None:
        for k, v in accepted_errors.items():
            if k in result and "error" in result[k]:
                if result[k]["error"] in v:
                    pass
                else:
                    raise Exception(result[k]["error"])

addService_errors = [
    "A service with the given name already exists. Please choose a different name.",
    None,
]

apps_query_errors = [
    "[]",
]
updateApp_errors = [
    "None is not a valid PermissionLevels",
    None,
]
addApp_errors = [
    "An app with this name already exists in this Dash Server. Please choose a different name.",
    None,
]

accepted_errors = {
    "addApp": addApp_errors,
    "updateApp": updateApp_errors,
    "addService": addService_errors,
    "apps": apps_query_errors,
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
result = client_service.execute(query, variable_values=params)
handle_error(result, accepted_errors)

if len(result["apps"]["apps"]) == 0:
    print(result["apps"]["apps"])
    print(
    f"    App {TARGET_APPNAME} does not exist."
    )
    raise Exception(result)

apps = result["apps"]["apps"]
apps_name = result["apps"]["apps"][0]["name"]
apps_owner = result["apps"]["apps"][0]["owner"]["username"]
apps_status = result["apps"]["apps"][0]["status"]["running"]
current_isAdmin = result["current"]["isAdmin"]
apps_collaborators = result["apps"]["apps"][0]["collaborators"]
apps_permissionLevels = result["apps"]["apps"][0]["metadata"]
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

result = client_user.execute(
    query, 
    variable_values=params
)

handle_error(result, accepted_errors)

for k in linkedServices:
    serviceName = f"{APPNAME}-{k}"[0:30]
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
        "serviceName": serviceName, 
        "serviceType": k, 
    }

    print("add service...", end=" ")

    sleep(5)
    result = client_service.execute(
        query_addService, 
        variable_values=params_addService
    )
    handle_error(result, accepted_errors)

    print("OK")
    print(f"Adding service: {serviceName}, {k}")

for k in linkedServices:
    serviceName = f"{APPNAME}-{k}"[0:30]
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
        "serviceName": serviceName, 
        "serviceType": k
    }

    print("link service...")

    sleep(5)
    result = client_service.execute(
        query_linkService, 
        variable_values=params_linkService
    )
    handle_error(result, accepted_errors)

    print(f"Linking service: {serviceName}, {k}")
    

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

    result = client_service.execute(query, variable_values=params)
    handle_error(result, accepted_errors)

    print(f"Mapped hostDir: {k} to targetDir: {v}")

# for k, v in permissionLevels.items():
#     query = gql(
#         """
#         mutation (
#             $appname: String,
#             $permissionLevel: PermissionLevels
#         ) { 
#             updateApp(
#                 appname: $appname, 
#                 metadata: {
#                     permissionLevel: $permissionLevel
#                 }
#             ){
#                 error
#             }
#         }
#         """
#     )
#     params = {"permissionLevel": v, "appname": APPNAME}
#     result_permissionLevel = client_service.execute(query, variable_values=params)
#     handle_error(result_permissionLevel, accepted_errors)

#     print(f"Copying permissionlevel from {TARGET_APPNAME} to {APPNAME}")
#     print(f"    {k}: {v}")

#     if (
#         v == "restricted" and 
#         current_isAdmin == "false" and 
#         apps_status == "true"
#     ):
#         query = gql(
#         """
#         mutation (
#             $appname: String,
#             $users: [String],
#         ) { 
#             addCollaborators(
#                 appname: $appname, 
#                 users: $users,
#             ){
#                 error
#             }
#         }
#         """
#     )
#         params = {"appname": APPNAME, "users": apps_owner}
#         result = client_service.execute(query, variable_values=params)
#         handle_error(result, accepted_errors)
      
#         print(f"Adding  \"{apps_owner}\" as \"collaborator\"")

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
        result = client_service.execute(query, variable_values=params)
        handle_error(result, accepted_errors)

        print(f"    {k} :", 5 * "*")

print(f"\n{APPNAME} has been initialized\n")
