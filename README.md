# Blockchain in Python with Docker
> One of the most spoken and trending technologies in the field of Computer Science is Blockchain. In simple words it is a chain of immutable blocks which can contain any records of information which we wanted to persist. And these blocks are connected with each other using hashes which makes it difficult to alter any block's information. Here, I have (tried to) demonstrate how we can implement Blockchain network using python and docker.

## Requirements

To run this project you need to have Docker and Postman installed on your machine.

https://docs.docker.com/get-docker/

https://www.postman.com/downloads/


## Running Docker Image
1. First thing first we have to create image using DockerFile. Run below command which will create image with name blockchain-in-python.
  ```shell
  docker build -t blockchain-in-python .
  ```
  You can varify by running command `docker images` which will display all the images you have created. At the top you will see our image.

2. As we have to run multiple nodes (servers) which can connect with each other we will create a new bridge (default) network.
  ```shell 
  docker network create mynetwork
  ```
  To varify that our network is created run `docker network ls`.

3. Now we will run container for each node. All of these nodes will be part of the network which we have created in second step.
```shell
docker run -d -p 3001:80 -e 'node=http://node1' --net=mynetwork --name node1 blockchain-in-python
docker run -d -p 3002:80 -e 'node=http://node2' --net=mynetwork --name node2 blockchain-in-python
docker run -d -p 3003:80 -e 'node=http://node3' --net=mynetwork --name node3 blockchain-in-python
```
  `-d` &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; : &nbsp; Run container in detached mode </br>
  `-p` &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; : &nbsp; Publish container's port to the host </br>
  `-e` &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; : &nbsp; Set environment variable </br>
  `--net` &nbsp; &nbsp; : &nbsp; Connect a container to network </br>
  `--name` &nbsp; : &nbsp; Assign name to container </br>

## Testing API's
First, Import postman collection from `/postman/collection/Blockchain.postman_collection.json` and environments from `/postman/environments/*`.

1. Blockchain : Get api which return Blockchain data
2. Register-And-Broadcast-Node : It will register a new node on network.
3. Transaction-Broadcast : It will create a new transaction and broadcast on network
4. Mine : It will mine a new block and add all the pending transactions.
5. Consensus : This api is used to verify if the perticular node has the correct blockchain data with respect to other nodes in a network.
