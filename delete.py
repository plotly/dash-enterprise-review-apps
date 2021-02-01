from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
from sys import argv
import sys, os, random, string

if sys.version_info[0] < 3.6 and sys.version_info[0] > 3.7:
    raise Exception("Python 3.6 is required.")

script, prefix, last_update = argv

if os.getenv("CIRCLECI") == "true":
    branch_name = os.getenv("CIRCLE_BRANCH")
    dash_app_name = f"review-app-{branch_name}".replace("_", "-")
    dash_enterprise_host = os.getenv("DASH_ENTERPRISE_HOST")
    username = os.getenv("USERNAME")
    username_password = os.getenv("USERNAME_PASSWORD")
    username_api_key = os.getenv("USERNAME_API_KEY")
    ssh_config = os.getenv("SSH_CONFIG")
    ssh_private_key = os.getenv("SSH_PRIVATE_KEY")
    prefix = str(prefix)
    last_update = float(last_update)  # days
else:
    dash_enterprise_host = "dash-playground.plotly.host"
    username = "developers"
    username_api_key = "faBhA8WwjuLpC8QoEulU"
    dash_app_name = "review-app-" + "".join(
        random.choices(string.ascii_lowercase + string.digits, k=6)
    )
    prefix= str(prefix)
    last_update = float(last_update) # days


transport = RequestsHTTPTransport(
    url="https://{dash_enterprise_host}/Manager/graphql".format(
        dash_enterprise_host=dash_enterprise_host
    ),
    auth=(username, username_api_key),
    use_json=True,
    retries=3,
)

client = Client(transport=transport)

print(" Querying apps...", end=" ")

deleteApp_errors = [
    "App does not exist.",
    "Invalid app name. Names should be between 3 to 30 characters long, start with a letter, and only contain lower case letters, numbers, and -",
]

queries = {
    "deleteApp": deleteApp_errors,
}

apps_result = []
apps = []
services_result = []
services = [] 

page = 0
while len(apps) != 0 or page == 0:

    query_string = """
    query {{
        apps(page: {page}, allApps:true) {{
            apps {{
                analytics {{
                    appname
                    timestamps {{
                        created
                        updated
                    }}
                }}
                linkedServices {{
                    name
                    serviceType
                }}  
            }}
        }}
        services {{
            name
            serviceType 
        }}  
    }}
    """.format(
        page=page
    )

    api_call = client.execute(gql(query_string))
    page = page + 1

    apps_result = api_call["apps"]["apps"]
    services_result = api_call["services"]

    apps_result.extend(apps)

    try:
        services_result.extend(services)
    except KeyError:
        continue

    for k, v in queries.items():
        if k in api_call and "error" in api_call[k]:
            if api_call[k]["error"] in v:
                raise Exception(api_call)

print("OK")

print(" Parsing apps...", end=" ")
apps_name = []
apps_updated = []
apps_created = []
services_name = []
services_type = []
apps_dict = dict()
services_dict = dict()
if len(apps_result) != 0:
    print("OK")
    for i in range(len(apps_result)):
        apps_name.append(apps_result[i]["analytics"]["appname"])
        apps_created.append(apps_result[i]["analytics"]["timestamps"]["created"])
        apps_updated.append(apps_result[i]["analytics"]["timestamps"]["updated"])
        apps_dict.update(zip(apps_name, zip(apps_updated, apps_created)))
        if range(len(apps_result[i]["linkedServices"])) == range(0,1):
            services_name.append(apps_result[i]["linkedServices"][0]["name"])
            services_type.append(apps_result[i]["linkedServices"][0]["serviceType"])
        elif range(len(apps_result[i]["linkedServices"])) == range(1,2):
            services_name.append(apps_result[i]["linkedServices"][1]["name"])
            services_type.append(apps_result[i]["linkedServices"][1]["serviceType"])
        elif range(len(apps_result[i]["linkedServices"])) == range(0,2):
            services_name.append(apps_result[i]["linkedServices"][0]["name"])
            services_type.append(apps_result[i]["linkedServices"][0]["serviceType"])
            services_name.append(apps_result[i]["linkedServices"][1]["name"])
            services_type.append(apps_result[i]["linkedServices"][1]["serviceType"])
        services_dict.update(zip(services_name, zip(apps_name, services_type)))
else:
    print("NULL")
    sys.exit()

print(" Filtering apps...", end=" ")
apps_filtered = dict()
if len(apps_result) != 0:
    print("OK")
    for k, v in apps_dict.items():
        if k.startswith("{prefix}".format(prefix=prefix)) and v[0] == None and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f")) >  timedelta(days=last_update):
            apps_filtered[k] = v[0]
        elif k.startswith("{prefix}".format(prefix=prefix)) and v[1] != None and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f")) > timedelta(days=last_update):
            apps_filtered[k] = v[1]
else:
    print("NULL")
    sys.exit()

print(" Deleting apps...", end=" ")
if apps_filtered != False:
    print("OK")    
    for k in apps_filtered:
        print("    ", k)
        query_string = """
            mutation {{
                deleteApp(name: "{k}") {{
                    ok
                    error
                }}
            }}
            """.format(
                k=k
            )
        # client.execute(gql(query_string))
        for k, v in queries.items():
            if k in api_call and "error" in api_call[k]:
                if api_call[k]["error"] in v:
                    raise Exception(api_call) 
else:
    print("NULL")

print(" Filtering services...", end=" ")
services_filtered = dict()
if  len(services_dict) != 0:
    print("OK")
    for k, v in services_dict.items():
        if v[0] in apps_filtered:
            services_filtered[k] = v[1]
            print("    ", k, v[1])
else:     
    print("NULL")

print(" Deleting services...", end=" ")
if services_filtered != False:
    print("OK")
    for k, v in services_filtered.items():
        
        query_string = """
            mutation{{
                deleteService(name: "{k}", serviceType: {v}){{
                    error
                    ok
                }}
            }}
            """.format(
                k=k, 
                v=v
            )
        print("    ", k, v)
        # client.execute(gql(query_string))
else:
    print("NULL")

# print(
#     f"https://{dash_enterprise_host}/Manager/graphql", 
#     f"https://{dash_enterprise_host}/Manager/apps/{dash_app_name}/overview", f"https://{dash_enterprise_host}/{dash_app_name}/", sep="\n", end=" "
# )
