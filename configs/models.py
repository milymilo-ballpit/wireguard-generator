from django.db import models


class PeerConfig(models.Model):
    interface_public_key = models.CharField(max_length=64)
    interface_private_key = models.CharField(max_length=64)
    interface_address = models.CharField(max_length=255)

    server_public_key = models.CharField(max_length=64)
    server_endpoint = models.CharField(max_length=255)
    server_allowed_ips = models.CharField(max_length=255)
    server_dns = models.CharField(max_length=255)

    client_ip = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.interface_public_key}"
