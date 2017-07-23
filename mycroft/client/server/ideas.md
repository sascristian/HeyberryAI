# Future server variants / operation modes

each could run in a different port in same unit

# trusted proxy

mycroft client acting as proxy between server and clients, will route messages
and mask identity of user (proxy = single pub key), proxy knows all info from
 all clients, encryption from proxy to server != encryption from client to proxy

- work as server for clients
- ask real server for all answers as a single entity


# relay

relay messages to server and identifies source user (pub_key),
 optionally masking the ip, relay doesnt know the content of messages, just
 the source and destinatary

- work as server for clients
- pass encrypted data between real server and client


# dead drop

store a file temporarily, without knowing who the receiver is

- listen for messages to store message for X days
- listen for requests for dropped files, client tries to decrypt all stored
messages
- delete them after X days

# conference

everyone gets all messages, queued

- sends all messages from all clients to all clients

# chat

allow users to chat without knowing each other location, host doesnt know
contents of messages

- listen for requests of " is X online"
- listen for requests of "message to X" (encrypted, we cant read)

# subscription

send periodic data to connected clients on request, like a newsletter / news

- listen for "last data" messages
- keep track of which clients received each stored message