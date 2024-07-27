#!/bin/bash

# Push to github
git push

# Get the latest tag
latest_tag=$(git log -n1 --format="%h")

# Docker build with :latest and :$latest_tag
docker build -t joyte/nginxadminui:latest -t joyte/nginxadminui:$latest_tag .

# Docker push both tags
docker push joyte/nginxadminui:latest
docker push joyte/nginxadminui:$latest_tag

# Done