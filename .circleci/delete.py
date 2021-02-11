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

apps = []
apps_result = []
services = []
services_result = []
page = 0

if 1 != 0:
    print("Querying apps...\n")
    while len(apps_result) != 0 or page == 0:
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
        api_call = client.execute(query,variable_values=params)
        apps_result = api_call["apps"]["apps"]
        apps.extend(apps_result)
        print(f"  Page: {page}")
        page = page + 1
    print(f"\n  Apps: {len(apps)}\n")
else:
    print("No apps were queried")


apps_name = []
apps_updated = []
apps_created = []
services_name = []
services_type = []
apps_dict = dict()
services_dict = dict()
if len(apps) != 0:
    print("Parsing apps...")
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
    print("No apps were parsed")


apps_filtered = dict()
if len(apps) != 0:
    print("Filtering apps...")
    for k, v in apps_dict.items():
        if (
            k.startswith("{prefix}".format(prefix=PREFIX))
            and v[0] == None
            and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f"))
            > timedelta(**LAST_UPDATE)
        ):
            print(f"  {k}")
            apps_filtered[k] = v[0]
        elif (
            k.startswith("{prefix}".format(prefix=PREFIX))
            and v[1] != None
            and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f"))
            > timedelta(**LAST_UPDATE)
        ):
            print(f"  {k}")
            apps_filtered[k] = v[1]
    print(f"\n  Apps filtered: {len(apps_filtered.items())}\n")
else:
    print("No apps were filtered")


if len(apps_filtered) != 0:
    print("Deleting apps...")
    for k in apps_filtered:
        print(f"  {k}")
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
    print("No apps were deleted")


services_filtered = dict()
if len(services_dict) != 0:
    print("Filtering services...")
    for k, v in services_dict.items():
        if services_dict[k][0] in apps_filtered:
            services_filtered[k] = v[1]
            # print(f"  {k}, {v[1]}")
    print(f"\n  Services filtered: {len(services_filtered.items())}\n")?
else:
    print("No services were filtered")


if len(services_filtered) != 0:
    print("Deleting services")
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
        print(f"  name: {k}, type: {v}")
else:
    print("No services were deleted")
