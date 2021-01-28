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

- [ ] Add error handling & retrying. If an API call fails, try it again. Explicitly check for status code != 200

Part 5 - Documentation

---

## Dash Enterprise App Manager API Docs

#### Content

https://github.com/plotly/streambed/issues/15071
https://github.com/plotly/streambed/issues/13540
https://github.com/plotly/streambed/issues/13692

- Schema: Provides "root" type for each operation
  - query: Fetchs data
  - mutation: updates data
    - updateSshKeys
    - changePassword
    - resetApiKey
    - addApp
    - updateApp
    - uploadAppThumbnail
    - addCollaborators
    - removeCollaborators
    - deleteApp
#### Format

- Examples
  - Increase JSON indentation from 2 to 4


#### ?

- Sandbox - changes are made directly to server
- Field Names
  - addApp vs initiateApp/createApp
  - current vs currentUserType/userType
- Filtering
- Errors
  - "Invalid app name. Names should be between 3 to 30 characters long, start with a letter, and only contain lower case letters, numbers, and -"
  - "401 Unauthorized: The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required." [BLOCKING]
  - Passing query f'string as variable in function
    - use `.format`

#### Errors

---------------------------------------------------------------------------
RemoteDisconnected                        Traceback (most recent call last)
~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/connectionpool.py in urlopen(self, method, url, body, headers, retries, redirect, assert_same_host, timeout, pool_timeout, release_conn, chunked, body_pos, **response_kw)
    698             # Make the request on the httplib connection object.
--> 699             httplib_response = self._make_request(
    700                 conn,

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/connectionpool.py in _make_request(self, conn, method, url, timeout, chunked, **httplib_request_kw)
    444                     # Otherwise it looks like a bug in the code.
--> 445                     six.raise_from(e, None)
    446         except (SocketTimeout, BaseSSLError, SocketError) as e:

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/packages/six.py in raise_from(value, from_value)

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/connectionpool.py in _make_request(self, conn, method, url, timeout, chunked, **httplib_request_kw)
    439                 try:
--> 440                     httplib_response = conn.getresponse()
    441                 except BaseException as e:

/usr/lib/python3.8/http/client.py in getresponse(self)
   1346             try:
-> 1347                 response.begin()
   1348             except ConnectionError:

/usr/lib/python3.8/http/client.py in begin(self)
    306         while True:
--> 307             version, status, reason = self._read_status()
    308             if status != CONTINUE:

/usr/lib/python3.8/http/client.py in _read_status(self)
    275             # sending a valid response.
--> 276             raise RemoteDisconnected("Remote end closed connection without"
    277                                      " response")

RemoteDisconnected: Remote end closed connection without response

During handling of the above exception, another exception occurred:

ProtocolError                             Traceback (most recent call last)
~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/requests/adapters.py in send(self, request, stream, timeout, verify, cert, proxies)
    438             if not chunked:
--> 439                 resp = conn.urlopen(
    440                     method=request.method,

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/connectionpool.py in urlopen(self, method, url, body, headers, retries, redirect, assert_same_host, timeout, pool_timeout, release_conn, chunked, body_pos, **response_kw)
    754 
--> 755             retries = retries.increment(
    756                 method, url, error=e, _pool=self, _stacktrace=sys.exc_info()[2]

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/util/retry.py in increment(self, method, url, response, error, _pool, _stacktrace)
    530             if read is False or not self._is_method_retryable(method):
--> 531                 raise six.reraise(type(error), error, _stacktrace)
    532             elif read is not None:

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/packages/six.py in reraise(tp, value, tb)
    733             if value.__traceback__ is not tb:
--> 734                 raise value.with_traceback(tb)
    735             raise value

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/connectionpool.py in urlopen(self, method, url, body, headers, retries, redirect, assert_same_host, timeout, pool_timeout, release_conn, chunked, body_pos, **response_kw)
    698             # Make the request on the httplib connection object.
--> 699             httplib_response = self._make_request(
    700                 conn,

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/connectionpool.py in _make_request(self, conn, method, url, timeout, chunked, **httplib_request_kw)
    444                     # Otherwise it looks like a bug in the code.
--> 445                     six.raise_from(e, None)
    446         except (SocketTimeout, BaseSSLError, SocketError) as e:

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/packages/six.py in raise_from(value, from_value)

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/urllib3/connectionpool.py in _make_request(self, conn, method, url, timeout, chunked, **httplib_request_kw)
    439                 try:
--> 440                     httplib_response = conn.getresponse()
    441                 except BaseException as e:

/usr/lib/python3.8/http/client.py in getresponse(self)
   1346             try:
-> 1347                 response.begin()
   1348             except ConnectionError:

/usr/lib/python3.8/http/client.py in begin(self)
    306         while True:
--> 307             version, status, reason = self._read_status()
    308             if status != CONTINUE:

/usr/lib/python3.8/http/client.py in _read_status(self)
    275             # sending a valid response.
--> 276             raise RemoteDisconnected("Remote end closed connection without"
    277                                      " response")

ProtocolError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

During handling of the above exception, another exception occurred:

ConnectionError                           Traceback (most recent call last)
<ipython-input-23-066fd0c31230> in <module>
     41     """.format(page = page))
     42 
---> 43     api_call =  client.execute(gql(query_string))
     44     page = 1 + page
     45     apps = api_call["apps"]["apps"]

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/gql/client.py in execute(self, document, *args, **kwargs)
     74             self.validate(document)
     75 
---> 76         result = self._get_result(document, *args, **kwargs)
     77         if result.errors:
     78             raise Exception(str(result.errors[0]))

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/gql/client.py in _get_result(self, document, *args, **kwargs)
     82     def _get_result(self, document, *args, **kwargs):
     83         if not self.retries:
---> 84             return self.transport.execute(document, *args, **kwargs)
     85 
     86         last_exception = None

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/gql/transport/requests.py in execute(self, document, variable_values, operation_name, timeout)
    113 
    114         # Using the created session to perform requests
--> 115         response = self.session.request(self.method, self.url, **post_args)  # type: ignore
    116         try:
    117             result = response.json()

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/requests/sessions.py in request(self, method, url, params, data, headers, cookies, files, auth, timeout, allow_redirects, proxies, hooks, stream, verify, cert, json)
    540         }
    541         send_kwargs.update(settings)
--> 542         resp = self.send(prep, **send_kwargs)
    543 
    544         return resp

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/requests/sessions.py in send(self, request, **kwargs)
    653 
    654         # Send the request
--> 655         r = adapter.send(request, **kwargs)
    656 
    657         # Total elapsed time of the request (approximately)

~/Repos/plotly/dash-enterprise-ci-qa/venv/lib/python3.8/site-packages/requests/adapters.py in send(self, request, stream, timeout, verify, cert, proxies)
    496 
    497         except (ProtocolError, socket.error) as err:
--> 498             raise ConnectionError(err, request=request)
    499 
    500         except MaxRetryError as e:

ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))


* Exception: {'message': 'Bad API key', 'locations': [{'line': 2, 'column': 3}], 'path': ['apps']}
* Exception: {'message': 'No such user', 'locations': [{'line': 2, 'column': 3}], 'path': ['apps']}
* ConnectionError: HTTPSConnectionPool(host='dash-playground.plotlwy.host', port=443): Max retries exceeded with url: /Manager/graphql (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7fbd803e14f0>: Failed to establish a new connection: [Errno -2] Name or service not known'))
* HTTPError: 405 Client Error: METHOD NOT ALLOWED for url: https://dash-playground.plotly.host/Manager/grapwhql