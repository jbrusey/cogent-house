"""
SSH Tunnelling functionality via paramiko

This set of classes sets up an ssh tunnel, While it would be simpler
to use the Popen function. Difficulties detecting when the network was
down, connection failures etc.  This made any error handing in the push
function somewhat convoluted.

Hopefully this approach is better.

Code based on the Paramiko Demos.

.. moduleauthor:: Daniel Goldsmith <djgoldsmith@googlemail.com>
.. versionadded:: 0.3
"""

#import paramiko
import SocketServer
import select
#import socket

import logging
log = logging.getLogger("__name__")
log.setLevel(logging.DEBUG)

class ForwardServer (SocketServer.ThreadingTCPServer):
    """Subclass Socket server to run in daemon mode"""
    daemon_threads = True
    allow_reuse_address = True
    

class Handler (SocketServer.BaseRequestHandler):
    """
    Subclassed handler to deal with requests
    """
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host, self.chain_port),
                                                   self.request.getpeername())
        except Exception, e:
            log.warning('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                                  self.chain_port,
                                                                  repr(e)))
            return
        if chan is None:
            log.warning('Incoming request to %s:%d was rejected by the SSH server.' %
                        (self.chain_host, self.chain_port))
            return

        log.debug('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
                                                              chan.getpeername(),
                                                              (self.chain_host, self.chain_port)))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)
                
        peername = self.request.getpeername()
        chan.close()
        self.request.close()
        log.debug('Tunnel closed from %r' % (peername,))


def forward_tunnel(local_port, remote_host, remote_port, transport):
    # this is a little convoluted, but lets me configure things for the Handler
    # object.  (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHander (Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport
    theServer = ForwardServer(('', local_port), SubHander)
    return theServer

