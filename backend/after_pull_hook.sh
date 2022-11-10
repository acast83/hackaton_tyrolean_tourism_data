#!/bin/sh

# cp after_pull_hook.sh .git/hooks/post-merge

cd ~/app/impresaone/v3
git branch -a | grep "*" | awk -F '*' '{print $2}' > src/svc_base/base/api/back_version.txt
date +"%Y-%m-%d %H:%M:%S" >> src/svc_base/base/api/back_version.txt



cat src/svc_base/base/api/back_version.txt
