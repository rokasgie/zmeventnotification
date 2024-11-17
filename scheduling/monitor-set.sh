#!/bin/bash
# Path to the .ini file
config_file="/etc/zm/zmeventnotification.ini"

# Extract the path to the actual config file from the secrets file
secrets_file=$(grep -oP '^\s*secrets\s*=\s*\K.*' "$config_file")

# Extract ZM_USER and ZM_PASSWORD from the .ini file
ZM_USER=$(grep -oP '^ZM_USER=\K.*' "$secrets_file")
ZM_PASSWORD=$(grep -oP '^ZM_PASSWORD=\K.*' "$secrets_file")
API_URL=$(grep -oP '^ZM_API_PORTAL=\K.*' "$secrets_file")

# Send POST request and capture response and HTTP status code
response=$(curl -s -w "%{http_code}" -X POST -d "user=$ZM_USER" -d "pass=$ZM_PASSWORD" $API_URL/host/login.json)
# Extract the HTTP status code (last 3 characters of response)
http_status="${response: -3}"

# Extract the JSON body (everything except the last 3 characters)
json_response="${response::-3}"

# Check if the HTTP status is 200
if [ "$http_status" -eq 200 ]; then
    access_token=$(echo "$json_response" | jq -r '.access_token')
else
    echo "Failed to authenticate. HTTP status: $http_status"
    echo "Response: $json_response"
fi

monitor_function="$1"
shift
echo "Setting monitors $@ to $monitor_function"

# Loop through all provided monitor IDs
for monitor_id in "$@"; do
    monitor_response=$(curl -s -X POST "$API_URL/monitors/${monitor_id}.json" \
        -d "Monitor[Function]=$monitor_function&Monitor[Enabled]=1" \
        -d "token=$access_token")

    # Check if the response matches the expected output
    if [[ "$monitor_response" != '{"message":"Saved"}' ]]; then
        echo "Error: Unexpected response for monitor ID $monitor_id"
        echo "Response: $monitor_response"
        exit 1
    fi

    echo "Monitor ID $monitor_id updated successfully."
done
