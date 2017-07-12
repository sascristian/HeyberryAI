Some steps were done to connect mycroft instances together, every instance can receive connections and send answers, or connect and ask answers

![ssl](https://raw.githubusercontent.com/JarbasAI/client_server_idea/master/ssl.jpeg)

# usage cases

Computational Server:

    - host deep dream, facebook, everything heavy
    - clients connect for heavy processing/private skills

House/Company Server:

    - connect all your mycrofts, "kitchen", "living room", "magic mirror", use them as a single one or to relay orders


Conference mode:

    - server sends all utterances to all clients (like a chat room)

Relay mode:

    - act like middle man, send messages from x to y, encrypted so you don't know what it says, clients don't know where it comes from

Subscription mode:

    - periodic broadcast of "newsletter" to all connected clients

Direct Chat:

    - speak messages in each side of the connection (lazy intercom)

Fallback Mycroft:

    - on intent failure ask other trusted mycroft to answer you



![house](https://raw.githubusercontent.com/JarbasAI/client_server_idea/master/Untitled%20Diagram.jpg)


Or you can go wild, create the mycroft mesh collective:

 - many mycrofts all running both as server and client,
 - each "asking their parent" the answers for the questions they do not know,
 - make a protocol to transfer and validate skills between mycrofts,
 - watch it evolve by itself as masters update code
 - throw smart contracts in so humans can't stop the mycroft evolution


# Trust model

- anyone can start ssl connection to server
- whitelist/blacklist ips in server
- on connecting a pgp_public key is exchanged
- initial aes key exchanged encrypted with client public-key
- all communications after are AES encrypted with a new key every message
- permissions per user (messages, skills, intents)
- client public_key is the authentication method, lose it, lose special permissions
- server keeps track of known ips, connection history, nicknames for this key
- server pre-process all client messages before emitting them to messagebus
- client trusts all server messages and emits them directly to messagebus
- you can be both server and client

# jarbas client

- the client process connects to the messagebus
- opens a ssl connection to jarbas's server
- receives id from server
- send's names list to server
- on utterance starts monitoring responses
- if some intent triggers -> do nothing
- if intent_failure -> ask server
- if 20 seconds and no intent nor failure trigger -> ask server
- listen for requests to message server, including files
- trust all messages from server and broadcast them to client messagebus


# jarbas server

- the server process connects to the messagebus
- listens for client ssl connections
- check if ip is black/whitelisted
- check if received message types are whitelisted (unknown/blacklisted messages are discarded)
- do message pre-processing (receive files, add context)
- answer client requests
- answer internal skills message_to_client requests

# TODO

- listen for intent.execution.start/end/failure to ask server (20 secs is a placeholder)


# Server , Key exchange Logs

        2017-07-11 23:17:11,833 - Jarbas_Server - INFO - Jarbas server key loaded
        2017-07-11 23:17:11,848 - Jarbas_Server - INFO - -----BEGIN PGP PUBLIC KEY BLOCK-----
        Version: GnuPG v1

        mI0EWWQxOQEEAMPxq+VAgRFnFcOG3HtR2IFUK47co8K3u4PoUonlEaAQDE+OoPgV
        5wibzLhkWFikzLBNLXcqPe1IUi8Yn/drtewDX4wqKysLAtVxvepYMUmjX2LEp5PK
        ib63Loimv6FPIzgEGwjlyNLAK21QzsRZEhBEq4eAv4PQj6d7yno044VPABEBAAG0
        L0phcmJhc0FJIChqYXJiYXMgc2VydmVyIGtleSkgPEphcmJhc0BKYXJiYXMuYWk+
        iLgEEwECACIFAllkMTkCGy8GCwkIBwMCBhUIAgkKCwQWAgMBAh4BAheAAAoJEPQK
        6GhUVrtvCswD/229B/IkUftKMQlwfc8nhRfCv2OYQ38cPbV4tjp525Wbvz7x9KCi
        K5bHHo5XS9IDlDw/frC6uR7q0HSsDKg/npxmmea1q/9yFuwRPfqk29pr7qumLpML
        B68yCxfNtutSjqh/Oh6PcGCdGo1sNetV8yvZRCo5y46aM14scXuXNwh/
        =agzw
        -----END PGP PUBLIC KEY BLOCK-----

        2017-07-11 23:17:11,855 - Jarbas_Server - DEBUG - Listening started on port 5000
        2017-07-11 23:17:11,859 - mycroft.messagebus.client.ws - INFO - Connected
        2017-07-11 23:17:12,473 - Jarbas_Server - DEBUG - Client (127.0.0.1, 55976) connected
        2017-07-11 23:17:12,503 - Jarbas_Server - INFO - Sending public pgp key to client
        2017-07-11 23:17:12,508 - Jarbas_Server - INFO - Message_Request: sock:55976 with type: client.pgp.public.request with data: {u'public_key': u'-----BEGIN PGP PUBLIC KEY BLOCK-----\nVersion: GnuPG v1\n\nmI0EWWQxOQEEAMPxq+VAgRFnFcOG3HtR2IFUK47co8K3u4PoUonlEaAQDE+OoPgV\n5wibzLhkWFikzLBNLXcqPe1IUi8Yn/drtewDX4wqKysLAtVxvepYMUmjX2LEp5PK\nib63Loimv6FPIzgEGwjlyNLAK21QzsRZEhBEq4eAv4PQj6d7yno044VPABEBAAG0\nL0phcmJhc0FJIChqYXJiYXMgc2VydmVyIGtleSkgPEphcmJhc0BKYXJiYXMuYWk+\niLgEEwECACIFAllkMTkCGy8GCwkIBwMCBhUIAgkKCwQWAgMBAh4BAheAAAoJEPQK\n6GhUVrtvCswD/229B/IkUftKMQlwfc8nhRfCv2OYQ38cPbV4tjp525Wbvz7x9KCi\nK5bHHo5XS9IDlDw/frC6uR7q0HSsDKg/npxmmea1q/9yFuwRPfqk29pr7qumLpML\nB68yCxfNtutSjqh/Oh6PcGCdGo1sNetV8yvZRCo5y46aM14scXuXNwh/\n=agzw\n-----END PGP PUBLIC KEY BLOCK-----\n', u'cipher': u'none', u'fingerprint': u'238ABE926EB72433DC519BD9F40AE8685456BB6F'}
        2017-07-11 23:17:12,510 - Jarbas_Server - DEBUG - Answering sock 55976
        2017-07-11 23:17:12,510 - Jarbas_Server - DEBUG - Encryption: none
        2017-07-11 23:17:12,510 - Jarbas_Server - DEBUG - Sucessfully sent data: {"data": {"public_key": "-----BEGIN PGP PUBLIC KEY BLOCK-----\nVersion: GnuPG v1\n\nmI0EWWQxOQEEAMPxq+VAgRFnFcOG3HtR2IFUK47co8K3u4PoUonlEaAQDE+OoPgV\n5wibzLhkWFikzLBNLXcqPe1IUi8Yn/drtewDX4wqKysLAtVxvepYMUmjX2LEp5PK\nib63Loimv6FPIzgEGwjlyNLAK21QzsRZEhBEq4eAv4PQj6d7yno044VPABEBAAG0\nL0phcmJhc0FJIChqYXJiYXMgc2VydmVyIGtleSkgPEphcmJhc0BKYXJiYXMuYWk+\niLgEEwECACIFAllkMTkCGy8GCwkIBwMCBhUIAgkKCwQWAgMBAh4BAheAAAoJEPQK\n6GhUVrtvCswD/229B/IkUftKMQlwfc8nhRfCv2OYQ38cPbV4tjp525Wbvz7x9KCi\nK5bHHo5XS9IDlDw/frC6uR7q0HSsDKg/npxmmea1q/9yFuwRPfqk29pr7qumLpML\nB68yCxfNtutSjqh/Oh6PcGCdGo1sNetV8yvZRCo5y46aM14scXuXNwh/\n=agzw\n-----END PGP PUBLIC KEY BLOCK-----\n", "cipher": "none", "fingerprint": "238ABE926EB72433DC519BD9F40AE8685456BB6F"}, "type": "client.pgp.public.request", "context": {"sock_num": "55976", "source": "KeyExchangeService:server"}}
        2017-07-11 23:17:12,589 - Jarbas_Server - DEBUG - current status: sending pgp
        2017-07-11 23:17:12,590 - Jarbas_Server - DEBUG - Received PGP encrypted message: -----BEGIN PGP MESSAGE-----
        Version: GnuPG v1

        hIwD9AroaFRWu28BA/9/QPUTAarwyEQhpnW0Xnl3BtNdpUQirXIWSyLEZ3y1uYHA
        4ywSQWmZKGkzo75G5tuBhpkKjRQ9hcu70Tw0iQMy45CpWG+2fdaykzokBEbEpsjV
        0jtgTK/Y9KaU1I4qpyKkokX7bC2j7vLxrPhjHq7oLe0/xif9f6hIiSNdJVOeZNLp
        AUN0vSFAgPC0Lqsi0PWQuDOIUrYyuu5Ms7IyAaEcfB3B6eWuMXo9lVyWTtUJ5On2
        KYw01paYXGCdOp3G7PSm+C6D1oklTLFBvrfkeT8vVFSJLfrGZYN2kQjVaoVkjlvQ
        Frob72tHOKKYUCWJNxmmqcmrpdE1R12LwHL08tC18hq8tDc5rGCTCD6jIqlitU+V
        GD9wFsKWESI5T5So4U75CvSNMyikcDkLy4KLvI3a6dUyS7AwUcY6ZiAwnT26sySi
        3BHGzUQUcs6Q7/dX4csKlqdDN+UX3WY/+l9z+FsQ4XeBe2Mx8eQD7gZEdr5fdTWo
        A5URzhYO5bPktpnMauVh5dKRCY4Hql9KA56rm702uOixEwF9tLz0JtFhHOinlAjD
        z5cOIrba5TEjmBs8hoegE43kA1il5ovGZQpbE03TO4AFClg2GQgrQdgaRcYCVXWC
        fA8mPl6SczZyUWCx73MWdjLBHztZQA8y4orxI90CbZ/9HoQxtLv3ycKmI2gwsjG/
        GX7PI8rv92GtfA6fqk4U0AalhZaqDS5sO4T4GHkZy7W3zacL+4PHg6mqz4uFNrvy
        UXwbVzeWVNmaN7cG9Jx7WyQjhOwwVaVfTfxPMHB2ddB01hCe+f9VPePiol1aeS6s
        3cDAN28eAkvbl8JKLz+CeO0bV2pVOdsD/VdRTH83Ltd0+4oOx9v6BUuz4DTek+kt
        HCthMnKDlCrDLcZ40NdC0a0Oyf1WmKSQO6Q+uEF8faaTP3Rfq4tb0w594VN01Vqm
        LSVoWbd01FRLt8/bam7oa7mQcwucE0ZXl3jlGBqWewZU0rQeH21UuPNnuKLHUC04
        7sJhYd8=
        =CmU8
        -----END PGP MESSAGE-----

        2017-07-11 23:17:12,590 - Jarbas_Server - DEBUG - Attempting to decrypt
        2017-07-11 23:17:12,612 - Jarbas_Server - DEBUG - Decrypted message: {"data": {"public_key": "-----BEGIN PGP PUBLIC KEY BLOCK-----\nVersion: GnuPG v1\n\nmI0EWWQxTgEEANI+vI0CXBNUDUTxOMnpR8lJ7SL+t8CRtA60R+FUdzWgpmLOWaTd\n1igMTtwID+eIRVPMucxxBJLEYDe6VC1hJ3qkSFWV8eTNGLNOW2WiSwNK0Z1DHSX6\n3IZgzQ/GdxG8CzMfKSMnOFKTxkUxJ5peeDAGBaC1Ubj+fKny5h7t1+W9ABEBAAG0\nN01pbmlKYXJiYXMgKGphcmJhcyBjbGllbnQga2V5KSA8SmFyYmFzQ2xpZW50QEph\ncmJhcy5haT6IuAQTAQIAIgUCWWQxTgIbLwYLCQgHAwIGFQgCCQoLBBYCAwECHgEC\nF4AACgkQECpTymtp9iGqugQAixjCzpsKLy1eyAD+w+wGHT2oN4PF3weAYhE7XxJ0\n7y9kenYsWUnscl0SRI1OoeH/lgP4SMR6RoF0YOIWlMFsq/j+ENVVtW33xgAa4UUN\nDlz8JyHWBOyQySSidA9dHDYMGqlJmklM146RX372+TS6oLLkGX/BHSOFkWjCxQ/l\n8Kg=\n=0ogb\n-----END PGP PUBLIC KEY BLOCK-----\n"}, "type": "client.pgp.public.response", "context": null}
        2017-07-11 23:17:12,612 - Jarbas_Server - DEBUG - Message type: client.pgp.public.response
        2017-07-11 23:17:12,804 - Jarbas_Server - INFO - Received client public pgp key:
        -----BEGIN PGP PUBLIC KEY BLOCK-----
        Version: GnuPG v1

        mI0EWWQxTgEEANI+vI0CXBNUDUTxOMnpR8lJ7SL+t8CRtA60R+FUdzWgpmLOWaTd
        1igMTtwID+eIRVPMucxxBJLEYDe6VC1hJ3qkSFWV8eTNGLNOW2WiSwNK0Z1DHSX6
        3IZgzQ/GdxG8CzMfKSMnOFKTxkUxJ5peeDAGBaC1Ubj+fKny5h7t1+W9ABEBAAG0
        N01pbmlKYXJiYXMgKGphcmJhcyBjbGllbnQga2V5KSA8SmFyYmFzQ2xpZW50QEph
        cmJhcy5haT6IuAQTAQIAIgUCWWQxTgIbLwYLCQgHAwIGFQgCCQoLBBYCAwECHgEC
        F4AACgkQECpTymtp9iGqugQAixjCzpsKLy1eyAD+w+wGHT2oN4PF3weAYhE7XxJ0
        7y9kenYsWUnscl0SRI1OoeH/lgP4SMR6RoF0YOIWlMFsq/j+ENVVtW33xgAa4UUN
        Dlz8JyHWBOyQySSidA9dHDYMGqlJmklM146RX372+TS6oLLkGX/BHSOFkWjCxQ/l
        8Kg=
        =0ogb
        -----END PGP PUBLIC KEY BLOCK-----

        2017-07-11 23:17:12,805 - Jarbas_Server - INFO - importing client pgp key
        2017-07-11 23:17:12,849 - Jarbas_Server - INFO - fingerprint: 147190AE8E927ECECE25C5B8102A53CA6B69F621
        2017-07-11 23:17:12,850 - Jarbas_Server - INFO - Initiating AES key exchange
        2017-07-11 23:17:12,856 - Jarbas_Server - INFO - Message_Request: sock:55976 with type: client.aes.key with data: {u'cipher': u'pgp', u'aes_key': u'hivWDyc/k7I2+hwqyhSUd5+1nMmHvkGEvYLdwT6wtUM=', u'iv': u'SrsWFUnYEo9UfWeED9juKQ=='}
        2017-07-11 23:17:12,857 - Jarbas_Server - DEBUG - Answering sock 55976
        2017-07-11 23:17:12,857 - Jarbas_Server - DEBUG - Encryption: pgp
        2017-07-11 23:17:12,858 - Jarbas_Server - DEBUG - target pgp fingerprint: 147190AE8E927ECECE25C5B8102A53CA6B69F621
        2017-07-11 23:17:12,884 - Jarbas_Server - DEBUG - Sucessfully sent data:
        -----BEGIN PGP MESSAGE-----
        Version: GnuPG v1

        hIwDECpTymtp9iEBA/9FFEQUUQlhvyf98Gz6W0I8+uDETqSn9qf6/xhPLQat5rdV
        eNsVMDAAFM9xdXDtUQg7/47B/8E203vrtjYsG30iXTeyTGQnN0i4FHR9ZWxWG+a/
        6HYSGTdYqx1Fbb1sUZcBECRcM8BIJKj6Cjwm7hZc1x/2iu6vayBl2PtyggRxldLA
        NAHfDqE5RM3JBMMpHSh+KLupNEhiGT38s0tbjV/iyCdeRdkXt/Il/MDV78Z3MZjl
        l7B+AF1kiQH8faZUjCqc6UjpjSzd2L6DyRWn3W1WNIxg1Kgjtn48BHZBVQ3V/2eb
        Sm/dcJJelUUrUJdpvnVYlOOmBpN1XEXcHPEAY5bodNTBNfw6k+AwGgU+JRIA0JmA
        bL1QceSspWrpxcb8/jQLL0yLDZk5raL+i3OTHGRtTJBPBuoBFSZOXEPBMshvXnNM
        Sot0PLYjQZYYaXL3HP+w5lFSWonw8pzYgPlrbd7yLAl4uorL4WIoncnfhIWcX+JR
        +6zafx8=
        =+K23
        -----END PGP MESSAGE-----

        2017-07-11 23:17:12,929 - Jarbas_Server - DEBUG - current status: sending aes key
        2017-07-11 23:17:12,929 - Jarbas_Server - DEBUG - Received AES encrypted message: J�I��T}g���)�T�}4h��\Cs�٨���%�ga	�؜�_M:����S٪$Xl�����0��x!���%���Xn�+�Ϙ�!c�
        2017-07-11 23:17:12,929 - Jarbas_Server - DEBUG - Attempting to decrypt aes message
        2017-07-11 23:17:12,930 - Jarbas_Server - DEBUG - Decrypted message: {"data": {"status": "success"}, "type": "client.aes.exchange.complete", "context": null}
        2017-07-11 23:17:12,934 - Jarbas_Server - DEBUG - Message type: client.aes.exchange.complete
        2017-07-11 23:17:13,162 - KeyExchangeService - INFO - AES Exchange result:{u'status': u'success'}
        2017-07-11 23:17:13,162 - Jarbas_Server - INFO - Key exchange complete


# client key exchange Logs


        2017-07-11 23:50:48,546 - jarbas - INFO - Jarbas client key loaded
        2017-07-11 23:50:48,625 - jarbas - INFO - -----BEGIN PGP PUBLIC KEY BLOCK-----
        Version: GnuPG v1

        mI0EWWVRjQEEANcVivXj96ZzWlErJdVpmIBbbUaVapXeOs20LaYwzFKGMYN1F8rj
        WH7KTq8j+ESgYYab0V6DGtmjes2LuOhMCLsXXZ6BFQmc2T0kojf7T/dT4nl/WxTD
        jgfvD/YV9DeOIv3rbBdukpq6OinP4ayTR+dl8QTyqT0gSXao534mnckhABEBAAG0
        N01pbmlKYXJiYXMgKGphcmJhcyBjbGllbnQga2V5KSA8SmFyYmFzQ2xpZW50QEph
        cmJhcy5haT6IuAQTAQIAIgUCWWVRjQIbLwYLCQgHAwIGFQgCCQoLBBYCAwECHgEC
        F4AACgkQgWSRwy6PTLIK/gP/YLewHATVXwxld146aHDoRHicZWvdnsY5eF/QjWxC
        Jj7JZ332GenEWgUMCXwVaPsXP+f1U/8Kn8Pdjd93W2SFNT7v2CGyYsTZp7hemu0n
        KfvFqoggKtlNNG61ZZMyLujqW3EsLJK5VA/CdweHXSHqNs6yunRwl9VHpFltSmiM
        LII=
        =6uBE
        -----END PGP PUBLIC KEY BLOCK-----

        2017-07-11 23:50:48,669 - mycroft.messagebus.client.ws - INFO - Connected
        2017-07-11 23:50:48,719 - jarbas - DEBUG - Connected to remote host. Exchanging keys
        2017-07-11 23:50:48,754 - jarbas - DEBUG - status: waiting for pgp
        2017-07-11 23:50:48,754 - jarbas - DEBUG - Received server key:
        -----BEGIN PGP PUBLIC KEY BLOCK-----
        Version: GnuPG v1

        mI0EWWQxOQEEAMPxq+VAgRFnFcOG3HtR2IFUK47co8K3u4PoUonlEaAQDE+OoPgV
        5wibzLhkWFikzLBNLXcqPe1IUi8Yn/drtewDX4wqKysLAtVxvepYMUmjX2LEp5PK
        ib63Loimv6FPIzgEGwjlyNLAK21QzsRZEhBEq4eAv4PQj6d7yno044VPABEBAAG0
        L0phcmJhc0FJIChqYXJiYXMgc2VydmVyIGtleSkgPEphcmJhc0BKYXJiYXMuYWk+
        iLgEEwECACIFAllkMTkCGy8GCwkIBwMCBhUIAgkKCwQWAgMBAh4BAheAAAoJEPQK
        6GhUVrtvCswD/229B/IkUftKMQlwfc8nhRfCv2OYQ38cPbV4tjp525Wbvz7x9KCi
        K5bHHo5XS9IDlDw/frC6uR7q0HSsDKg/npxmmea1q/9yFuwRPfqk29pr7qumLpML
        B68yCxfNtutSjqh/Oh6PcGCdGo1sNetV8yvZRCo5y46aM14scXuXNwh/
        =agzw
        -----END PGP PUBLIC KEY BLOCK-----

        2017-07-11 23:50:48,798 - jarbas - DEBUG - {"data": {"public_key": "-----BEGIN PGP PUBLIC KEY BLOCK-----\nVersion: GnuPG v1\n\nmI0EWWVRjQEEANcVivXj96ZzWlErJdVpmIBbbUaVapXeOs20LaYwzFKGMYN1F8rj\nWH7KTq8j+ESgYYab0V6DGtmjes2LuOhMCLsXXZ6BFQmc2T0kojf7T/dT4nl/WxTD\njgfvD/YV9DeOIv3rbBdukpq6OinP4ayTR+dl8QTyqT0gSXao534mnckhABEBAAG0\nN01pbmlKYXJiYXMgKGphcmJhcyBjbGllbnQga2V5KSA8SmFyYmFzQ2xpZW50QEph\ncmJhcy5haT6IuAQTAQIAIgUCWWVRjQIbLwYLCQgHAwIGFQgCCQoLBBYCAwECHgEC\nF4AACgkQgWSRwy6PTLIK/gP/YLewHATVXwxld146aHDoRHicZWvdnsY5eF/QjWxC\nJj7JZ332GenEWgUMCXwVaPsXP+f1U/8Kn8Pdjd93W2SFNT7v2CGyYsTZp7hemu0n\nKfvFqoggKtlNNG61ZZMyLujqW3EsLJK5VA/CdweHXSHqNs6yunRwl9VHpFltSmiM\nLII=\n=6uBE\n-----END PGP PUBLIC KEY BLOCK-----\n"}, "type": "client.pgp.public.response", "context": null}
        2017-07-11 23:50:48,821 - jarbas - DEBUG - Sending pgp key to server:
        -----BEGIN PGP MESSAGE-----
        Version: GnuPG v1

        hIwD9AroaFRWu28BBACdFDdxNuu8zX18555Y1ku26csbeW+lgCquRPaYYpD0CuQz
        ONJXDQrjgEGWk+KuQ15ibptYGEt8JFKg2+PgNTgQzktiblTZ/40LMvORXKj4SXZD
        YmCSUID5QUiFVFIDGn4HA8FBL4HbGs6wsXP3xOUp/itE7L35qfp//v1Wmn36ftLp
        AT1kf7wp2HAxO4303uI7EaofTbypY8XVy7hEd774SqJA/T1mMymkRPrANiVyiPjI
        NPjTNCpPTwAJowDVpbiYlh5EmLXh7DaDo8P/MtEqxzDNgwgR43GFEZmmUCLMtY+c
        XrFNVkw9qjlZCiBRUlNpcavkC8SkDjwyey6hvNXWhktqA8rNCEUpCGuM1UeZ0+39
        XjRibc1CmmX06dy/c/7FaL0cyCYXdOCNkx0dMiS2thswiHdr5CL5k9j1AoLoGyJK
        hkhZiOz8BIDdNI/y+drhCepLXb1lXZVhLUeBptDBpmSivKF2GO3vjpPho+IfTMvA
        xB3KsDSJiwm+k+t5L+/vM5PZlu4wXhK8OVTNgWbMk2xHjRos8KAh2I+bv+O62KEa
        gJC8aUR4sVtktd+WjBNnMFbzZPDT880A64xW7gIeW/Vb4qHaLgMq570BWV0tJ+eH
        qoTvZGOcOMuGxsb5/pogQbX693eaR39H2RUjgh4dwHPBf4QND/2dauhpQW59GR2X
        YabILHGKekRft8B6Kv3xzMkkynX/6s1zL87rRku2Kr0UKuZYoWxWTe3dZf8PGzFB
        ISDs+Bxm5DkruoSdp7CsRKTCtQ+YhCRuZ+6gGyveF7grFNOWzQf390oIz1yoYLZX
        0IjMe858ltarsQ+iPmg1Gcy00fzP/2v+ZrXLzvfP3vt4WPGAnAef8aEpgnwJyyK9
        KwxtVI++XOE90JEX46nVr0xx5ctA+KW+JBNVgWj2h5MxVd2er5ahyWH6F65MIY0B
        O5ZRbiqxxIuCdM/4cGhZYVmDbix818da6msg91Huzt92HWtq+2TLKm8LJWnUBFwp
        mAKD8raz25Ei
        =B2JD
        -----END PGP MESSAGE-----

        2017-07-11 23:50:48,822 - jarbas - DEBUG - Pgp key sent, waiting for initial AES key
        2017-07-11 23:50:49,135 - jarbas - DEBUG - status: waiting for aes
        2017-07-11 23:50:49,135 - jarbas - DEBUG - Received PGP encrypted AES key Exchange
        -----BEGIN PGP MESSAGE-----
        Version: GnuPG v1

        hIwDgWSRwy6PTLIBBADEYnTkHnD7wL4O8IoolWgl1b6xtXV7aRdgvXxLfR1pfSSc
        qhzoSRFDqO3vISP44njwIzpeNMM3fmVsZq7ZpEfEaeQC1zzPOXtYtnYxkLG4VNqo
        2/tpumb4vpIMAkEFXkDowLArVy8vPhxLTiz1Ri0sqg0YpqYuIpUt98w8V/8hP9LA
        OQFu2zHxcjFyMFQIkoSkA0JQIR4+3VIQYA+KtmzrujYnNbXaef0K9IvqZIk/Fr3i
        51aVdBw4ZqV/OnYFTVNft9O89Nz+aqfiq/i1raP0dKj36w8lJBxpyjD4d6kuZ0oi
        AWWI+AWqiMhJyNALKwO2IYHao1fDgEqlYQkNdwimpMCfLEgf30307q0CLaOb5W1U
        kila4VZxd4X/X3RJpcV7xTQs6ySxAHvbSb3234/zMMMrcQpkd7SsqVaA1aLdomZL
        oZ+e7whquRtsSOzvHDSMxOx6AWuUDuDuHIlCUyMdh63RqsOn6t+AIXw0uGbv+mRa
        0hwooZkWGBpneg==
        =+QlX
        -----END PGP MESSAGE-----

        2017-07-11 23:50:49,193 - jarbas - DEBUG - Decrypted Message:
        {"data": {"cipher": "pgp", "aes_key": "s0BaMCkpZUi9odIxcIR9k2ZnhHufdqWTvwsBvXAcHzw=", "iv": "8swZXDt5I+QA13qugcIenw=="}, "type": "client.aes.key", "context": {"sock_num": "56116", "source": "KeyExchangeService:server"}}
        2017-07-11 23:50:49,195 - jarbas - DEBUG - Key exchange complete, you are communicating securely
        2017-07-11 23:50:49,195 - jarbas - DEBUG - Start sending messages

# client usage LOGS

            2017-07-05 15:19:08,354 - jarbas - DEBUG - Connected to remote host. Start sending messages
            2017-07-05 15:19:08,574 - jarbas - DEBUG - Received data: {"data": {"id": 42904}, "type": "id", "context": null}
            2017-07-05 15:59:05,408 - jarbas - ERROR - Disconnected from server
            2017-07-05 15:59:05,693 - jarbas - ERROR - Unable to connect, error [Errno 111] Connection refused, retrying in 5 seconds
            2017-07-05 15:59:05,693 - jarbas - ERROR - Possible causes: Server Down, Bad key, Bad Adress
            2017-07-05 15:59:12,055 - jarbas - DEBUG - Connected to remote host. Start sending messages
            2017-07-05 15:59:12,156 - jarbas - DEBUG - Received data: {"data": {"id": 43166}, "type": "id", "context": null}
            2017-07-05 16:01:41,662 - jarbas - DEBUG - Processing utterance: describe what you see from source: cli
            2017-07-05 16:01:41,674 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:01:41,739 - jarbas - DEBUG - intent handled internally
            2017-07-05 16:01:41,775 - jarbas - DEBUG - Not asking server
            2017-07-05 16:01:42,542 - jarbas - INFO - Received request to message server from vision_service with type: image_classification_request with data: {u'source': u'vision_service', u'user': u'unknown', u'file': u'/home/user/jarbas_stable/JarbasAI/jarbas_skills/service_vision/feed.jpg'}
            2017-07-05 16:01:42,542 - jarbas - INFO - File requested, sending first
            sending chunk 1
            sending chunk 2
            sending chunk 3
            sending chunk 4
            sending chunk 5
            sending chunk 6
            sending chunk 7
            sending chunk 8
            sending chunk 9
            sending chunk 10
            sending chunk 11
            sending chunk 12
            sending chunk 13
            sending chunk 14
            sending chunk 15
            sending chunk 16
            sending chunk 17
            sending chunk 18
            2017-07-05 16:01:43,882 - jarbas - INFO - sending message with type: image_classification_request
            2017-07-05 16:02:00,040 - jarbas - DEBUG - Received data: {"data": {"classification": ["n01910747 jellyfish", "n04606251 wreck", "n01484850 great white shark, white shark, man-eater, man-eating shark, Carcharodon carcharias", "n01494475 hammerhead, hammerhead shark", "n01496331 electric ray, crampfish, numbfish, torpedo"]}, "type": "image_classification_result", "context": {"mute": false, "destinatary": "jarbas:43166", "source": "ImageRecognitionSkill:server", "more_speech": false}}
            2017-07-05 16:03:08,766 - jarbas - DEBUG - Processing utterance: who am i from source: cli
            2017-07-05 16:03:08,766 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:03:08,893 - jarbas - DEBUG - Intent failure detected, ending wait
            2017-07-05 16:03:08,967 - jarbas - DEBUG - Asking server for answer
            2017-07-05 16:03:09,151 - jarbas - DEBUG - Received data: {"data": {}, "type": "vision_request", "context": {"source": "skills:server"}}
            2017-07-05 16:03:10,111 - jarbas - INFO - Received request to message server from vision_service with type: vision_result with data: {u'distance': 0, u'smile_detected': False, u'num_persons': 0, u'master': False, u'file': u'/home/user/jarbas_stable/JarbasAI/jarbas_skills/service_vision/webcam/Wed_Jul__5_16:03:09_2017.jpg', u'movement': False}
            2017-07-05 16:03:10,111 - jarbas - INFO - File requested, sending first
            sending chunk 1
            sending chunk 2
            sending chunk 3
            sending chunk 4
            sending chunk 5
            sending chunk 6
            sending chunk 7
            sending chunk 8
            sending chunk 9
            sending chunk 10
            sending chunk 11
            sending chunk 12
            sending chunk 13
            sending chunk 14
            sending chunk 15
            sending chunk 16
            sending chunk 17
            sending chunk 18
            2017-07-05 16:03:12,282 - jarbas - INFO - sending message with type: vision_result
            2017-07-05 16:03:13,469 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "You are 43166, according to source of message\n", "metadata": {}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:04:10,675 - jarbas - DEBUG - Processing utterance: what am i from source: cli
            2017-07-05 16:04:10,676 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:04:10,789 - jarbas - DEBUG - Intent failure detected, ending wait
            2017-07-05 16:04:10,878 - jarbas - DEBUG - Asking server for answer
            2017-07-05 16:04:11,174 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "You are jarbas user", "metadata": {}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:04:56,585 - jarbas - DEBUG - Processing utterance: joke from source: cli
            2017-07-05 16:04:56,586 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:04:56,689 - jarbas - DEBUG - Intent failure detected, ending wait
            2017-07-05 16:04:56,787 - jarbas - DEBUG - Asking server for answer
            2017-07-05 16:04:57,151 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "'It works on my machine' always holds true for Chuck Norris.", "metadata": {}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:05:57,683 - jarbas - DEBUG - Processing utterance: dream from source: cli
            2017-07-05 16:05:57,684 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:05:58,066 - jarbas - DEBUG - Intent failure detected, ending wait
            2017-07-05 16:05:58,085 - jarbas - DEBUG - Asking server for answer
            2017-07-05 16:05:58,763 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "please wait while the dream is processed", "metadata": {}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:16:18,341 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "Here is what i dreamed", "metadata": {"url": "http://i.imgur.com/BTCarU4.jpg", "elapsed_time": 616.5030989646912, "file": "../database/dreams/Wed_Jul__5_11:16:14_2017.jpg"}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:16:18,577 - jarbas - DEBUG - Received data: {"data": {"elapsed_time": 616.5030989646912, "layer": "inception_3a/pool", "dream_url": "http://i.imgur.com/BTCarU4.jpg", "file": "../database/dreams/Wed_Jul__5_11:16:14_2017.jpg"}, "type": "deep_dream_result", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills:server", "user": "43166", "more_speech": false}}
