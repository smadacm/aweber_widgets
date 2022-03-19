#!/usr/bin/env bash

HOST="http://app:9000"
CURL_CMD="curl -s -k"

ERR_A_OK=0
ERR_MODEL_DOES_NOT_EXIST=1
ERR_INVALID_DATA=2
ERR_MALFORMED_DATA=3

# install curl and jq (or don't and just continue on)
if [ -z "$(which curl)" ] ; then 
    apk add --no-cache curl jq
fi

# wait for app container to respond
VALID="7"
while [ "$VALID" -gt "0" ]; do
    $CURL_CMD "${HOST}/" 2>&1 > /dev/null
    VALID="$?"
done


# test basic creation of widgets
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


run_test() {
    local failure_exit_code="$1"
    local failure_exit_message="$2"
    local expected_error_number="$3"
    local verb="$4"
    local path="$5"
    local data="$6"

    local params="-X ${verb}"

    if [ ! -z "${data}" ] ; then
        params="${params} -d @-"
        local actual_error_number="$(echo ${data} |$CURL_CMD ${params} ${HOST}${path} | jq '.error_number')"
    else
        local actual_error_number="$($CURL_CMD ${params} ${HOST}${path} | jq '.error_number')"
    fi

    if [ "${actual_error_number}" != "${expected_error_number}" ] ; then
      echo "${failure_exit_message}"
      echo "expected ${expected_error_number}, but got ${actual_error_number}"
      exit ${failure_exit_code}
    fi
}

### assert failures
run_test 3 "invalid response for name too long" "${ERR_INVALID_DATA}" "put" "/widgets/" \
    '{"name":"Test Widget from Curl with a super long name that should be too long for the model", "parts_count": 52}'
run_test 4 "invalid response for missing name" "${ERR_INVALID_DATA}" "put" "/widgets/" '{"parts_count": 51}'
run_test 5 "invalid response for missing parts_count" "${ERR_INVALID_DATA}" "put" "/widgets/" '{"name": "missing parts_count"}'
run_test 6 "invalid response for missing parts_count" "${ERR_MALFORMED_DATA}" "put" "/widgets/" '{"malformed_json", "name": "A Name", "parts_count": 3}'

# these tests could cause a false failure if a widget with the given id exists, but it's unlikely
run_test 7 "invalid response for get missing widget" "${ERR_MODEL_DOES_NOT_EXIST}" "get" "/widgets/99999999/"
run_test 8 "invalid response for delete missing widget" "${ERR_MODEL_DOES_NOT_EXIST}" "delete" "/widgets/99999999/"
run_test 9 "invalid response for update missing widget" "${ERR_MODEL_DOES_NOT_EXIST}" "patch" "/widgets/99999999/"


# create test widget for next few tests
output="$($CURL_CMD -X put -d '{"name":"Basic, Valid, Volatile, Test Widget 5", "parts_count": 1115}' ${HOST}/widgets/)"
id="$(echo $output | jq '.widgets[0].id')"

run_test 10 "invalid response for update widget name" "${ERR_A_OK}" "patch" "/widgets/${id}/" '{"name":"Edited, Volatile, Test Widget 5"}'
run_test 11 "invalid response for update widget parts_count" "${ERR_A_OK}" "patch" "/widgets/${id}/" '{"parts_count":5}'
run_test 12 "invalid response for update widget without name or parts_count" "${ERR_A_OK}" "patch" "/widgets/${id}/" '{"extra":"ordinary"}'

# delete test widget
$CURL_CMD -X delete ${HOST}/widgets/{$id}/ 2>&1 > /dev/null

echo "Tester done. No errors found."

# vim: set ts=4 sw=4 et ai:
