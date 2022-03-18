#!/usr/bin/env bash

HOST="http://app:9000"
CURL_CMD="curl -s -k"

ERR_A_OK=0
ERR_MODEL_DOES_NOT_EXIST=1
ERR_INVALID_DATA=2
ERR_MALFORMED_DATA=3

# wait for app container to respond
VALID="7"
while [ "$VALID" -gt "0" ]; do
    $CURL_CMD "${HOST}/" 2>&1 > /dev/null
    VALID="$?"
done

output=""

for x in $($CURL_CMD "${HOST}/widgets/" |jq '.widgets[].id') ; do
  $CURL_CMD -X delete "${HOST}/widgets/$x/"
done


VALID_WIDGETS_TO_ADD=(
  '{"name":"Basic, Valid, Test Widget 1", "parts_count": 1111}'
  '{"name":"Basic, Valid, Test Widget 2", "parts_count": 1112}'
  '{"name":"Basic, Valid, Test Widget ̛", "parts_count": 1113}' # utf8 name
  '{"name":"Basic, Valid, Test Widget 4", "parts_count": 1114, "extra": "Im so fancy"}' # extra keys
)

for wta in "${VALID_WIDGETS_TO_ADD[@]}"; do
  output="$($CURL_CMD -X put -d "${wta}" ${HOST}/widgets/)"
  if [ "$(echo $output | jq '.error_number')" -ne "${ERR_A_OK}" ] ; then
    echo "invalid response for ${wta}"
    exit 1
  else
    id="$(echo $output | jq '.widgets[0].id')"
    del_output="$($CURL_CMD -X delete ${HOST}/widgets/{$id}/)"
    if [ "$(echo $output | jq '.error_number')" -ne "${ERR_A_OK}" ] ; then
      echo "invalid response when trying to delete ${id}"
      exit 2
    fi
  fi
done

### assert failures
# name too long
output="$($CURL_CMD -X put -d '{"name":"Test Widget from Curl with a super long name that should be too long for the model", "parts_count": 52}' -s ${HOST}/widgets/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_INVALID_DATA}" ] ; then
  echo "invalid response for name too long"
  echo $output
  exit 3
fi
# missing name
output="$($CURL_CMD -X put -d '{"parts_count": 51}' -s ${HOST}/widgets/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_INVALID_DATA}" ] ; then
  echo "invalid response for missing name"
  echo $output
  exit 4
fi
# missing parts_count
output="$($CURL_CMD -X put -d '{"name": "missing parts_count"}' -s ${HOST}/widgets/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_INVALID_DATA}" ] ; then
  echo "invalid response for missing parts_count"
  echo $output
  exit 5
fi
# malformed json
output="$($CURL_CMD -X put -d '{"malformed_json", "name": "A Name", "parts_count": 3}' -s ${HOST}/widgets/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_MALFORMED_DATA}" ] ; then
  echo "invalid response for missing parts_count"
  echo $output
  exit 6
fi
# missing widget (get)
# this could cause a false failure if a widget with the given id exists, but it's unlikely
output="$($CURL_CMD ${HOST}/widgets/9999999/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_MODEL_DOES_NOT_EXIST}" ] ; then
  echo "invalid response for get missing widget"
  echo $output
  exit 7
fi
# missing widget (delete)
# this could cause a false failure if a widget with the given id exists, but it's unlikely
output="$($CURL_CMD -X delete ${HOST}/widgets/9999999/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_MODEL_DOES_NOT_EXIST}" ] ; then
  echo "invalid response for delete missing widget"
  echo $output
  exit 8
fi
# patch non-existent widget
# this could cause a false failure if a widget with the given id exists, but it's unlikely
output="$($CURL_CMD -X patch -d '{"parts_count":5}' ${HOST}/widgets/9999999/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_MODEL_DOES_NOT_EXIST}" ] ; then
  echo "invalid response for update missing widget"
  echo $output
  exit 9
fi


output="$($CURL_CMD -X put -d '{"name":"Basic, Valid, Volatile, Test Widget 5", "parts_count": 1115}' ${HOST}/widgets/)"
id="$(echo $output | jq '.widgets[0].id')"

output="$($CURL_CMD -X patch -d '{"name":"Edited, Volatile, Test Widget 5"}' ${HOST}/widgets/${id}/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_A_OK}" ] ; then
  echo "invalid response for update missing widget"
  echo $output
  exit 10
fi

output="$($CURL_CMD -X patch -d '{"parts_count":5}' ${HOST}/widgets/${id}/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_A_OK}" ] ; then
  echo "invalid response for update missing widget"
  echo $output
  exit 11
fi

output="$($CURL_CMD -X patch -d '{"extra":"ordinary"}' ${HOST}/widgets/${id}/)"
if [ "$(echo $output | jq '.error_number')" -ne "${ERR_A_OK}" ] ; then
  echo "invalid response for update missing widget"
  echo $output
  exit 12
fi

$CURL_CMD -X delete ${HOST}/widgets/{$id}/ 2>&1 > /dev/null

# vim: set ts=4 sw=4 et ai:
