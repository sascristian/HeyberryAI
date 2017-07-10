from mycroft.util.jarbas_services import ServiceBackend

class ServerService(ServiceBackend):
    def __init__(self, emitter=None, timeout=125, waiting_messages=None, logger=None):
        super(ServerService, self).__init__(name="ServerService", emitter=emitter, timeout=timeout,
                                            waiting_messages=waiting_messages, logger=logger)
    def pgp_request(self, sock_num):
        message_type = "client.pgp.public.request"
        message_data = {"public_key": ascii_public, "key_id": key_id, "cipher": "none"}
        message_context = {"sock_num": sock_num}
        self.send_request(message_type=message_type, message_data=message_data, message_context=message_context, client=True)
        self.wait("client.pgp.public.response")
        return self.result

    def aes_key_exchange(self, sock_num, iv=None, key=None):
        message_type = "client.aes.key"
        iv, key = self.aes_generate_pair(iv, key)
        sock_ciphers[sock_num]["aes_key"] = key
        sock_ciphers[sock_num]["aes_iv"] = iv
        message_data = {"aes_key": key, "iv": iv, "cipher": "pgp"}
        message_context = {"sock_num": sock_num}
        self.send_request(message_type=message_type, message_data=message_data, message_context=message_context,
                          client=True)
        self.wait("client.aes.exchange_complete")
        return self.result

    def aes_generate_pair(self, iv=None, key=None):
        if iv is None:
            iv = Random.new().read(AES.block_size)
        if key is None:
            key = Random.get_random_bytes(32)
        return iv, key

