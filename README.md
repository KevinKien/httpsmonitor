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
