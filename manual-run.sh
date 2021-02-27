#!/bin/sh

# Trigger a manual run.
# Add `-n namespace` if you need to pass the
# namespace.

kubectl create job $@ \
    --from=cronjob/kfp-secret-scanner \
    kfp-secret-scanner-$(date +'%Y%m%d-%M%S')
