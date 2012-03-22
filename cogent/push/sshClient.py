#Test ssh functionality with paramiko

import paramiko
import SocketServer
import select
import threading
import socket

import logging
log = logging.getLogger("__name__")

class ForwardServer (SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True
    

class Handler (SocketServer.BaseRequestHandler):

    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host, self.chain_port),
                                                   self.request.getpeername())
        except Exception, e:
            law.warning('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                                  self.chain_port,
                                                                  repr(e)))
            return
        if chan is None:
            log.warning('Incoming request to %s:%d was rejected by the SSH server.' %
                        (self.chain_host, self.chain_port))
            return

        log.debug('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
                                                              chan.getpeername(), (self.chain_host, self.chain_port)))
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
    #th = threading.Thread(target=theServer.serve_forever)
    #th.daemon=True
    #th.start()
    return theServer


if __name__ == "__main__":
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #Connect to the Remote Server
    print "Connecting to SSH"
    #ssh.connect("127.0.0.1",port=3306,username="dang")

    try:
        ssh.connect("127.0.0.1",username="dang")
        #ssh.connect("127.0.0",username="bern")
        #ssh.connect("cogentee.coventry.ac.uk",username="dang")
    except socket.error,e:
        print "Connection Error {0}".format(e)
        sys.exit(0)
    except paramiko.AuthenticationException:
        print "Authentication Error"
        sys.exit(0)
    
    log.debug("Connection Ok")
    transport = ssh.get_transport()
    
    # #Next setup tunneling
    server = forward_tunnel(3307,"127.0.0.1",3306,transport)
    serverThread = threading.Thread(target=server.serve_forever)
    serverThread.daemon = True
    serverThread.start()

    
    raw_input("Shutdown")
    server.shutdown()
    server.socket.close()
    ssh.close()
