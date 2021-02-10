import logging
import os
import sys
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
from time import sleep
from config import (
    DEBUG,
    DASH_ENTERPRISE_HOST,
    SERVICE_USERNAME,
    SERVICE_API_KEY,
    SSH_CONFIG,
    DEBUG,
    PREFIX,
    LAST_UPDATE,
)

if sys.version_info[0] < 3.6 and sys.version_info[0] > 3.7:
    raise Exception("Python 3.6 is required.")

if DEBUG == "true":
    logging.basicConfig(level=logging.DEBUG)

transport = RequestsHTTPTransport(
    url=f"https://{DASH_ENTERPRISE_HOST}/Manager/graphql",
    auth=(SERVICE_USERNAME, SERVICE_API_KEY),
    use_json=True,
    retries=5,
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

apps = []
services = []
page = 0

print("OK")
while len(apps) != 0 or page == 0:
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
    sleep(5)
    result = client.execute(query,variable_values=params)
    apps= result["apps"]["apps"]
    apps.extend(apps)
    print(f"    Page: {page}")
    page = page + 1

print("\n    Total apps: ", len(apps), "\n")
print(" Parsing apps and services...", end=" ")
apps_name = []
apps_updated = []
apps_created = []
services_name = []
services_type = []
apps = dict()
services = dict()
if len(apps) != 0:
    print("OK")
    for i in range(len(apps)):
        apps_name.append(apps[i]["analytics"]["appname"])
        apps_created.append(apps[i]["analytics"]["timestamps"]["created"])
        apps_updated.append(apps[i]["analytics"]["timestamps"]["updated"])
        apps.update(zip(apps_name, zip(apps_updated, apps_created)))

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
        services.update(zip(services_name, zip(apps_name, services_type)))
else:
    print("NULL")
    sys.exit()

print(" Filtering apps...", end=" ")
apps_filtered = dict()
if len(apps) != 0:
    print("OK")
    for k, v in apps.items():
        if (
            k.startswith(f"{PREFIX}")
            and v[0] == None
            and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f"))
            > timedelta(**LAST_UPDATE)
        ):
            apps_filtered[k] = v[0]
            print(datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f"))
            print(timedelta(**LAST_UPDATE))
        elif (
            k.startswith(f"{PREFIX}")
            and v[1] != None
            and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f"))
            > timedelta(**LAST_UPDATE)
        ):
            apps_filtered[k] = v[1]
            print(datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f"))
            print(timedelta(**LAST_UPDATE))
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
if len(services) != 0:
    print("OK")
    for k, v in services.items():
        if services[k][0] in apps_filtered:
            services_filtered[k] = v[1]
            print("    ", k, v[1])
else:
    print("NULL")

print(" Deleting services...", end=" ")
if len(services) != 0:
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

