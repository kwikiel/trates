#!/usr/bin/env bash

gcloud builds submit --tag gcr.io/airswap/trackato
gcloud beta run deploy trackato --image gcr.io/airswap/trackato --platform managed

response=$(curl --write-out %{http_code} --silent --output /dev/null https://trackato.com/)

echo "Pings the endpoint to warmup. It should return 200 status code"
echo $response

