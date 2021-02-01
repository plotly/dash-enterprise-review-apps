from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import subprocess, os, sys
import random
import string

if sys.version_info[0] < 3.6 and sys.version_info[0] > 3.7:
    raise Exception("Python 3.6 is required.")

if os.getenv("CIRCLECI") == "true":
    print("CIRCLECI")


    from sys import argv

    script, target_app_name = argv

    branch_name = os.getenv("CIRCLE_BRANCH")
    dash_app_name = f"review-app-{branch_name}".replace("_", "-")
    dash_enterprise_host = os.getenv("DASH_ENTERPRISE_HOST")
    username = os.getenv("USERNAME", "admin")
    username_api_key = os.getenv("USERNAME_API_KEY")
    ssh_config = os.getenv("SSH_CONFIG")
    ssh_private_key = os.getenv("SSH_PRIVATE_KEY")
    target_app_name = str(target_app_name)

else:
    print("LOCAL")

    dash_enterprise_host = "dash-playground.plotly.host"
    username = "developers"
    username_api_key = "faBhA8WwjuLpC8QoEulU"
    dash_app_name = "review-app-" + "".join(
        random.choices(string.ascii_lowercase + string.digits, k=6)
    )
    target_app_name = "aa-chris"

transport = RequestsHTTPTransport(
    url="https://{dash_enterprise_host}/Manager/graphql".format(
        dash_enterprise_host=dash_enterprise_host
    ),
    auth=(username, username_api_key),
    use_json=True,
    retries=3,
)

client = Client(transport=transport)

addApp_errors = [
    "An app with this name already exists in this Dash Server. Please choose a different name.",
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

queries = {
    "addApp": addApp_errors,
    "deleteApp": deleteApp_errors,
    "addEnvironmentVariable": addEnvironmentVariable_errors,
    "addService": addService_errors,
    "mountDirectory": mountDirectory_errors,
}

print("Initializing app...", end=" ")
print("OK")
print("    ", dash_app_name)

query_string = """
mutation {{
    addApp(name: "{dash_app_name}") {{
        app {{
            name
        }}
        error
    }}
}}
""".format(
    dash_app_name=dash_app_name
)

api_call = client.execute(gql(query_string))
for k, v in queries.items():
    if k in api_call and "error" in api_call[k]:
        if api_call[k]["error"] in v:
            raise Exception(api_call)

if len(target_app_name) != 0:
    print(f"Querying {target_app_name} settings...", end=" ")

    query_string = """
    {{
        apps(name: "{target_app_name}", allApps:true) {{
            apps {{
                name
                linkedServices {{
                    serviceType
                }}
                mounts {{
                    targetDir
                    hostDir
                }}
                environmentVariables {{
                    name
                    value
                }}
                metadata {{
                    permissionLevel
                }}
            }}
        }}
    }}""".format(
        target_app_name=target_app_name
    )

    api_call = client.execute(gql(query_string))

    api_call_results = []
    api_call_results = api_call["apps"]["apps"]

    for k, v in queries.items():
        if k in api_call and "error" in api_call[k]:
            if api_call[k]["error"] not in v:
                raise Exception(api_call)

    print("OK")
else:
    print("NULL")

print("Parsing API call", end=" ")
if len(api_call_results) != 0:

    print("OK")

    app_linkedServices = api_call_results[0]["linkedServices"]
    app_mounts = api_call_results[0]["mounts"]
    app_environmentVariables = api_call_results[0]["environmentVariables"]
    app_permissionLevel = api_call_results[0]["metadata"]
    app_name = api_call_results[0]["name"]

    app_linkedServices_serviceType = []
    print("Parsing LinkedServices...", end=" ")
    if len(app_linkedServices) != 0:
        print("OK")
        for i in range(len(app_linkedServices)):
            app_linkedServices_serviceType.append(app_linkedServices[i]["serviceType"])
            print("    ", app_linkedServices[i]["serviceType"])
    else:
        print("NULL")

    app_mounts_dict = dict()
    app_mounts_hostDir = []
    app_mounts_targetDir = []
    print("Parsing Mounts...", end=" ")
    if len(app_mounts) != 0:
        print("OK")
        for i in range(len(app_mounts)):
            app_mounts_hostDir.append(app_mounts[i]["hostDir"])
            app_mounts_targetDir.append(app_mounts[i]["targetDir"])
        app_mounts_dict = dict(zip(app_mounts_hostDir, app_mounts_targetDir))
        for k, v in app_mounts_dict.items():
            print("    ", k, " : ", v)
    else:
        print("NULL")

    app_environmentVariables_filter = [
        "DASH_APP_NAME",
        "DASH_DOMAIN_BASE",
        "DASH_LOGOUT_URL",
        "DASH_PATH_ROUTING",
        "DASH_SECRET_KEY",
        "DASH_STREAMBED_DIRECT_IP",
        "DATABASE_URL",
        "DOKKU_APP_RESTORE",
        "DOKKU_APP_TYPE",
        "DOKKU_PROXY_PORT",
        "DOKKU_PROXY_PORT_MAP",
        "GIT_REV",
        "REDIS_URL",
        "SCRIPT_NAME",
        "NO_VHOST",
    ]

    app_environmentVariables_dict = dict()
    app_environmentVariables_name = []
    app_environmentVariables_value = []
    print("Parsing EnvironmentVariables...", end=" ")
    if len(app_environmentVariables) != 0:
        print("OK")
        for i in range(len(app_environmentVariables)):
            app_environmentVariables_name.append(app_environmentVariables[i]["name"])
            app_environmentVariables_value.append(app_environmentVariables[i]["value"])
        app_environmentVariables_dict = dict(
            zip(app_environmentVariables_name, app_environmentVariables_value)
        )
        for k, v in app_environmentVariables_dict.items():
            print("    ", k, " : ", v)

    app_permissionLevel = []
    app_permissionLevel_name = []
    app_permission_level_dict = dict()
    print("Parsing PermissionLevels...", end=" ")
    if len(app_permissionLevel) != 0:
        print("OK")
        for i in range(len(app_permissionLevel)):
            app_permissionLevel.append(app_permissionLevel[i]["permissionLevel"])
            app_permissionLevel_name.append(app_name[i]["name"])
        app_permission_level_dict = zip(app_permissionLevel, app_permissionLevel_name)
else:
    print("NULL")

print("Updating {dash_app_name}...".format(dash_app_name=dash_app_name), end=" ")
if len(api_call_results) != 0:
    print("OK")
    print("Updating LinkedServices...", end=" ")
    if len(app_linkedServices) != 0:
        print("OK")
        filtered_dict = dict()
        for i in app_linkedServices_serviceType:
            query_string = """
            mutation {{
                addService (name: "{dash_app_name}", serviceType:{service_type}) {{
                    service {{
                        name
                        serviceType
                        created
                    }}
                    error
                }}
            }}  
            """.format(
                service_type=i, dash_app_name=dash_app_name
            )
            client.execute(gql(query_string))

            print(
                "   {dash_app_name}-{service_type}, {service_type}".format(
                    service_type=i, dash_app_name=dash_app_name
                )
            )
    else:
        print("NULL")

    print("Updating Mounts...", end=" ")
    if len(app_mounts_dict) != 0:
        print("OK")
        for k, v in app_mounts_dict.items():
            query_string = """
                mutation {{
                    mountDirectory(
                        hostDir: "{app_mounts_hostDir}",
                        targetDir: "{app_mounts_targetDir}", 
                        appname: "{dash_app_name}"
                        ) {{
                            ok
                            error
                        }}
                }}
                """.format(
                app_mounts_hostDir=k,
                app_mounts_targetDir=v,
                dash_app_name=dash_app_name,
            )
            client.execute(gql(query_string))

            print("    ", k, "to", v)

    else:
        print("NULL")

    # Environment Variables

    print("Updating EnvironmentVariables...", end=" ")
    if len(app_environmentVariables_dict) != 0:
        print("OK")
        for k, v in app_environmentVariables_dict.items():
            if k not in app_environmentVariables_filter:
                query_string = """
                    mutation {{
                        addEnvironmentVariable(
                            name: "{k}",
                            value: "{v}",
                            appname: "{dash_app_name}"
                        ){{
                            ok
                            error
                        }}
                    }}
                    """.format(
                    k=k, v=v, dash_app_name=dash_app_name
                )
                client.execute(gql(query_string))
                print("    ", k, " : ", v)
    else:
        print("NULL")
else:
    print("NULL")


print("Deploying {dash_app_name}...".format(dash_app_name=dash_app_name), end=" ")
if os.getenv("CIRCLECI") == "true":
    print("OK")
    subprocess.run(
        f"""
        echo "{ssh_private_key}" | tr ',' '\n' > ~/.ssh/id_rsa
        chmod 600 ~/.ssh/id_rsa
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/id_rsa
        echo "{ssh_config}" | tr ',' '\n' > ~/.ssh/config
        git config remote.plotly.url >&- || git remote add plotly dokku@{dash_enterprise_host}:{dash_app_name}
        git push --force plotly HEAD:master
        """,
        shell=True,
    )
else:
    print("NULL")

print(
    "\nView your Dash app:",
    f"https://{dash_enterprise_host}/Manager/graphql", 
    f"https://{dash_enterprise_host}/Manager/apps/{dash_app_name}/overview", f"https://{dash_enterprise_host}/{dash_app_name}/", sep="\n", end=" "
)   
