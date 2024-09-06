#!/bin/bash

# App name
app_name="nginxadminui"
username="joyte"

# Push to github
git push

# Get the latest tag
latest_tag=$(git log -n1 --format="%h")

# Docker build with :latest and :$latest_tag
docker build -t $username/$app_name:latest -t $username/$app_name:$latest_tag .

# Docker push both tags
docker push $username/$app_name:latest
docker push $username/$app_name:$latest_tag

# Done