#!/usr/bin/env bash

# Dependencies: jq, pup, perl
# Usage: cas-get.sh username password

DEST="https://edt.inp-toulouse.fr/direct/myplanning.jsp"
ENCODED_DEST="https%3A%2F%2Fedt.inp-toulouse.fr%2Fdirect%2Fmyplanning.jsp"
CAS_HOSTNAME=cas.inp-toulouse.fr

# set -x  # debug: show commands in terminal

if [ "$#" -ne 2 ]; then
  echo "usage: $0 <username> <password>"
  exit
fi

#Temporary files used by curl to store cookies and http headers
COOKIE_JAR=$(mktemp)
HEADER_DUMP_DEST=$(mktemp)
trap "rm -f $COOKIE_JAR" EXIT
trap "rm -f $HEADER_DUMP_DEST" EXIT

CURL_PARAMS="--compressed -s -o /dev/null"  # debug to use mitmproxy: "--proxy localhost:8080 -k"

TEST=$(curl $CURL_PARAMS $COOKIE_JAR https://$CAS_HOSTNAME/cas/login?service=$ENCODED_DEST | pup '#fm1 input json{}' | jq '.[] | {(.name): .value}' | jq -s 'add' | jq ".username = \"$1\" | .password = \"$2\"")

#Authentication details. This script only supports username/password login, but curl can handle certificate login if required
USERNAME=$(echo "$TEST" | jq -r '.username')
PASSWORD=$(echo "$TEST" | jq -r '.password')
EXECUTION=$(echo "$TEST" | jq -r '.execution')

#The script itself is below

#Submit the login form, using the cookies saved in the cookie jar and the form submission ID just extracted. We keep the headers from this request as the return value should be a 302 including a "ticket" param which we'll need in the next request
curl $CURL_PARAMS --data-urlencode "username=$USERNAME" --data-urlencode "password=$PASSWORD" --data-urlencode "execution=$EXECUTION" --data-urlencode "_eventId=submit" -i -c $COOKIE_JAR https://$CAS_HOSTNAME/cas/login -D $HEADER_DUMP_DEST

#Pass ticket to actual service to validate cas authentication
CURL_DEST=`grep location $HEADER_DUMP_DEST | sed 's/location: //' | tr -d '\r'`
curl $CURL_PARAMS -I -b $COOKIE_JAR -c $COOKIE_JAR "$CURL_DEST"

#Moodle: Validate login and retrieve actual session cookie
curl $CURL_PARAMS -L -I -b $COOKIE_JAR -c $COOKIE_JAR "$DEST"

#Moodle: Test by downloading a random pdf file
#curl $CURL_PARAMS -b $COOKIE_JAR "https://moodle-n7.inp-toulouse.fr/pluginfile.php/80810/mod_resource/content/1/TD_Gestion_Processus.pdf" -o output.pdf

cat $COOKIE_JAR | sed -n "s/^.*JSESSIONID\t*//p" | tail -n 1
