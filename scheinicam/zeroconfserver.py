import socket
from zeroconf import IPVersion, ServiceInfo, Zeroconf

class ZeroconfServer:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.info = None

    def register_service(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        deviceType = '_http'
        desc = {'deviceName': self.name}
        # desc = {}

        self.info = ServiceInfo(deviceType + "._tcp.local.",
                        self.name + "." + deviceType +"._tcp.local.",
                        self.port, 0, 0,
                        addresses=socket.inet_aton(ip_address)
                        )

        zeroconf = Zeroconf()
        zeroconf.register_service(self.info)
        print(f"Registered service: {self.name} ({ip_address}:{self.port})")

    def unregister_service(self):
        if self.info:
            zeroconf = Zeroconf(ip_version=IPVersion.All)
            zeroconf.unregister_service(self.info)
            zeroconf.close()
            print(f"Unregistered service: {self.name}")
