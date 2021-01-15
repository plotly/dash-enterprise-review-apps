#!/bin/sh
set -eux

echo '-----> Project directory'
pwd
ls -al

echo '-----> Creating ssh key'
echo "$SSH_PRIVATE_KEY" | tr ',' '\n' > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa # permissioning
eval "$(ssh-agent -s)" # setting ssh environment variable in shell

echo '-----> Adding keys to ssh-agent'
ssh-add ~/.ssh/id_rsa

echo '-----> Creating ssh config'
echo "$SSH_CONFIG" | tr ',' '\n' > ~/.ssh/config

echo '-----> Adding git remote'
git config remote.plotly.url >&- || git remote add plotly dokku@dash-playground.plotly.host:aa-tngo-ci-qa # add remote if remote doesn't exist
git branch
echo '-----> Deploying app'
git push plotly HEAD:master