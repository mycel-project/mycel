from .factory import InterfaceFactory

class Interface():
    def __init__(self, config, bus, services = {}):
        self.interface = None
        self.interface_name = None
        self.config = config
        self.bus = bus
        self.services = services
        
    async def init_interface(self):
        self.interface_name = self.config.get("interface")
        if self.interface_name:
            print("Interface:", self.interface_name)
            
        else:
            print("No interface set in config")
            return
        self.interface = InterfaceFactory.create(self.interface_name)
        await self.interface.init(self.config, self.bus, self.services)
