#!/bin/sh

echo '-----> Project directory'

pwd
ls -al

echo '-----> Formatting ssh key'
echo "$SSH_PRIVATE_KEY" | tr ',' '\n' > /home/circleci/.ssh/id_rsa
chmod 600 /home/circleci/.ssh/id_rsa
eval "$(ssh-agent -s)" # setting ssh environment variable in shell

echo '-----> Adding keys to ssh-agent'
ssh-add /home/circleci/.ssh/id_rsa

echo '-----> Formatting ssh config'
echo "$SSH_CONFIG" | tr ',' '\n' > /home/circleci/.ssh/config
cat /home/circleci/.ssh/config

echo '-----> Adding git remote'
git config remote.plotly.url >&- || git remote add plotly dokku@dash-playground.plotly.host:aa-tngo-ci-qa

echo '-----> Deploying app'
git push plotly HEAD:master