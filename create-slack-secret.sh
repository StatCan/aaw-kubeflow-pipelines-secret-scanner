#!/bin/bash
#
# Create a secret with the slack webhook
# in a given namespace. E.g
#
# > this-script.sh monitoring
#
# Will prompt for webhook
# and will create a secret named `kfp-slack-webhook`
# `

set -e

NAMESPACE="$1"
WEBHOOK="$2"

if test -z "$NAMESPACE"; then
	echo "Error: No namespace provided." >&2
	echo "Please provide a namespace as an argument." >&2
	exit 1
fi

# Read Password
if test -z "$WEBHOOK"; then
	read -s -p "Slack Webhook: " webhook
	echo
fi

if test -z "$WEBHOOK"; then
	echo "Provided webhook was blank. Exiting." >&2
	exit 1
fi

kubectl create secret generic kfp-slack-webhook \
		--from-literal=SLACK_WEBHOOK=$WEBHOOK \
		--namespace $NAMESPACE
