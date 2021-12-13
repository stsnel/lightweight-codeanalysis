#!/bin/bash
# Basic installation for ubuntu 20.04
## Changes to package install instructions: 
## - also install required python3-distutils
## - configure storage_path

sudo apt update
sudo apt install -y libpq5 redis-server nginx supervisor python3-distutils python3-pip
sudo pip3 install --upgrade requests==2.26.0
wget https://packaging.ckan.org/python-ckan_2.9-py3-focal_amd64.deb
sudo dpkg -i python-ckan_2.9-py3-focal_amd64.deb
sudo apt install -y postgresql
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres createdb -O ckan_default ckan_default -E utf-8
sudo apt install -y solr-tomcat
sudo perl -pi.bak -e 's/port=\"8080\"/port=\"8983\"/g' /etc/tomcat9/server.xml
sudo mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.bak
sudo ln -s /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
sudo systemctl restart tomcat9
sudo perl -pi.bak -e 's/^ckan\.site_url =/ckan.site_url = http:\/\/localhost:8080/g' /etc/ckan/default/ckan.ini
sudo perl -pi.bak -e 's/^\#ckan\.storage_path/ckan.storage_path/' /etc/ckan/default/ckan.ini
sudo chmod -R 0777 /var/lib/ckan
sudo ckan db init
sudo supervisorctl reload
sudo service nginx restart

# Create test users and data
. /usr/lib/ckan/default/bin/activate
cd /usr/lib/ckan/default/src/ckan
ckan -c /etc/ckan/default/ckan.ini seed basic
ckan -c /etc/ckan/default/ckan.ini seed user
ckan -c /etc/ckan/default/ckan.ini sysadmin add tester
