from werkzeug.exceptions import Forbidden
import ipaddress


class LocalhostAuthorizationMiddleware():
    def __init__(self):
        pass

    def check(self):
        remote_ip = ipaddress.ip_address(request.remote_addr)
        if remote_ip.is_loopback is False:
            raise Forbidden('Not authorized.')
