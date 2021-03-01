"""This script allows you to delete your Review apps on a schedule."""

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
    LAST_UPDATE,
)

if sys.version_info[0] < 3.6 and sys.version_info[0] > 3.7:
    raise Exception(
        "This script has only been tested on Python 3.6."
        + "You are using {version}.".format(version=sys.version_info[0])
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
    print(f"  Page: {PAGE}")
    PAGE = PAGE + 1
print("\n  Apps: {apps}\n".format(apps=len(apps)))

if len(apps) == 0:
    print(
        "No apps were found by user {username}.".format(username=SERVICE_USERNAME)
        + "Check that {username} owns apps or has admin privileges.\n".format(
            username=SERVICE_USERNAME
        )
    )
    sys.exit()

apps_name = []
apps_updated = []
apps_created = []
services_name = []
services_type = []
apps_dict = dict()
services_dict = dict()
if len(apps) != 0:
    print("Discovering linked databases associated with the apps...")
    for i in enumerate(apps):
        apps_name.append(apps[i]["analytics"]["appname"])
        apps_created.append(apps[i]["analytics"]["timestamps"]["created"])
        apps_updated.append(apps[i]["analytics"]["timestamps"]["updated"])
        apps_dict.update(zip(apps_name, zip(apps_updated, apps_created)))
        for j in range(len(apps[i]["linkedServices"])):
            services_name.append(apps[i]["linkedServices"][j]["name"])
            services_type.append(apps[i]["linkedServices"][j]["serviceType"])
            services_dict.update(zip(services_name, zip(apps_name, services_type)))
else:
    print("No linked databases associated with the apps were discovered.")


apps_filtered = dict()
if len(apps) != 0:
    print(
        "Determining which apps haven't been updated or visited in "
        + "{time} {period}...".format(
            time=LAST_UPDATE.values(),
            period=LAST_UPDATE.keys(),
        )
    )
    for app_name, app_time in apps_dict.items():
        if (
            app_name.startswith("{prefix}".format(prefix=PREFIX))
            and app_time[0] is None
            and (
                datetime.now() - datetime.strptime(app_time[1], "%Y-%m-%dT%H:%M:%S.%f")
            )
            > timedelta(**LAST_UPDATE)
        ):
            print("  {app_name}".format(app_name=app_name))
            apps_filtered[app_name] = app_time[0]
        elif (
            app_name.startswith("{prefix}".format(prefix=PREFIX))
            and app_time[1] is not None
            and (
                datetime.now() - datetime.strptime(app_time[1], "%Y-%m-%dT%H:%M:%S.%f")
            )
            > timedelta(**LAST_UPDATE)
        ):
            print("  {app_name}".format(app_name=app_name))
            apps_filtered[app_name] = app_time[1]
    if len(apps_filtered.items()) > 0:
        print(f"\n  Apps filtered: {len(apps_filtered.items())}\n")
else:
    print(
        "All apps have been updated or visited since in the last "
        + "{time} {period}.".format(
            time=LAST_UPDATE.values(),
            period=LAST_UPDATE.keys(),
        )
    )
    sys.exit()


print(
    "Deleting apps that haven't been updated or visited in "
    + "{time} {period}...".format(
        time=LAST_UPDATE.values(),
        period=LAST_UPDATE.keys(),
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


services_filtered = dict()
if len(services_dict) != 0:
    print("Discovering databases associated with deleted apps...")
    for service_name, service_type in services_dict.items():
        if services_dict[service_name][0] in apps_filtered:
            services_filtered[service_name] = service_type[1]
    if len(services_filtered.items()) > 0:
        print(f"\n  Databases filtered: {len(services_filtered.items())}\n")
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
