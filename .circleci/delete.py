from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
import sys, os, random, string, logging
from time import sleep

DEBUG = os.getenv("DEBUG", "false")

if sys.version_info[0] < 3.6 and sys.version_info[0] > 3.7:
    raise Exception("Python 3.6 is required.")

if DEBUG == "true":
    logging.basicConfig(level=logging.DEBUG)

if os.getenv("CIRCLECI") == "true":
    branch_name = os.getenv("CIRCLE_BRANCH")
    dash_app_name = f"review-app-{branch_name}".replace("_", "-")
    dash_enterprise_host = os.getenv("DASH_ENTERPRISE_HOST")
    username = os.getenv("USERNAME")
    username_password = os.getenv("USERNAME_PASSWORD")
    username_api_key = os.getenv("USERNAME_API_KEY")
    ssh_config = os.getenv("SSH_CONFIG")
    ssh_private_key = os.getenv("SSH_PRIVATE_KEY")
    prefix = "aa-chris-rev"
    last_update = {"days": 3}

else:
    dash_enterprise_host = "dash-playground.plotly.host"
    username = "developers"
    username_api_key = "faBhA8WwjuLpC8QoEulU"
    dash_app_name = "review-app-" + "".join(
        random.choices(string.ascii_lowercase + string.digits, k=6)
    )
    prefix = "review-app"
    last_update = {"days": 1}
    # days, hours, minutes

transport = RequestsHTTPTransport(
    url="https://{dash_enterprise_host}/Manager/graphql".format(
        dash_enterprise_host=dash_enterprise_host
    ),
    auth=(username, username_api_key),
    use_json=True,
    retries=3,
)

client = Client(transport=transport)

deleteApp_errors = [
    "App does not exist.",
    "Invalid app name. Names should be between 3 to 30 characters long, start with a letter, and only contain lower case letters, numbers, and -",
]

queries = {
    "deleteApp": deleteApp_errors,
}
print("Querying apps...", end=" ")

apps_result = []
apps = []
services_result = []
services = []
page = 0

print("OK")
while len(apps_result) != 0 or page == 0: #len(apps) != 0 or 
    query = gql(
        """
        query($page: Int) {
        apps(page: $page, allApps:true) {
                apps {
                    analytics {
                        appname
                        timestamps {
                            created
                            updated
                        }
                    }
                    linkedServices {
                        name
                        serviceType
                    }  
                }
            }  
        }
        """
    )
    params = {"page": page}
    api_call = client.execute(query,variable_values=params)
    apps_result = api_call["apps"]["apps"]
    apps.extend(apps_result)
    print(f"    Page: {page}")
    page = page + 1

print("\n    Total apps: ", len(apps), "\n")
print(" Parsing apps and services...", end=" ")
apps_name = []
apps_updated = []
apps_created = []
services_name = []
services_type = []
apps_dict = dict()
services_dict = dict()
if len(apps) != 0:
    print("OK")
    for i in range(len(apps)):
        apps_name.append(apps[i]["analytics"]["appname"])
        apps_created.append(apps[i]["analytics"]["timestamps"]["created"])
        apps_updated.append(apps[i]["analytics"]["timestamps"]["updated"])
        apps_dict.update(zip(apps_name, zip(apps_updated, apps_created)))

        if range(len(apps[i]["linkedServices"])) == range(0, 1):
            services_name.append(apps[i]["linkedServices"][0]["name"])
            services_type.append(apps[i]["linkedServices"][0]["serviceType"])
        elif range(len(apps[i]["linkedServices"])) == range(1, 2):
            services_name.append(apps[i]["linkedServices"][1]["name"])
            services_type.append(apps[i]["linkedServices"][1]["serviceType"])
        elif range(len(apps[i]["linkedServices"])) == range(0, 2):
            services_name.append(apps[i]["linkedServices"][0]["name"])
            services_type.append(apps[i]["linkedServices"][0]["serviceType"])
            services_name.append(apps[i]["linkedServices"][1]["name"])
            services_type.append(apps[i]["linkedServices"][1]["serviceType"])
        services_dict.update(zip(services_name, zip(apps_name, services_type)))
else:
    print("NULL")
    sys.exit()

print(" Filtering apps...", end=" ")
apps_filtered = dict()
if len(apps) != 0:
    print("OK")
    for k, v in apps_dict.items():
        if (
            k.startswith("{prefix}".format(prefix=prefix))
            and v[0] == None
            and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f"))
            > timedelta(**last_update)
        ):
            apps_filtered[k] = v[0]
        elif (
            k.startswith("{prefix}".format(prefix=prefix))
            and v[1] != None
            and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f"))
            > timedelta(**last_update)
        ):
            apps_filtered[k] = v[1]
            print(apps_filtered)
else:
    print("NULL")
    sys.exit()

print(" Deleting apps...", end=" ")
if apps_filtered != False:
    print("OK")
    for k in apps_filtered:
        print("    ", k)
        query = gql(
            """
            mutation ($name: String) {
                deleteApp(name: $name) {
                    ok
                    error
                }
            }
            """
        )
        params = {"name": k}
        client.execute(query,variable_values=params)
else:
    print("NULL")

print(" Filtering services...", end=" ")
services_filtered = dict()
if len(services_dict) != 0:
    print("OK")
    for k, v in services_dict.items():
        if services_dict[k][0] in apps_filtered:
            services_filtered[k] = v[1]
            print("    ", k, v[1])
else:
    print("NULL")

print(" Deleting services...", end=" ")
if len(services_dict) != 0:
    print("OK")
    for k, v in services_filtered.items():

        query = gql(
            """
            mutation ($name: String, $serviceType: ServiceType){
                deleteService(name: $name, serviceType: $serviceType){
                    error
                    ok
                }
            }
            """
        )
        params = {"name": k, "serviceType": v}
        client.execute(query,variable_values=params)
        print("    ", k, v)
else:
    print("NULL")

