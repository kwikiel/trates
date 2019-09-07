#!/usr/bin/env bash

gcloud builds submit --tag gcr.io/airswap/trackato
gcloud beta run deploy trackato --image gcr.io/airswap/trackato --platform managed
