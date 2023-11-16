#!/usr/bin/env bash

# Download the data
wget http://alt.qcri.org/semeval2016/task1/data/uploads/sts2016-english-with-gs-v1.0.zip
# create data directory if it doesn't exist
mkdir -p data
# unzip the data into the data directory
unzip sts2016-english-with-gs-v1.0.zip -d data
# remove the zip file
rm sts2016-english-with-gs-v1.0.zip
