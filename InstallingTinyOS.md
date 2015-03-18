echo "deb http://tinyos.stanford.edu/tinyos/dists/ubuntu natty main" | sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get install tinyos-2.1.2
wget http://github.com/tinyos/tinyos-release/archive/tinyos-2_1_2.tar.gz
tar xf tinyos-2\_1\_2.tar.gz
mv tinyos-release-tinyos-2\_1\_2 tinyos-main-read-only
sudo mv tinyos-main-read-only /opt/
cat >/opt/tinyos-main-read-only/tinyos.sh <<'EOF'
# script for profile.d for bash shells, adjusted for each users
# installation by substituting @prefix@ for the actual tinyos tree
# installation point.

export TOSROOT=
export TOSDIR=
export MAKERULES=

TOSROOT="/opt/tinyos-main-read-only"
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
cat >>~/.profile <<'EOF'
#set-up TinyOS
if [-f /opt/tinyos-main-read-only/tinyos.sh ](.md);  then
> . /opt/tinyos-main-read-only/tinyos.sh
fi
EOF
sudo tos-install-jni
sudo usermod -a -G dialout $USER}}}

 # Download the github version:
    {{{
    }}}
 # The following installs a script in `/opt/tinyos-main-read-only/tinyos.sh`
        {{{
        }}} 
 # Add to your `.profile` set-up for TinyOS:
        {{{
        }}}
 # Run 
     {{{
     }}}
     to get java set up right. 
 # With some versions of ubuntu you may have difficulties writing to the serial ports, in this case you need to add your user to the 'dialout' group.  This change will only take place after you log out and back in again.
    {{{
    }}}
    
 ```