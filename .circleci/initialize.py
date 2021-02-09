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
    USERNAME,
    USERNAME_API_KEY,
)

if sys.version_info[0] < 3.6 and sys.version_info[0] > 3.7:
    raise Exception("Python 3.6 is required.")

if DEBUG == "true":
    logging.basicConfig(level=logging.DEBUG)

transport = RequestsHTTPTransport(
    url=f"https://{DASH_ENTERPRISE_HOST}/Manager/graphql",
    auth=(USERNAME, USERNAME_API_KEY),
    use_json=True,
    retries=0,
)

client = Client(transport=transport)

# import hashlib
# import json
# from flask import Flask
# from flask_caching import Cache
# app = Flask(__name__)
# # For more configuration options, check out the documentation
# cache = Cache(app, config={'CACHE_TYPE': 'filesystem', "CACHE_DIR": "cache"})

# @cache.memoize()
# def execute(*args, **kwargs):
#     result = client.execute(*args, **kwargs)
    
#     filename = str(args) + str(kwargs) + '.json'
#     filename = hashlib.sha256(filename.encode()).hexdigest()
#     with open(f'cache/{filename}', 'w') as f:
#         f.write(json.dumps(result, indent=4))

#     return result

def zipped(l, a, b):
    k = [l[i][a] for i in range(len(l))]
    v = [l[i][b] for i in range(len(l))]
    return dict(zip(k,v))

addApp_errors = [
    "Invalid app name. Names should be between 3 to 30 characters long, start with a letter, and only contain lower case letters, numbers, and -",
    "An app with the given name already exists. Please choose a different name.",
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

errors = {
    "addApp": addApp_errors,
    "deleteApp": deleteApp_errors,
    "addEnvironmentVariable": addEnvironmentVariable_errors,
    "addService": addService_errors,
    "mountDirectory": mountDirectory_errors,
}

# Querying target app settings
query = gql(
    """
    query ($name: String) {
        current {
            username
            isAdmin
        }
        apps(name: $name, allApps:true) {
            apps {
                name
                owner {
                    username
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
for k, v in errors.items():
    if k in result and "error" in result[k]:
        if result[k]["error"] in v:
            raise Exception(result)

apps = result["apps"]["apps"]
apps_name = result["apps"]["apps"][0]["name"]
apps_owner = result["apps"]["apps"][0]["owner"]["username"]
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
linkedServices = zipped(apps_linkedServices, "serviceType", "name")
mounts = zipped(apps_mounts, "hostDir", "targetDir")
environmentVariables = zipped(apps_environmentVariables, "name", "value")

query = gql(
    """
    mutation ($appname: String) {
        addApp(name: $appname) {
            app {
                name
            }
            error
        }
    }
    """
)
params = {"appname": APPNAME}
print(client.execute(query, variable_values=params))

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
                service {
                    name
                    serviceType
                    created
                }
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
    client.execute(query_addService, variable_values=params_addService)
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
            ){
                refresh
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
    client.execute(query_linkService, variable_values=params_linkService)
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
                ok
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

    client.execute(query, variable_values=params)
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
                app {
                    name
                    owner {
                        username
                    }
                    metadata{
                        permissionLevel
                    }
                }
            }
        }
        """
    )
    params = {"permissionLevel": v, "appname": APPNAME}
    client.execute(query, variable_values=params)
    print(
        f"Copying permissionlevel from {TARGET_APPNAME} to {APPNAME}"
    )
    print(f"    {k}: {v}")

    if v == "restricted" and current_isAdmin != "false":
        query = gql(
        """
        mutation (
            $appname: String,
            $users: [String]
        ) { 
            addCollaborators(
                appname: $appname, 
                users: $users
            ){
                error
            }
        }
        """
    )
        params = {"appname": APPNAME, "users": apps_owner}
        client.execute(query, variable_values=params)
        print(f"Adding  \"{apps_owner}\" as \"collaborator\"")


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
                    ok
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
        client.execute(query, variable_values=params)
        print(f"    {k} :", 5 * "*")

print(
    f"""
    Preview your Dash app:
    
    https://{DASH_ENTERPRISE_HOST}/{APPNAME}/
    https://{DASH_ENTERPRISE_HOST}/Manager/apps/{APPNAME}/settings
    """
)
