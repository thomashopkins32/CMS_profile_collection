#!/bin/bash

sudo echo "127.0.0.1 info.cms.nsls2.bnl.gov" >> /etc/hosts

mkdir -v -p ~/.ipython/profile_test/startup/
cp -v startup/.cms_config ~/.ipython/profile_test/startup/
