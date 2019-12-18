
#kubectl create namespace dev
#--namespace=dev 

kubectl create secret docker-registry gcr-json-key --docker-server=https://gcr.io --docker-username=_json_key --docker-email=naanyaar@gmail.com --docker-password='{
  "type": "service_account",
  "project_id": "prj-nyc-taxis-with-kafka",
  "private_key_id": "348d29dd29f5170e096504596a0f06db02ff6790",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDTXStTAuByyYNQ\nZTYI2wpibRZBraMFXbmzL8t9lHszxtsOqPXwzzH/GixP7+Jm3pBhfo94GpHRfmA3\nb5yWArzcF+eI3soLslbz/fyWFJUPMCEiuk76305z9nmSj8HEDbWc4C5JlMB6xCtR\nzIccAwEEiD1gXACPjHqqXtV8+pambLDgA7SZ3lfV6R7kqp1Jr3lFLFL35BCWxZ71\no9RgPj09pZFEVK4JKP15EpIPcD2tsTL2+beXy1tKBz+sipkV1xHaXnbIxGWvkcpr\nzZQoyNvZVuWee5tNJsv+mjt8tWMUVIJ0rOfgTSuh3PwkcRWql4TjbSzOGtaV+Wc+\n+UqiwtvBAgMBAAECggEAIV+77bVtvleTp01L58BlFongsp8vDLOyFO6Y5CvepkbM\neQyfGkEvxPbw2fBn9dPyb/UyxIVMKAxF4gr6v8m6i3WE0YeoLIpM5jrhDXY+MRyU\nPC5h4TADFxbAjIQBgFT6gRpO2hR7A1zX9ZMPdGdZsPRYM0+4+5xJaX8O7lcyaXWa\nI80elRbUr1iWPoxSKXPs15exlAJmBnjXefKmTri2IYzFsRXBMyTzGVayLCTLoY/c\nOW3PmkIxOGDB7aM98rnV8kwaQG5WLRLjq/+Ifr5Ai17l+B0kNOX9cS+QgG7PG+6f\nLArWtP3NvuWFMwYPraaqDbB43XpLnOqQbYoQpeS6fwKBgQD48uuBOICgovW8IyHe\nRud6FOCArPMU/iPeIAFoWD42JnDONWwaD7lx/6aZbjbX/dNLHazBp6SOLs4jdkpb\nrLtyyY607VOcAynL1uVeE0Jvc4i8Itut248TgYRf9Ut9mHCyA97VvwX2AUty7m7h\nG0wgqJtEw5IQSCSqn0SJyMzFGwKBgQDZWbpgxUmqmCup/ec2vlGjwhe763mwGeDV\nhGKo9BS0YwuABikcLgbGTMT21xbgNoP7UbtV7kKQCYPOIYg+att5S27J5XyGDXAe\ngW7C0Mt/w9jCHspChOE9XjthqHT0HXLJ8mG8818DvJleFhOvunem90p8SwYoARQ4\nWhAPJXAcUwKBgQCYi1Gfpt26kOB+3hA8wbnJZs2CS3fQH0IfNAFozNmiGL/6u2V4\nOrZpkjulvJFCnLhCSPa4217L+QY7WJqLvjZGShd16g7XhGCyFQYLNUX6QRNCJSHz\nUJxFWZGhsw8E8Mntas26sAiZC4YN8Ohka3Okd2xdIHF6JJrDKkC3JSHEjQKBgDp6\nouPgkRZ+RNlDAE/BWzPlR/9+tsoD3HN2YBk3Os7iCzkR70OuupHmG+SSMIx4/n/D\nGNVg+rXIaZcvfHnWxGBZRGC8BwoGWZFLn+J4zRf+OLbaE+9b00JwtSdsbLM1rSna\ntiNhk8Hsn5Mp+3f/gqwAwyC4Ctr+l1MmIEYC+6wTAoGAB9lIkPw6ODawrOpqu5rT\ncJ2ktY4k05RE99PbwEV+BWrTHCt8DGs4e83kym0ePVYLCf6MTBkLuMl8f9a55QAf\n3rb8V3Amx65zQAGdIhVRsoxhGtmtbqJ4v0kJUtYbL+8dcEhyFg8hsVw8lH2FgYqM\nPvdpSELn2o6u6kfw+te+pYA=\n-----END PRIVATE KEY-----\n",
  "client_email": "srv-acc-prj-nyc-taxis-with-kaf@prj-nyc-taxis-with-kafka.iam.gserviceaccount.com",
  "client_id": "112773127090078380317",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/srv-acc-prj-nyc-taxis-with-kaf%40prj-nyc-taxis-with-kafka.iam.gserviceaccount.com"
}'

kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "gcr-json-key"}]}'

rc=$?;
while [[ $rc != 0 ]]
do
  echo Waiting for service accounts to be ready
  sleep 15
  kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "gcr-json-key"}]}'
  rc=$?;
done


