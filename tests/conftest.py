import sys
import types

# Provide minimal tinyos3 stub so that pulp.node imports work during tests
moteif_mod = types.ModuleType("tinyos3.message.MoteIF")


class DummySource:
    def isDone(self):
        return False


class DummyMoteIF:
    def addSource(self, source):
        return DummySource()

    def addListener(self, listener, msgType):
        pass

    def sendMsg(self, source, dest, amType, group, msg):
        pass

    def finishAll(self):
        pass


moteif_mod.MoteIF = DummyMoteIF

message_mod = types.ModuleType("tinyos3.message.Message")


class DummyMessage:
    def __init__(self, data="", addr=None, gid=None, base_offset=0, data_length=None):
        pass


message_mod.Message = DummyMessage

message_pkg = types.ModuleType("tinyos3.message")
message_pkg.MoteIF = moteif_mod
message_pkg.Message = message_mod

package = types.ModuleType("tinyos3")
package.message = message_pkg

sys.modules.setdefault("tinyos3", package)
sys.modules.setdefault("tinyos3.message", message_pkg)
sys.modules.setdefault("tinyos3.message.MoteIF", moteif_mod)
sys.modules.setdefault("tinyos3.message.Message", message_mod)
