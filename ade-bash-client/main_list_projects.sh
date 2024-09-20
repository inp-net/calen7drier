#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <login_as_username>"
  exit
fi

LOCATION="$(dirname -- "$(readlink -f "${BASH_SOURCE}")")"
login_user=$1
query_uid=$2
read -p 'INP cas password: ' password

token=$($LOCATION/cas-get.sh $login_user $password)

>&2 echo "warning: this script doesn't check if authentication actually succeed"
COOKIE=$token $LOCATION/ADE_list_projects.sh
