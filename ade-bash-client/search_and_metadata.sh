if [ "$#" -ne 1 ]; then
  echo "usage: $0 <query_string>"
  exit
fi

./ADE_search.sh "$1" | xargs -P 8 -I % bash -c 'echo % - $(./get_calendar_name.sh %)'
