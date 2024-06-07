[![Plotly](https://circleci.com/gh/plotly/dash-enterprise-review-apps.svg?style=shield)](<LINK>)

# Review Apps

<div align="center">
  <a href="https://dash.plotly.com/project-maintenance">
    <img src="https://dash.plotly.com/assets/images/maintained-by-plotly.png" width="400px" alt="Maintained by Plotly">
  </a>
</div>


<p align="center">
  <img width="460" height="300" src="https://user-images.githubusercontent.com/11036740/110763533-fe7af480-821f-11eb-9103-829e5ebb6a12.png">
</p>

Review apps are "pre-release" versions of your Dash apps automatically
created by your CI platform when making a pull request.

These apps inherit the configuration options of their production equivalent,
ensuring parity between environments for testing. Review apps enable you to
quickly deploy and share proposed changes with the rest of your team before
merging them into production. The review apps are deleted once those changes
go live.

## Requirements

To get started you will need:

* Dash Enterprise Server instance
* Deployed Dash app
* Repository containing your Dash app's source code
    (e.g. GitHub, GitLab, Bitbucket)
* CI platform (e.g. GitHub Actions, GitLab CI/CD, Bitbucket Pipes & 
    Deployment, CircleCI)
* CI pipeline for your app's repository
* CI platform configuration file
* Review app scripts

## Quick start guide

1. Designate a *service account* with admin privileges on Dash Enterprise.
2. Generate an SSH key *without a passphrase*, and add the public key to
    Dash Enterprise.
3. Generate an API key for the *service account* and all developer accounts that will push changes to the app repository.
4. Add the private SSH key, and Dash Enterprise service and developer API keys as environment variables on your CI platform.
5. Add your CI platform configuration file to the root of your project folder. For example, in CircleCI this file would be `.circleci/config.yml`.
6. Copy the `.review-apps` folder from this repository to the root your project folder.
7. In your `.review-apps` folder, update the specified variables in the `settings.py`.
8. Set up your CI configuration to run the Review App scripts. See [`.circleci/config.yml`](https://github.com/plotly/dash-enterprise-review-apps/tree/main/.circleci) for an example using CircleCI's configuration.


See [Review Apps](https://dash.plotly.com/dash-enterprise/review-apps) for more detailed instructions.

## Basic Usage

After setting up, review apps will get automatically created anytime you make a pull request from your review app branch. When pull request are merged, those approved changes get deployed to your main app branch.

1. In your app's repository, create and checkout a new branch.
2. Make changes to your apps source code on your review app branch.
3. Commit and push those changes.

