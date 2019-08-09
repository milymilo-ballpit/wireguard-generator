import subprocess
from ipaddress import ip_address

from constance import config


class WireGuard:

    def __init__(self, *args, **kwargs):
        self.server_public_key = config.SERVER_PUBLIC_KEY
        self.server_allowed_ips = config.SERVER_ALLOWED_IPS
        self.server_endpoint = config.SERVER_ENDPOINT
        self.server_dns = config.SERVER_DNS

    def get_pubkey(self, private_key):
        return self.__run_cmd('wg', 'pubkey', input=private_key)

    def gen_privkey(self):
        return self.__run_cmd('wg', 'genkey')

    def get_address(self):
        config.LAST_IP = ip_address(config.LAST_IP) + 1
        return f"{config.LAST_IP}/32"

    def add_peer(self, public_key, address):
        # wg set wg0 peer <public_key> allowed-ips <allowed_ips>
        # REQUIRES: setcap cap_net_admin+eip /usr/bin/wg or running as root
        self.__run_cmd('wg', 'set', 'wg0', 'peer',
                             public_key, 'allowed-ips', address)

        self.__run_cmd('ip', '-4', 'r', 'add', address, 'dev', 'wg0')

    def __run_cmd(self, *args, **kwargs):
        output = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            input=kwargs.get('input', '').encode()
        )

        content = output.stdout.decode().strip('\n')
        return content


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]

    return request.META.get('REMOTE_ADDR')
