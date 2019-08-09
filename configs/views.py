from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import FormView, TemplateView

from base64 import b64encode
from qrcode import QRCode
from redis import Redis
from io import BytesIO

from .forms import ConnectionPackForm, ConnectionPackLookupForm
from .models import PeerConfig
from .utils import WireGuard, get_client_ip

r = Redis.from_url(settings.REDIS_URL)


class IndexView(TemplateView):
    template_name = 'index.html'


class ConnectionPackBaseView(FormView):
    model = PeerConfig

    def __init__(self, *args, **kwargs):
        self.wg = WireGuard()
        self.redis = r

    def get_qr_code(self, config):
        raw_config = render_to_string(
            'partials/_config.txt', {'config': config}
        )
        qr = QRCode()
        qr.add_data(raw_config)
        qr.make(fit=True)

        # render peer config
        img = qr.make_image(
            fill_color="black", back_color="white"
        )

        buf = BytesIO()
        img.save(buf, format="PNG")
        return b64encode(buf.getvalue()).decode("utf-8")


class ConnectionPackCreateView(ConnectionPackBaseView):
    form_class = ConnectionPackForm
    template_name = 'generate.html'

    def post(self, request, *args, **kwargs):
        ctx = {}
        form = ConnectionPackForm(request.POST)

        if form.is_valid():
            private_key = self.wg.gen_privkey()
            public_key = self.wg.get_pubkey(private_key)
            client_ip = get_client_ip(request)

            props = dict(interface_public_key=public_key,
                         interface_private_key=private_key,
                         server_public_key=self.wg.server_public_key,
                         server_endpoint=self.wg.server_endpoint,
                         server_allowed_ips=self.wg.server_allowed_ips,
                         server_dns=self.wg.server_dns,
                         client_ip=client_ip)

            hits = self.redis.get(client_ip)
            hits = 0 if hits is None else int(hits)

            # allow to generate up to 3 configs per ip per hour
            if hits >= 3 and not request.user.is_staff:
                messages.error(
                    request, "You've hit the limit of generated configs. Please check back in an hour."
                )

                ctx['form'] = form
                return render(request, 'generate.html', ctx)

            # bump hit number, and the cooldown TTL
            # so when it reaches the limit it starts when someone has hit it
            self.redis.set(client_ip, hits+1, ex=3600)

            props['interface_address'] = self.wg.get_address()
            config = PeerConfig(**props)
            config.save()

            # add peer on wg server
            self.wg.add_peer(public_key, config.interface_address)

            ctx['qr_code_b64'] = self.get_qr_code(config)
            ctx['config'] = config
            return render(request, 'config.html', ctx)

        ctx['form'] = form
        return render(request, 'generate.html', ctx)


class ConnectionPackLookupView(ConnectionPackBaseView):
    form_class = ConnectionPackLookupForm
    template_name = 'lookup.html'

    def post(self, request, *args, **kwargs):
        ctx = {}
        form = ConnectionPackLookupForm(request.POST)

        if form.is_valid():
            private_key = form.cleaned_data.get('private_key', '')

            config_exists = PeerConfig.objects.filter(
                interface_private_key=private_key
            ).exists()

            if not config_exists:
                messages.error(
                    request, "Config not found!"
                )

                ctx['form'] = form
                return render(request, 'lookup.html', ctx)

            config = PeerConfig.objects.get(
                interface_private_key=private_key
            )

            ctx['qr_code_b64'] = self.get_qr_code(config)
            ctx['config'] = config
            return render(request, 'config.html', ctx)

        ctx['form'] = form
        return render(request, 'lookup.html', ctx)
