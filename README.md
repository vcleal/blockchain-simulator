# bc_testbed
A testbed to implement and evaluate blockchain consensus mechanisms.

**Dependencies:**
- Python 2.7.x
- pyzmq

## node.py

Process to run in each host participating in the network.

**Arguments:**
- `-i`  
IP address of the node in the network
- `-p`  
port to listen to peers (defaults to 9000)
- `--peers`  
list of peers IP addresses
- `--miner`  
start node mining
- `--log`  
console log level
- `-c`  
configuration file

## simpleNet.py

Simple single switch Mininet topology that runs `node.py` in each host with private directories.

**Arguments:**
- number of hosts on switch

## rpc/rpcclient.py

Localhost client to communicate with the node process and obtain blockchain info

**Arguments:**
- `getlastblock`  
last block on the chain
- `addpeer X`  
add X peer IP and connect to it
- `removepeer X`  
remove X peer and disconnect
- `getblock X`  
block X information
- `getblocks X Y`  
blocks X and Y information
- `getpeerinfo`  
IP of all connected peers  
- `startmining`  
start mining on the node  
- `stopmining`  
stop mining on the node  
- `exit`  
stop node process

###### TODO
- 
>>>>>>> 0c247b2cff96e5c07bb09a3f0b5962e5c6f2d248
