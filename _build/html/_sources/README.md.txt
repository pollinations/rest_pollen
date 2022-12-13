# rest-pollen

## Dev setup
1. Install node and [pollinations-ipfs](github.com/pollinations/pollinations-ipfs)
2. Install this repo
```sh
# Install dependencies
pip install -e ".[test]"

# Install pre-commit hooks
brew install pre-commit
pre-commit install -t pre-commit
```
3. Add your jwt secret to `.env`

### Start the server:
```
python rest_pollen/main.py
```

### Working with Docker
Build the image
```
docker build -t rest .
```
Start the dockererized backend:
```
docker run -p 5000:5000 --env-file .env rest
```

### Sending requests
```
python test/client.py
```

### Testing
```
pytest test --cov
```

### API docs
Start a server, then open the [openapi docs](http://localhost:5000/openapi.json). Can be viewed in [swagger editor](https://editor.swagger.io/).


todo
[] POST /pollen
    [x] accept arbitrary json
    [x] use pypollsdk to send request
    [x] return response
[] authentication
    [x] validate token
    [] make runModel accept a --token flag
[.] deployment
    [] deploy container
    [] 
[] make wedatanation endpoints work
    [] create clip index
    [] wedatanation-picker: download from index
