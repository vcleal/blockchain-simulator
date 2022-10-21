# Blockchain consensus simulator

Simulate a simple blockchain on a real distributed network emulated on Mininet.
For more information on Mininet, see the [Mininet website](http://mininet.org) or the [Wiki](https://github.com/mininet/mininet/wiki/Introduction-to-Mininet).

**Dependencies:**
- Python 2.7.x
- pyzmq

## node.py

Process to run in each host participating in the network. The script doesn't necessarily need to run on Mininet hosts, any machine could do it. Mininet only facilitates the network and usage of multiple nodes.

`$ ./node.py -i 10.0.0.1 -p 9000 --peers 10.0.0.2 10.0.0.3 --log=debug --miner`

**Arguments:**
- `-i`  
IP address of this node in the network
- `-p`  
port to listen to peers (defaults to 9000)
- `--peers`  
list of peers IP addresses that the node will try to connect
- `--miner`  
flag to start this node also executing the mining process
- `--log`  
console log level

```
$ ./node.py -h
usage: node.py [-h] [-i ip] [-p port] [--peers [PEERS [PEERS ...]]] [--miner]
               [--log [LOGLEVEL]] [-c CONFIG_FILE]

Blockchain simulation

optional arguments:
  -h, --help            show this help message and exit
  -i ip, --ip ip        Specify listen IP address
  -p port, --port port  Specify listen port
  --peers [PEERS [PEERS ...]]
                        Specify peers IP addresses
  --miner               Start the node immediately mining
  --log [LOGLEVEL]      Set the logging output level ['CRITICAL', 'ERROR',
                        'WARNING', 'INFO', 'DEBUG']
  -c CONFIG_FILE, --config CONFIG_FILE
                        Specify the configuration file
```

The optional configuration file should have INI format, here's an example:
```
# node.conf
[node]
# default ip 127.0.0.1
ip = 10.0.0.1
# default port 9000
port = 9090
# one peer each line
peers = 10.0.0.2
        10.0.0.3
miner = false	# true/false or yes/no
#loglevel = debug
```

## simple.py

This script is a simple single switch Mininet topology that runs `node.py` in each emulated host with private directories.

More complex networks are also possible, but the user should ensure the connectivity.

**Arguments:**
- number of hosts on switch (*pending*)

Example:
```
$ sudo python simpleNet.py 10
*** Creating network
*** Adding controller
*** Adding hosts and stations:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 
*** Adding switches and access point(s):
s1 
*** Adding link(s):
(h1, s1) (h2, s1) (h3, s1) (h4, s1) (h5, s1) (h6, s1) (h7, s1) (h8, s1) (h9, s1) (h10, s1) 
*** Configuring hosts
*** Starting controller(s)
c0 
*** Starting switches and/or access points
s1 ...
*** Blockchain node starting on h1
*** Blockchain node starting on h2
*** Blockchain node starting on h3
*** Blockchain node starting on h4
*** Blockchain node starting on h5
*** Blockchain node starting on h6
*** Blockchain node starting on h7
*** Blockchain node starting on h8
*** Blockchain node starting on h9
*** Blockchain node starting on h10
*** Starting CLI:
mininet>
```

After this you can execute commands on hosts through the mininet CLI, or even access each host terminal.
```
mininet> h1 rpc/rpcclient.py getlastblock
{
    "nonce": "214074", 
    "index": "132", 
    "hash": "00000223e62597da220d29f46d1f309d8db8a573b8474b01d26b1909ea9c42d0", 
    "tx": "\u001e", 
    "timestamp": "2018-11-23 08:54:14.682075", 
    "merkle_root": "9652595f37edd08c51dfa26567e6cd76e6fa2709c3e578478ca398d316837a7a", 
    "prev_hash": "0000095b7a0e31959780884b0d81b062a21f2a2a34a0ae40538d5795330a85ac"
}

mininet> h5 rpc/rpcclient.py getlastblock
{
    "nonce": "214074", 
    "index": "132", 
    "hash": "00000223e62597da220d29f46d1f309d8db8a573b8474b01d26b1909ea9c42d0", 
    "tx": "\u001e", 
    "timestamp": "2018-11-23 08:54:14.682075", 
    "merkle_root": "9652595f37edd08c51dfa26567e6cd76e6fa2709c3e578478ca398d316837a7a", 
    "prev_hash": "0000095b7a0e31959780884b0d81b062a21f2a2a34a0ae40538d5795330a85ac"
}

mininet> h9 rpc/rpcclient.py getblocks 131 132
{
    "nonce": "688688", 
    "index": "131", 
    "hash": "0000095b7a0e31959780884b0d81b062a21f2a2a34a0ae40538d5795330a85ac", 
    "tx": " ", 
    "timestamp": "2018-11-23 08:54:11.136267", 
    "merkle_root": "36a9e7f1c95b82ffb99743e0c5c4ce95d83c9a430aac59f84ef3cbfab6145068", 
    "prev_hash": "000001f7d66514ed999b044c87371f455273b00b0b683016265864bd8c06bc47"
}
{
    "nonce": "214074", 
    "index": "132", 
    "hash": "00000223e62597da220d29f46d1f309d8db8a573b8474b01d26b1909ea9c42d0", 
    "tx": "\u001e", 
    "timestamp": "2018-11-23 08:54:14.682075", 
    "merkle_root": "9652595f37edd08c51dfa26567e6cd76e6fa2709c3e578478ca398d316837a7a", 
    "prev_hash": "0000095b7a0e31959780884b0d81b062a21f2a2a34a0ae40538d5795330a85ac"
}
```

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
blocks X to Y information
- `getpeerinfo`  
IP of all connected peers  
- `startmining`  
start mining on the node  
- `stopmining`  
stop mining on the node  
- `exit`  
stop node process

```
$ ./rpc/rpcclient.py -h
usage: ./rpc/rpcclient.py [-h]
        <command> [<args>]

Blockchain RPC client

These are the commands available:

getlastblock        Print the last block info
getblock <index>    Print the block info with index <index>
getblocks <list>    Print the blocks info from index <list>
startmining         Start the miner thread
stopmining          Stop the miner thread
addpeer <ip>      	Add <ip> to the node peers list
removepeer <ip>   	Remove <ip> to the node peers list
getpeerinfo         Print the peers list
exit                Terminate and exit the node.py program running
```

Examples:
```
$ ./rpc/rpcclient.py getlastblock
{
    "nonce": "0", 
    "index": "0", 
    "hash": "adbc2423894ab7d91ab583be0e660aa92673ec6445f026a9aeed4289e5ed6fe3", 
    "tx": "", 
    "timestamp": "2018-10-10 00:00:0.0", 
    "merkle_root": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 
    "prev_hash": ""
}

$ ./rpc/rpcclient.py startmining
Starting mining...

$ ./rpc/rpcclient.py stopmining
Stopping mining...

$ ./rpc/rpcclient.py getlastblock
{
    "nonce": "3117090", 
    "index": "2", 
    "hash": "00000e1164cd1e93becf31b16c1ab66e7370e4265a5cfc9c6028ebb81c7bd913", 
    "tx": "\n", 
    "timestamp": "2018-12-02 20:47:11.589315", 
    "merkle_root": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b", 
    "prev_hash": "00000d354ffca98697c2804202d79a179f5e4e3ab6f5edb87a0c1f3d47810df6"
}

$ ./rpc/rpcclient.py exit
Exiting...
```

###### TODO
- 
