# -*- mode: ruby -*-
# vi: set ft=ruby :
 
$script = <<SCRIPT

wget -O - http://tinyprod.net/repos/debian/tinyprod.key | sudo apt-key add -

# add tinyprod to apt sources

tee -a /etc/apt/sources.list >/dev/null <<APTEOF
deb http://tinyprod.net/repos/debian squeeze main
deb http://tinyprod.net/repos/debian msp430-46 main
APTEOF

# update apt database

sudo apt-get update -q

# upgrade all packages before we start

sudo apt-get upgrade -qy

# install tinyos (squeeze)

sudo apt-get install nesc tinyos-tools msp430-46 avr-tinyos -qy

# Install tos essentials

sudo apt-get install autoconf automake gawk build-essential libtool \
    linux-image-extra-virtual \
    python-dev openjdk-6-jdk graphviz ntp -qy 

# remove anything unnecessary

sudo apt-get autoremove -qy

# Get the code from the TinyOS release repository:

wget -q http://github.com/tinyos/tinyos-release/archive/tinyos-2_1_2.tar.gz
tar xf tinyos-2_1_2.tar.gz
sudo mv tinyos-release-tinyos-2_1_2 /opt/tinyos-main


# tinyos environment script

cat >/opt/tinyos-main/tinyos.sh <<'EOF'
# script for profile.d for bash shells, adjusted for each users
# installation by substituting @prefix@ for the actual tinyos tree
# installation

export TOSROOT=
export TOSDIR=
export MAKERULES=

TOSROOT="/opt/tinyos-main"
TOSDIR="$TOSROOT/tos"
CLASSPATH=$CLASSPATH:$TOSROOT/support/sdk/java/tinyos.jar
PYTHONPATH=$PYTHONPATH:$TOSROOT/support/sdk/python
MAKERULES="$TOSROOT/support/make/Makerules"
echo "Setting up for TinyOS"

export TOSROOT
export TOSDIR
export CLASSPATH
export PYTHONPATH
export MAKERULES

# Extend path for java
type java >/dev/null 2>/dev/null || PATH=`/usr/local/bin/locate-jre --java`:$PATH
type javac >/dev/null 2>/dev/null || PATH=`/usr/local/bin/locate-jre --javac`:$PATH
echo $PATH | grep -q /usr/local/bin ||  PATH=/usr/local/bin:$PATH
EOF

cat >>/home/vagrant/.bashrc <<'EOF'
#set-up TinyOS
if [ -f /opt/tinyos-main/tinyos.sh ];  then
    . /opt/tinyos-main/tinyos.sh
fi
EOF

# Source the env set up java

source /opt/tinyos-main/tinyos.sh
sudo tos-install-jni

sudo chown -R vagrant:vagrant /opt/tinyos-main/

# give vagrant access to dialout

sudo usermod -a -G dialout vagrant


echo "=== Installation almost complete - use 'vagrant reload' until boots without installing new packages ==="

SCRIPT
 
VAGRANTFILE_API_VERSION = "2"
 
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.ssh.forward_agent = true

  config.vm.provider :virtualbox do |vb|
    # not sure if the following is needed
    vb.customize ["storageattach", :id,
                  "--storagectl", "SATAController",
                  "--port", "1",
                  "--device", "0",
                  "--type", "dvddrive",
                  "--medium", "emptydrive"]
    
    # set the USB to v3, paravirtprovider to kvm

    vb.customize ["modifyvm", :id, "--usb", "on",
                  "--usbxhci", "on",
                  "--paravirtprovider", "kvm"]
    
    # filter rule to capture any telos mote
    
    vb.customize ["usbfilter", "add", "0", 
                  "--target", :id, 
    	          "--name", "MTM-CM5000MSP",
	          "--vendorid", "0x0403",
	          "--productid", "0x6001"]
  end
  
  config.vm.provision "shell", inline: $script
end
