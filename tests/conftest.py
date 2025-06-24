import sys
import types

# Stub tinyos3.message and submodules
pkg = types.ModuleType('tinyos3')
msg_mod = types.ModuleType('tinyos3.message')
class DummySource:
    def isDone(self):
        return False
class DummyMoteIF:
    def __init__(self, *args, **kwargs):
        pass
    def addSource(self, source):
        return DummySource()
    def addListener(self, *args, **kwargs):
        pass
    def sendMsg(self, *args, **kwargs):
        pass
    def finishAll(self):
        pass
msg_mod.MoteIF = types.SimpleNamespace(MoteIF=DummyMoteIF)

msg_message_mod = types.ModuleType('tinyos3.message.Message')
class DummyMessage:
    def __init__(self, data=b"", addr=None, gid=None, base_offset=0, data_length=None):
        if isinstance(data, str):
            data = data.encode()
        self._data = bytearray(data)
    def dataGet(self):
        return bytes(self._data)
    def offset_data(self, i):
        return 0
    def amTypeSet(self, t):
        self._amType = t
    def get_amType(self):
        return getattr(self, "_amType", 0)
    def getUIntElement(self, *args, **kwargs):
        return 0
    def setUIntElement(self, *args, **kwargs):
        pass
    def getFloatElement(self, *args, **kwargs):
        return 0.0
    def setFloatElement(self, *args, **kwargs):
        pass
msg_message_mod.Message = DummyMessage
msg_mod.Message = msg_message_mod
pkg.message = msg_mod
sys.modules.setdefault('tinyos3', pkg)
sys.modules.setdefault('tinyos3.message', msg_mod)
sys.modules.setdefault('tinyos3.message.Message', msg_message_mod)

# Stub paho.mqtt.client
mqtt_client_mod = types.ModuleType('paho.mqtt.client')
class DummyClient:
    def loop_start(self):
        pass
    def connect(self, host="", port=0, keepalive=0):
        pass
    def publish(self, *args, **kwargs):
        pass
mqtt_client_mod.Client = DummyClient
mqtt_mod = types.ModuleType('paho.mqtt')
mqtt_mod.client = mqtt_client_mod
sys.modules.setdefault('paho', types.ModuleType('paho'))
sys.modules.setdefault('paho.mqtt', mqtt_mod)
sys.modules.setdefault('paho.mqtt.client', mqtt_client_mod)
