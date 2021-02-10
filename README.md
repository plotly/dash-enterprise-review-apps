# dash-enterprise-ci-qa
QA repo to test out deploying Dash apps via CI pipelines

---
Part 1 - Create an app & deploy that app when creating a pull request

- [x] Get the documented simple graphql examples to run in Python (demo_examples.py)
  - [x] First 10 apps
  - [x] Get all fields for a particular app
  - [x] Get the owner for a particular app
  - [x] View Which Apps Promoted to the Portal
  - [x] Python example
- [x] Create a simple example that creates an app in the graphql sandbox
- [x] Migrate that example to your python script (demo_add_app.py)
- [x] Get this python script to work in circleci - so when you create a new pull request, it initializes an app on dash enterprise.
- [x] Modify the script to create the app name based off of the branch name, e.g. review-app-<branch-name>
  
Part 2 - Scheduler: Delete apps that haven't been updated in X amount of time

- [x] Create a hello world scheduler on CircleCI that prints "hello world" every Y amount of time
- [x] Create a GraphQL API call to query all of the app names and last modified date of the apps. Use the sandbox as appropriate.
- [x] Get this API call to work in Python
- [x] Create a GraphQL API call to delete an app based off of its name. Use the sandbox as appropriate.
- [x] Combine (2) & (4) to create a script that deletes all apps with the prefix review-app- that haven't been updated in X amount of time (e.g. 5 days, 1 hour).
- [x] Combine (1) & (5) to run this script every Y amount of time.

Part 3 - Auto-Configuration of Review Apps: Copy the configuration of the main application to the review app

- [x] Create a GraphQL API call that queries the environment variables of a particular app
- [x] Create a GraphQL API call that queries the database mappings of a particular app
- [x] Create a GraphQL API call that queries whether or not the app has a postgres database attached to it
- [x] Create a GraphQL API call that queries whether or not the app has a redis database attached to it
- [x] Combine this into a single API call if possible
- [x] Create a GraphQL API call that sets these same settings on a new app
- [ ] Combine with Part 1 #5 so that a new app that is created gets these settings

Part 4 - Production

- [x] Add error handling & retrying. If an API call fails, try it again. Explicitly check for status code != 200

Part 5 - Documentation

- [x] Environment Variables
  - [x] Copy
  - [ ] Assets
---

## Dash Enterprise App Manager API Docs

#### Content

https://github.com/plotly/streambed/issues/15071
https://github.com/plotly/streambed/issues/13540
https://github.com/plotly/streambed/issues/13692
