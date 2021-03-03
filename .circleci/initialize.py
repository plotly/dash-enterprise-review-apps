"""
This script is used initialize Review Apps that inherit the properties and
settings of their a target app.
"""

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

transport_user = RequestsHTTPTransport(
    url=f"https://{DASH_ENTERPRISE_HOST}/Manager/graphql",
    auth=(USERNAME, USERNAME_API_KEY),
    use_json=True,
    retries=5,
)

client_service = Client(transport=transport_service)
client_user = Client(transport=transport_user)


def zip_list_index(index_list, index_a, index_b):
    """
    Accepts two indices, from a single list, with values equivalent to a list
    and zips them together, resulting in a dictionary.
    """
    index_key = [index_list[i][index_a] for i in range(len(index_list))]
    index_value = [index_list[i][index_b] for i in range(len(index_list))]
    return dict(zip(index_key, index_value))


print("Querying target app...")
print("  {TARGET_APPNAME}".format(TARGET_APPNAME=TARGET_APPNAME))

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

if len(result["apps"]["apps"]) != 0:
    print("Initializing review app...")
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

    result = client_user.execute(query, variable_values=params)
    print("  {APPNAME}".format(APPNAME=APPNAME))
else:
    print(result)
    raise Exception(
        "\nReview app not initialized"
        + "\nApp {TARGET_APPNAME} does not exist or the user {USERNAME}".format(
            TARGET_APPNAME=TARGET_APPNAME, USERNAME=USERNAME
        )
        + "does not have permission to query this app.\n"
    )

if len(linkedServices.items()) != 0:
    print(
        "Adding redis/postgres databases...",
    )
    for serviceType in linkedServices:
        if serviceType == "redis":
            serviceName = "{APPNAME}-{serviceType}".format(
                APPNAME=APPNAME,
                serviceType="redis",
            )[0:30]
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
                "serviceType": serviceType,
            }
            sleep(5)
            result = client_service.execute(
                query_addService, variable_values=params_addService
            )

            print(
                "  {serviceName}, {serviceType}".format(
                    serviceName=serviceName, serviceType=serviceType
                )
            )
        elif serviceType == "postgres":
            serviceName = "{APPNAME}-{serviceType}".format(
                APPNAME=APPNAME,
                serviceType="postgres",
            )[0:30]
            query_addService = gql(
                """
                mutation (
                    $serviceType: ServiceType=postgres,
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
                "serviceType": serviceType,
            }
            sleep(5)
            result = client_service.execute(
                query_addService, variable_values=params_addService
            )

            print(
                "  {serviceName}, {serviceType}".format(
                    serviceName=serviceName, serviceType=serviceType
                )
            )
else:
    print("No redis/postgres databases to add")


print(
    "Linking databases...",
)
for serviceType in linkedServices:
    if serviceType == "redis":
        serviceName = "{APPNAME}-{serviceType}".format(
            APPNAME=APPNAME,
            serviceType="redis",
        )[0:30]
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
            "serviceType": serviceType,
        }

        sleep(5)
        result = client_service.execute(
            query_linkService, variable_values=params_linkService
        )

        print(
            "  {serviceName}, {serviceType}".format(
                serviceName=serviceName, serviceType=serviceType
            )
        )

    elif serviceType == "postgres":
        serviceName = "{APPNAME}-{serviceType}".format(
            APPNAME=APPNAME,
            serviceType="postgres",
        )[0:30]
        query_linkService = gql(
            """
            mutation (
                $appname: String
                $serviceType: ServiceType=postgres,
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
            "serviceType": serviceType,
        }

        sleep(5)
        result = client_service.execute(
            query_linkService, variable_values=params_linkService
        )

        print(
            "  {serviceName}, {serviceType}".format(
                serviceName=serviceName, serviceType=serviceType
            )
        )

if len(mounts.items()) != 0:
    print("Mapping directories...")
    for host_dir, target_dir in mounts.items():
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
            "hostDir": host_dir,
            "targetDir": target_dir,
            "appname": APPNAME,
        }

        result = client_service.execute(query, variable_values=params)

        print(
            "  Mapping host directory: {host_dir} to review app directory: {target_dir}".format(
                host_dir=host_dir, target_dir=target_dir
            )
        )
else:
    print("No directories to map")

if len(environmentVariables.items()) != 0:
    print("Adding environment variables...")
    environmentVariables_filter = tuple(
        # These environment variables are created automatically by Dash
        # Enterprise and do not need to be manually modified.
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
    for envar_name, envar_value in environmentVariables.items():
        if not envar_name.startswith(environmentVariables_filter):
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
                "environmentVariable": envar_name,
                "value": envar_value,
                "appname": APPNAME,
            }
            result = client_service.execute(query, variable_values=params)

            print("  {envar_name} :".format(envar_name=envar_name), 10 * "*")
else:
    print("No environment variables to add\n")
