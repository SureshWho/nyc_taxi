
#kubectl create namespace dev
#--namespace=dev 

kubectl create secret docker-registry gcr-json-key --docker-server=https://gcr.io --docker-username=_json_key --docker-email=naanyaar@gmail.com --docker-password='{
  "type": "service_account",
  "project_id": "prj-nyc-taxis",
  "private_key_id": "9877814e83d5774f6f6e92794ea82ced379ee8d2",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDe0KeVj/B6XQCz\nH0IZLWgUC37lg8DuxoGEaSRjrlNnP4h4WCIHMGPCYflhODkIG4MUumOXnbqJUIB4\n9Jmyxq7SHgFWhYzuxQvMRKckaMHeCt39g/QKkkejzNdpfP8S3Fve0xbLCUbEgOhS\nqad6OCX/8DWOxsVq/fgxVSQs6Ip5lizuT7XxAv2isihUC2F+lsezgukP7q9W6XyB\nemEVGF0pAs8OxahRgYqvfQt8QfsyunJp3BF7ry2qqJsKE5CMbTx6NAL6djBH9b8s\n5gEIcs3UEht29EmVXq9mPc/MdCCiHF03YvTQlYKPn+nCFumSFOtfnYhXRzhX2xXz\nq71928iVAgMBAAECggEAAYTnrO/gd7JxokcDctt/Ov/Bu5E0kWGIxDKD/SqqRpPF\ne5iSPCf6ziT6h8ypKuJ7zXo12p9IhHjS32rqL1tbxB1Ql1qYFZACCWsAaWb4x2md\n44Vw9lon+I3EJuPOHhP4NmKMZGb+9LEHpHn5T9kufSUR9b6/iCq3dKf8HqhD5W9Q\nQu4nXe1HR+I6Mew+HPxDWihvcmeSo+Y/D6r1utivma+bab5ZS2RhHhKk/l/4gXj4\nEGYQf/A8yV8QYYaaH2+4geYbElHMAACzqgg0o3LzmDj90JR5sXe6Qg4VwKwX3auu\ngyLpSvWaGy17vF5H8btqgZw4lZ4ujEEquk+blethMQKBgQD5Yhd+AQjtIEy6EzIy\nvbvEPmGRpcG9c0TrhZ2HOFe6hMbCDwUxJxoLncIdfJf2p+2uRiZ7dl/v1NCXEa4c\nGmBa18zi+sGBP0KZp04TcPEvtyXpL36ID/F1b/Jtj7l88RDc/fSfiFHO70XRPshr\ni9DWwSE4fi/7i/1qhFLiSGPhfQKBgQDkuhoQvdvFjgp7cKCiQdVgmjSR2U+UtcdY\nmbCzA8Jic8yoD0L5XfaHsMGr0LR+guORCM3NZsLXsplsML5Elak5sz05J5lh5mZg\nBEiTjgBmJ0gIgq/AN44KP26JnxLAeQ/6vhsb+AU3POYhADGSWwrwOTwg9fdYbbA6\nZCyDocUu+QKBgQDADbn30QY1z8UnG/dxukqrVDtBtnyg0O/HzevGIi71tqF2+6hM\n9UcKoSDIIpbJXwQdTWr/c+doROWrIfOLMwj3jO/98Y0qYzSALqdjM3ya+ZoZnfj9\nAgI7Jc52b9Qyk1ggSPemEI6oJf8HqSkiIdfgO3XBEvUS7PlpmaRXHdbF5QKBgAqn\ntMEk5xEL7ecUNxd386W9aUeGFRP7Z97zweyE91A4zsbhdyBAxVRK4qrLXS0rkchW\n3ad86wS7WDRXDPYK9sguVmLMOnP6FLjSWkMtcU1Q9SUYWXGd5OsLS23z0B7RRPJM\nWtzxr+SD3MCazrRfs2G/eNKcQrqG2ZfOxNgY+COZAoGBAKcyiAoKPa/vUhEMfN18\nEbV8Eq9FlyA/t90U1iUWDgBahE3BXJMT2tZBvFZLJC3/CM3wGC0yqwHNLDmsFEiG\nwHlhKLu1mbA5MNMVRbzTRyTDQW+AsppfaG4jIvtL4YxCV+r8W973GfOHf0H2WACO\nfKbe/CqC0m0fwCIZNgg0jStI\n-----END PRIVATE KEY-----\n",
  "client_email": "pubsubfull@prj-nyc-taxis.iam.gserviceaccount.com",
  "client_id": "117556244767918619367",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/pubsubfull%40prj-nyc-taxis.iam.gserviceaccount.com"
}'


kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "gcr-json-key"}]}'

rc=$?; if [[ $rc != 0 ]]; then echo "Waiting for service accounts to be ready"; sleep(15) fi

