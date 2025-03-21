#!/usr/bin/env bash
# stop script on error
set -e

# Check to see if root CA file exists, download if not
if [ ! -f ./root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
fi

# install AWS Device SDK for Java if not already installed
if [ ! -d ./aws-iot-device-sdk-java-v2 ]; then
  printf "\nInstalling AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-java-v2.git --recursive
  cd aws-iot-device-sdk-java-v2
  mvn versions:use-latest-versions -Dincludes="software.amazon.awssdk.crt*"
  mvn clean install -Dmaven.test.skip=true
  cd ..
fi

# run pub/sub sample app using certificates downloaded in package
printf "\nRunning pub/sub sample application...\n"
cd aws-iot-device-sdk-java-v2
mvn exec:java -pl samples/BasicPubSub -Dexec.mainClass=pubsub.PubSub -Dexec.args='--endpoint a3qw7ret33putt-ats.iot.us-east-1.amazonaws.com --client_id sdk-java --topic sdk/test/java --ca_file ../root-CA.crt --cert ../GDA.cert.pem --key ../GDA.private.key'