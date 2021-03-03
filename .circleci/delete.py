"""
This script deletes your Review apps and their linked databases. It is intended
to be run on a schedule.
"""

import sys
from datetime import datetime, timedelta
from time import sleep
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from settings import (
    DASH_ENTERPRISE_HOST,
    SERVICE_USERNAME,
    SERVICE_API_KEY,
    PREFIX,
    PERIOD,
    TIME,
    LAST_UPDATE,
    TARGET_APPNAME,
)

if sys.version_info[0:2] < (3, 6) or sys.version_info[0:2] > (3, 7):
    raise Exception(
        "This script has only been tested on Python 3.6. "
        + "You are using {major}.{minor}.".format(
            major=sys.version_info[0], minor=sys.version_info[1]
        )
    )

transport = RequestsHTTPTransport(
    url="https://{DASH_ENTERPRISE_HOST}/Manager/graphql".format(
        DASH_ENTERPRISE_HOST=DASH_ENTERPRISE_HOST
    ),
    auth=(SERVICE_USERNAME, SERVICE_API_KEY),
    use_json=True,
    retries=5,
)

client = Client(transport=transport)

PAGE = 0

apps = []
apps_result = []
services = []

print("Querying apps...\n")
while len(apps_result) != 0 or PAGE == 0:
    query = gql(
        """
        query($PAGE: Int) {
        apps(page: $PAGE, allApps:true) {
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
    params = {"PAGE": PAGE}
    sleep(5)
    api_call = client.execute(query, variable_values=params)
    apps_result = api_call["apps"]["apps"]
    apps.extend(apps_result)
    print("  Page: {PAGE}".format(PAGE=PAGE))
    PAGE = PAGE + 1
print("\n  Apps: {apps}\n".format(apps=len(apps)))

if len(apps) == 0:
    sys.exit(
        "No apps were found by user {username}.".format(username=SERVICE_USERNAME)
        + "Check that {username} owns apps or has admin privileges.\n".format(
            username=SERVICE_USERNAME
        )
    )


apps_name = []
apps_updated = []
apps_created = []
services_name = []
services_type = []
apps_dict = dict()
services_dict = dict()

print("Discovering linked databases associated with the apps...")
for i in range(len(apps)):
    apps_name.append(apps[i]["analytics"]["appname"])
    apps_created.append(apps[i]["analytics"]["timestamps"]["created"])
    apps_updated.append(apps[i]["analytics"]["timestamps"]["updated"])
    apps_dict.update(zip(apps_name, zip(apps_updated, apps_created)))
    for j in range(len(apps[i]["linkedServices"])):
        services_name.append(apps[i]["linkedServices"][j]["name"])
        services_type.append(apps[i]["linkedServices"][j]["serviceType"])
        services_dict.update(zip(services_name, zip(apps_name, services_type)))

apps_filtered = dict()


print(
    "Determining which apps haven't been updated or visited the last "
    + "{time} {period}...".format(
        time=TIME,
        period=PERIOD,
    )
)
for app_name, app_time in apps_dict.items():
    # app_time[0] is the time last updated
    # app_time[1] is the time last viewed
    if (
        app_name.startswith(PREFIX)
        and app_time[0] is None
        and (datetime.now() - datetime.strptime(app_time[1], "%Y-%m-%dT%H:%M:%S.%f"))
        > timedelta(**LAST_UPDATE)
    ):
        print("  {app_name}".format(app_name=app_name))
        apps_filtered[app_name] = app_time[0]
    elif (
        app_name.startswith(PREFIX)
        and app_time[1] is not None
        and (datetime.now() - datetime.strptime(app_time[1], "%Y-%m-%dT%H:%M:%S.%f"))
        > timedelta(**LAST_UPDATE)
    ):
        print("  {app_name}".format(app_name=app_name))
        apps_filtered[app_name] = app_time[1]
print(
    "\n  Apps filtered: {total_apps_filtered}\n".format(
        total_apps_filtered=len(apps_filtered.items())
    )
)


print(
    "Deleting apps that haven't been updated or visited in over "
    + "{time} {period}...".format(
        time=TIME,
        period=PERIOD,
    )
)
for app_name in apps_filtered:
    print("  {app_name}".format(app_name=app_name))
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
    params = {"name": app_name}
    client.execute(query, variable_values=params)
    sleep(10)

services_filtered = dict()
if len(services_dict) != 0:
    print("Discovering databases associated with deleted apps...")
    for service_name, service_type in services_dict.items():
        if services_dict[service_name][0] in apps_filtered:
            services_filtered[service_name] = service_type[1]
    print(
        "  Databases filtered: {total_db_filtered}\n".format(
            total_db_filtered=len(services_filtered.items())
        )
    )
else:
    print("No databases associated with deleted apps were found.")
    sys.exit()

print("Deleting associated databases...")
for service_name, service_type in services_filtered.items():
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
    params = {"name": service_name, "serviceType": service_type}
    client.execute(query, variable_values=params)
    print(
        "  name: {service_name}, type: {service_type}".format(
            service_name=service_name, service_type=service_type
        )
    )
