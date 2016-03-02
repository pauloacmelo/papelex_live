# ssh suporte@192.168.24.45
# suporte@123
# su - root
# p@55w0rd
# Install sudo!
aptitude install sudo
cat > /etc/sudoers <<- EOM
# /etc/sudoers
#
# This file MUST be edited with the 'visudo' command as root.
#
# See the man page for details on how to write a sudoers file.
#

Defaults        env_reset

# Host alias specification

# User alias specification

# Cmnd alias specification

# User privilege specification
root    ALL=(ALL) ALL
EOM
sudo apt-get install xz-utils

# Install dependencies
apt-get update; apt-get upgrade
sudo apt-get install build-essential
sudo apt-get install -y unzip
# git
sudo apt-get install -y git
# node
curl -sL https://deb.nodesource.com/setup_5.x | bash -
sudo apt-get install -y nodejs
npm shrinkwrap
# rethinkdb
echo "deb http://download.rethinkdb.com/apt `lsb_release -cs` main" | sudo tee /etc/apt/sources.list.d/rethinkdb.list
wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y rethinkdb
# python
sudo apt-get install -y python3
sudo apt-get install -y python3-pip
pip3 install rethinkdb

# Oracle
sudo apt-get install -y python-dev build-essential libaio1
# local scp -r ~/Downloads/instantclient-basic-linux-12.1.0.2.0.zip suporte@192.168.24.45:/home/suporte/
# local scp -r ~/Downloads/instantclient-sdk-linux-12.1.0.2.0.zip suporte@192.168.24.45:/home/suporte/
# local scp -r ~/Downloads/instantclient-sqlplus-linux-12.1.0.2.0.zip suporte@192.168.24.45:/home/suporte/
cd /home/suporte
mkdir /opt/ora
unzip instantclient-sdk-linux-12.1.0.2.0.zip -d /opt/ora 
unzip instantclient-basic-linux-12.1.0.2.0.zip -d /opt/ora
unzip instantclient-sqlplus-linux-12.1.0.2.0.zip -d /opt/ora/
export ORACLE_HOME=/opt/ora/instantclient_12_1/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME
cd $ORACLE_HOME && ln -s libclntsh.so.12.1 libclntsh.so
ln -s /opt/ora/instantclient_12_1/sqlplus /usr/bin/sqlplus
mkdir -p $ORACLE_HOME/network/admin
cat > $ORACLE_HOME/network/admin/tnsnames.ora <<- EOM
WINT =
  (DESCRIPTION =
    (ADDRESS_LIST =
      (ADDRESS = (PROTOCOL = TCP)(HOST = 192.168.24.57)(PORT = 1521))
    )
    (CONNECT_DATA =
      (SID = WINT)
    )
  )

TESTE =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = 192.168.24.58)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = TESTE)
    )
  )
EOM
pip3 install cx_Oracle

# setup iptables (ACCEPT all the stuff)
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

python3
import rethinkdb as r
conn = r.connect('localhost', 28015).repl()
r.db_create('papelex').run(conn)
conn = r.connect('localhost', 28015, db='papelex').repl()
conn.close()
r.table_create('orders').run(conn)
r.table_create('goal').run(conn)
conn.close()