from gql import  gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
from sys import argv
import os


if os.getenv("CIRCLECI") == True:
    script, prefix_string, last_update = argv
    branch_name = os.getenv("CIRCLE_BRANCH")
    dash_app_name = f"review-app-{branch_name}".replace("_", "-")
    dash_enterprise_host = os.getenv("DASH_ENTERPRISE_HOST")
    username = os.getenv("USERNAME")
    username_password = os.getenv("USERNAME_PASSWORD")
    username_api_key = os.getenv("USERNAME_API_KEY")
    ssh_config = os.getenv("SSH_CONFIG")
    ssh_private_key = os.getenv("SSH_PRIVATE_KEY")
    prefix_string = str(prefix_string) 
    last_update = int(last_update) # days
else:
    import random
    import string

    script, prefix_string, last_update = argv
    dash_enterprise_host = "dash-playground.plotly.host"
    username = "developers"
    username_api_key = "faBhA8WwjuLpC8QoEulU"
    dash_app_name = "review-app-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    prefix_string = str(prefix_string)
    last_update = int(last_update)
 

transport = RequestsHTTPTransport(
    url =  "https://{dash_enterprise_host}/Manager/graphql".format(dash_enterprise_host = dash_enterprise_host), 
    auth = (username, username_api_key), 
    use_json = True
)

client = Client(transport = transport)

print("Querying all apps...", end=" ")

# Querying all apps

deleteApp_errors = [
    "App does not exist.",
    "Invalid app name. Names should be between 3 to 30 characters long, start with a letter, and only contain lower case letters, numbers, and -",
]

queries = {
    "'deleteApp'":"deleteApp_errors",
}

api_results = []
apps = []

page = 0
while len(apps) != 0 or page == 0:
    
    query_string = ("""
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
            }}   
        }}
    }}
    """.format(page = page))

    api_call =  client.execute(gql(query_string))
    page = 1 + page 
    apps = api_call["apps"]["apps"]
    api_results.extend(apps)

    for key,value in queries.items():
        if key in api_call and 'error' in api_call[key]:
            if api_call[key]['error'] not in value:
                raise Exception(api_call)

print("OK")

print("Parsing all apps...", end=" ")
if len(api_results) != 0:

    # Parse all app names and updated times from api_results, and append them to their respective lists.

    names = []
    times = []

    for i in range(len(api_results)):
        names.append(api_results[i]["analytics"]["appname"])
        times.append(api_results[i]["analytics"]["timestamps"]["updated"])

    zipped_dict = dict(zip(names, times))
    print("OK")


    # Filter zipped_dict:
    # 1. key.startswith("{string}".format(string = string)) == True
    # 2. (type(None) != type(value)) == True
    # 3. (datetime.now() - datetime.fromisoformat("{value}".format(value = value)) < timedelta(days=int)) == True
    print("Filtering all apps...", end=" ")
    filtered_dict = dict()

    for key, value in zipped_dict.items():
        if key.startswith("{prefix_string}".format(prefix_string = prefix_string)):
            if value != None:
                if (datetime.now() - datetime.fromisoformat("{value}".format(value=value)) < timedelta(days=last_update)):
                    filtered_dict[key] = value
    print("OK")

    # Delete all apps meeting filter conditions

    print("Deleting filtered apps...")

    for key in filtered_dict:

        print("> Deleting {key}...".format(key = key), end=" ")
        query_string = ("""
        mutation {{
            AddApp(name: "{key}") {{
                ok
                error
            }}
        }}
        """.format(key = key))
        # client.execute(gql(query_string))
        print("OK")
  
else:
    print("NULL")