# InternshipFastAPI


## Running
The project is started using the command:
```shell
uvicorn src.main:app
```
To automatically restart the project when making changes during local development, you need to execute the command:
```shell
uvicorn src.main:app --reload
```

## Using Docker
Creating a Docker image:
```shell
docker build -t internimage .
```
Start the Docker Container:
```shell
docker build --name interncontainer -p 8000:8000 internimage
```
 Run using docker-compose:
```shell
docker-compose up --build web
```
