## Description
HTTPSMonitor is a tool written in Python and Golang to check the HTTPS status and SSL certificates of domains in a list. The tool performs the following main functions:

HTTPS Check: Determines whether the domain supports HTTPS.
SSL Certificate Check: If the domain supports HTTPS, it checks whether the SSL certificate is expiring within the next 7 days.
Telegram Notification: Sends notifications to a Telegram group if the domain does not support HTTPS or if the certificate is about to expire.

## Run with golang

### Install lib
```
go get -u github.com/go-resty/resty/v2
go get -u github.com/rs/zerolog/log
go get -u github.com/joho/godotenv
```

### Complie file
- With linux, macos
```
go build -o httpsmonitor
```

- With windows
```
GOOS=windows GOARCH=amd64 go build -o httpsmonitor.exe .
```

### Run with python

### Install lib
```
pip install requests python-dotenv
```

### Run file
```
python httpsmonitor.py
```
