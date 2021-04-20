#!/bin/bash
#
# Create a secret with elastic-search credentials
# in a given namespace. E.g
#
# > this-script.sh monitoring
#
# Will prompt for username and password, and the create
# a secret named `elastic-creds
# `

set -e

NAMESPACE="$1"
elk_user="$2"
elk_pass="$3"

if test -z "$NAMESPACE"; then
	echo "Error: No namespace provided." >&2
	echo "Please provide a namespace as an argument." >&2
	exit 1
fi

# Read Password
if test -z "$elk_user" || test -z "$elk_pass"; then
	read -s -p "Elastic User: " elk_user
	echo
	read -s -p "Elastic Password: " elk_pass
	echo
fi

if test -z "$elk_user" || test -z "$elk_pass"; then
	echo "Provided username or password were blank. Exiting." >&2
	exit 1
fi

kubectl create secret generic elastic-creds \
		--from-literal=ES_USER=$elk_user \
		--from-literal=ES_PASS=$elk_pass \
		--namespace $NAMESPACE
