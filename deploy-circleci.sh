#!/bin/sh
set -eux

echo '-----> Project directory'
pwd
ls -al

echo '-----> Formatting ssh key'
echo "$SSH_PRIVATE_KEY" | tr ',' '\n' > ~/circleci/.ssh/id_rsa
chmod 600 ~/circleci/.ssh/id_rsa # permissioning
eval "$(ssh-agent -s)" # setting ssh environment variable in shell

echo '-----> Adding keys to ssh-agent'
ssh-add ~/circleci/.ssh/id_rsa

echo '-----> Formatting ssh config'
echo "$SSH_CONFIG" | tr ',' '\n' > ~/circleci/.ssh/config
cat ~/circleci/.ssh/config

echo '-----> Adding git remote'
git config remote.plotly.url >&- || git remote add plotly dokku@dash-playground.plotly.host:aa-tngo-ci-qa # add remote if remote doesn't exist
git remote -v

echo '-----> Deploying app'
git push plotly HEAD:master