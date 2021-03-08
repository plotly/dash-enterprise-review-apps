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
    TIME_UNIT,
    TIMESPAN,
    LAST_UPDATE,
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

print()
print("Running delete.py...")
print()
print("Querying apps...")

# while len(apps_result) != 0 or PAGE == 0:
#     query = gql(
#         """
#         query($PAGE: Int) {
#         apps(page: $PAGE, allApps:true) {
#                 apps {
#                     analytics {
#                         appname
#                         timestamps {
#                             created
#                             updated
#                         }
#                     }
#                     linkedServices {
#                         name
#                         serviceType
#                     }
#                 }
#             }
#         }
#         """
#     )
#     params = {"PAGE": PAGE}
#     sleep(2)
#     api_call = client.execute(query, variable_values=params)
#     apps_result = api_call["apps"]["apps"]
#     apps.extend(apps_result)

#     print("  Total: {apps_total}".format(apps_total=len(apps)), end="\r")
#     PAGE = PAGE + 1
# print("  Total: {apps_total}".format(apps_total=len(apps)))

if len(apps) == 0:
    sys.exit(
        "No apps were found. ".format(SERVICE_USERNAME=SERVICE_USERNAME)
        + 'Check that user "{SERVICE_USERNAME}" '.format(
            SERVICE_USERNAME=SERVICE_USERNAME
        )
        + "owns apps or has admin privileges."
    )

apps_name = []
apps_updated = []
apps_created = []
services_name = []
services_type = []
apps_dict = dict()
services_dict = dict()

print("Discovering linked databases...")
for _, app in enumerate(apps):
    apps_name.append(app["analytics"]["appname"])
    apps_created.append(app["analytics"]["timestamps"]["created"])
    apps_updated.append(app["analytics"]["timestamps"]["updated"])
    apps_dict.update(zip(apps_name, zip(apps_updated, apps_created)))
    for _, service in enumerate(app["linkedServices"]):
        services_name.append(service["name"])
        services_type.append(service["serviceType"])
        services_dict.update(zip(services_name, zip(apps_name, services_type)))

apps_filtered = dict()

print("  Total: {databases_total}".format(databases_total=len(services_dict.items())))


print(
    "Determining which Review Apps haven't been updated or visited the last"
    + " {TIMESPAN} {TIME_UNIT}...".format(
        TIMESPAN=TIMESPAN,
        TIME_UNIT=TIME_UNIT,
    )
)

for app_name, app_time in apps_dict.items():
    TIME_UPDATED = app_time[0]
    TIME_CREATED = app_time[1]
    if (
        app_name.startswith(PREFIX)
        and TIME_UPDATED is None
        and (datetime.now() - datetime.strptime(TIME_CREATED, "%Y-%m-%dT%H:%M:%S.%f"))
        > timedelta(**LAST_UPDATE)
    ):
        print("  {app_name}".format(app_name=app_name))
        apps_filtered[app_name] = TIME_CREATED
    elif (
        app_name.startswith(PREFIX)
        and TIME_UPDATED is not None
        and (datetime.now() - datetime.strptime(TIME_UPDATED, "%Y-%m-%dT%H:%M:%S.%f"))
        > timedelta(**LAST_UPDATE)
    ):
        print("  {app_name}".format(app_name=app_name))
        apps_filtered[app_name] = TIME_UPDATED
print(
    "  Total: {total_apps_filtered}".format(
        total_apps_filtered=len(apps_filtered.items())
    ),
)

if len(apps_filtered.items()) != 0:
    print(
        "Deleting apps that haven't been updated or visited in over "
        + "{TIMESPAN} {TIME_UNIT}...".format(
            TIMESPAN=TIMESPAN,
            TIME_UNIT=TIME_UNIT,
        )
    )
else:
    print(
        "All Review Apps have been updated or visited in the last "
        + "{TIMESPAN} {TIME_UNIT}...".format(
            TIMESPAN=TIMESPAN,
            TIME_UNIT=TIME_UNIT,
        )
    )
    print("  No apps deleted")
    sys.exit(0)


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
    sleep(20)

    services_filtered = dict()
    if len(services_dict) != 0:
        print("Discovering databases associated with deleted apps...")
        for service_name, service_type in services_dict.items():
            if services_dict[service_name][0] in apps_filtered:
                services_filtered[service_name] = service_type[1]
        print(
            "  Total: {total_db_filtered}".format(
                total_db_filtered=len(services_filtered.items())
            )
        )
    else:
        print("No databases associated with deleted apps were found.")
        sys.exit(0)

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
