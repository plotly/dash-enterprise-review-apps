# Adding Environment Variables to CircleCI


## Required Environment Variables

To automate Dash app deployment with CircleCI, you will need to include the
 following environment variable secrets to your **Project Settings** page:

- SSH Config
  - Contains your SSH config file settings.
- Private and Public Service SSH keys
  - The **administrative account** associated with these keys is responsible for deploying review apps, and merging those app's into their respective main or master branch after approval.
- Service API Key
  - Contains your Dash Enterprise Service API key
- User1/User2/User3... API Keys
  - You must add an API key **for each developer account** deploying apps on the server.

> Multi-line environment variables **should be base64 encoded**
> before pasting them in the CircleCI dashboard. See [CircleCI Docs on Multi-line Environment variables](https://support.circleci.com/hc/en-us/articles/360046094254-Using-Multiple-Line-newline-Environment-Variables-in-CircleCI) for more information.

----------

### SSH Config

**config**
```sh
Host <your-dash-host-name>
    User admin
    HostName <your-dash-enterprise-host>
    Port 3022
    IdentityFile ~/.ssh/id_rsa_service

```

```sh
cat config | base64 -w 0
```

```sh
SG9zdCBkZS10b2Jpbm5nby1xYQogICAgVXNlciB0b2Jpbm5nbwogICAgSG9zdE5hbWUgcWEtZGUtNDEwLnBs[...]Lmhvc3QKICAgIFBvcnQgMzAyMgogICAgSWRlbnRpdHlGaWxlIH4vLnNzaC9hZG1pbl9xYV9kZV80MTBfcGxvdGx5X2hvc3QKICAgIFN0cmljdEhvc3RLZXlDaGVja2luZyBubwogICAgVXNlcktub3duSG9zdHNGaWxlIC9kZXYvbnVsbAoK
```

----------

### Private Service SSH Key

**id_rsa_service**

```sh
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjE[...]AAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAACFwAAAAdzc2gtcn
mCj/GR/a7en/4uU7PkJu1jsVRhnTAKbMSyf09ASUeUwBYBZG/MbXtOBQVZBHis8fAutVDG
QuFxV5Z4Mf3JlOr1wnucW+qCLkh4/ECFLOF/0RXDI2+OoZtzCqFkjuBa8wOQs8uli+3/vZ
NYwrH6xc2WjVAAAAG2FkbWluX3FhX2RlXzQxMF9wbG90bHlfaG9zdAECAwQFBgc=
-----END OPENSSH PRIVATE KEY-----

```

```sh
$cat id_rsa_service | base64 -w 0
```

```sh
LS0tLS1CRUdJTiBPUEV[...]OU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1SDZ4YzJXalZBQUFBRzJGa2JXbHVYM0ZoWDJSbFh6UXhNRjl3Ykc5MGJIbGZhRzl6ZEFFQ0F3UUZCZ2M9Ci0tLS0tRU5EIE9QRU5TU0ggUFJJVkFURSBLRVktLS0tLQo=
```

----------

### Public Service SSH Key

**id_rsa_service.pub**

```sh
ssh-rsa AAAAB3NzaC1[...]yc2EAAAADAQABAAACAQDD+kQvfxUYgCoqoVk9qNmk1i60AKzIzGOFqCLd56rz7P2Gh/O/ybaHf2Qzg1horc8BvQxfB0o9POaaPy80WZg5IkBtOQlLoJJD+ohlQcvpqN1odEAJnmOQ== service_account

```


```sh
$cat id_rsa_service.pub | base64 -w 0
```


```sh
c3NoLXJzYSBBQUFBQjN[...]OemFDMXljMkVBQUFBREFRQUJBQUFDQVFERCtack5pRnFaVWgxVlBYR3ZUdFpJWkhKVXoyMzh5OGJBdlhJOGdLT1FGbG9xODBXWmc1SWtCdE9RbExvSkpEK29obFFjdnBxTjFvZEVBSm5tT1E9PSBhZG1pbl9xYV9kZV80MTBfcGxvdGx5X2hvc3QK
```

----------

### Service API Key

```sh
7ktJXalZBQUFBRzJGaOB
```

----------
## Adding Environment Variables

1. Navigate to your CircleCI Project Settings page:

https://app.circleci.com/settings/project/<your-git-platform>/<your-org>/<your-repo>/environment-variables

TK add variables page asset (add variable)

1. Click on **Add Environment Variable**, a modal will appear.

TK add variable modal (empty)

3. Fill out the **Name*** field with your environment variable's name and the **Value*** field, with its value.

TK add variable modal (full)

4. Click on **Add Environment Variable** to confirm.

TK add variable modal (confirm)

