#!/bin/bash

sudo apt-get install -y libzmq3-dev
if ! [ -x "$(command -v pip)" ]; then
  sudo apt-get install -y pip
fi
sudo pip install pyzmq