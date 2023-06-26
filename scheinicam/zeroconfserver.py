import socket
from zeroconf import IPVersion, ServiceInfo, Zeroconf

class ZeroconfServer:
    def __init__(self, name, port):
        ''' Initialize ZeroconfServer '''
        self.name = name
        self.port = port
        self.info = None

    def register_service(self):
        ''' Register service with zeroconf '''
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        self.info = ServiceInfo(
            "_http._tcp.local.",
            f"{self.name}._http._tcp.local.",
            addresses=[socket.inet_aton(ip_address)],
            port=self.port,
            server=f"{hostname}.local.",
        )
        zeroconf = Zeroconf(ip_version=IPVersion.All)
        zeroconf.register_service(self.info)
        print(f"Registered service: {self.name} ({ip_address}:{self.port})")

    def unregister_service(self):
        ''' Unregister service with zeroconf '''
        if self.info:
            zeroconf = Zeroconf(ip_version=IPVersion.All)
            zeroconf.unregister_service(self.info)
            zeroconf.close()
            print(f"Unregistered service: {self.name}")
