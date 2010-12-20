# Requirements:
* Python 3.2
* PyMongo 1.9
* Linux (64-bit)

# Quick Start
## Starting Servers
Several servers must be started before clients can perform any work.

### MongoDB
`vendor/mongodb/mongod --dbpath=/path/to/data/dir`

### HTTP
`python dmut/server/http_server.py`

### Master
`python dmut/server/master.py`

## Starting Clients
Clients can easily be started by starting the slave script.
`python dmut/client/slave.py localhost:8001 localhost:8000`

Alternatively, one can use the provided BASH script to spawn 4 clients.
`./spawn.sh`
