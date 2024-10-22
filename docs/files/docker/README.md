# Web2Vec Docker usage

This sample demonstrates how to use the Web2Vec project in a Docker container.
It will run the [generate_dataset.py](generate_dataset.py) script that will process a list of websites, gather their
features and save them in a CSV file.

1. Install Docker
2. Clone this repository
3. Build the Docker image - [Dockerfile](.Dockerfile)

```bash
docker build -t web2vec .
```

4. Run the Docker container. It will run the [generate_dataset.py](generate_dataset.py) script that will process a list
   of websites, gather their features and save them in a CSV file.

```bash
docker run -it web2vec
```
