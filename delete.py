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
    username_api_k = os.getenv("USERNAME_API_KEY")
    ssh_config = os.getenv("SSH_CONFIG")
    ssh_private_k = os.getenv("SSH_PRIVATE_KEY")
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

app_results = []
apps = []
services_results = []
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

    app_results = api_call["apps"]["apps"]
    service_results = api_call["services"]
    
    app_results.extend(apps)

    try:
        services_results.extend(services)
    except KeyError:
        continue

    for k, v in queries.items():
        if k in api_call and "error" in api_call[k]:
            if api_call[k]["error"] in v:
                raise Exception(api_call)

print("OK")

print(" Parsing apps...", end=" ")
app_names = []
app_updated = []
app_created = []
app_dict = dict()
if len(app_results) != 0:
    for i in range(len(app_results)):
        app_names.append(app_results[i]["analytics"]["appname"])
        app_created.append(app_results[i]["analytics"]["timestamps"]["created"])
        app_updated.append(app_results[i]["analytics"]["timestamps"]["updated"])
        app_dict.update(zip(app_names, zip(app_updated, app_created)))
    print("OK")
else:
    print("NULL")
    sys.exit()

print(" Filtering apps...", end=" ")
filtered_apps = dict()
if len(app_results) != 0:
    print("OK")
    for k, v in app_dict.items():
        if k.startswith("{prefix}".format(prefix=prefix)) and v[0] == None and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f")) >  timedelta(days=last_update):
            filtered_apps[k] = v[0]
        elif k.startswith("{prefix}".format(prefix=prefix)) and v[1] != None and (datetime.now() - datetime.strptime(v[1], "%Y-%m-%dT%H:%M:%S.%f")) > timedelta(days=last_update):
            filtered_apps[k] = v[1]
else:
    print("NULL")
    sys.exit()

print(" Deleting apps...", end=" ")
if filtered_apps != False:
    print("OK")    
    for k in filtered_apps:
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




print(" Parsing services...", end=" ")
service_names = []
service_types = []
services_dict = dict()
if len(service_results) != 0:
    for i in range(len(services)):
        service_names.append(service_results[i]["services"]["name"])
        service_types.append(service_results[i]["services"]["serviceType"])
        services_dict.update(zip(service_names, service_types))
    print("OK")   
else:     
    print("NULL")


print(" Filtering services...", end=" ")
filtered_services = dict()
if  len(service_results) != 0:
    print("OK")
    for k, v in services_dict:
        if k.startwith(k) in filtered_apps:
            filtered_services[k] = filtered_services[v]
else:     
    print("NULL")


print(" Deleting services...", end=" ")
if filtered_services != False:
    print("OK")
    for k, v in filtered_services.items():
         
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
        print("    ",k)
        # client.execute(gql(query_string))
else:
    print("NULL")

# print(
#     f"https://{dash_enterprise_host}/Manager/graphql", 
#     f"https://{dash_enterprise_host}/Manager/apps/{dash_app_name}/overview", f"https://{dash_enterprise_host}/{dash_app_name}/", sep="\n", end=" "
# )
