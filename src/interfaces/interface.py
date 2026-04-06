from .factory import InterfaceFactory

class Interface():
    def __init__(self, config, bus):
        self.interface = None
        self.interface_name = None
        self.config = config
        self.bus = bus
        
    async def init_interface(self):
        self.interface_name = self.config.get("interface")
        if self.interface_name:
            print("Interface:", self.interface_name)
            
        else:
            print("No interface set in config")
            return
        self.interface = InterfaceFactory.create(self.interface_name)
        await self.interface.init(self.config, self.bus)
