#!/bin/bash

set -veo pipefail

# Per https://stackoverflow.com/a/66982842:
sudo echo "127.0.0.1 info.cms.nsls2.bnl.gov" | sudo tee -a /etc/hosts
cat /etc/hosts

# Copy config files into the dummy IPython profile:
mkdir -v -p ~/.ipython/profile_test/startup/
cp -v startup/.cms_config ~/.ipython/profile_test/startup/

# Create the /nsls2 dir tree:
mkdir -v -p /nsls2
