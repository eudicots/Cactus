#!/bin/sh

rm -Rf /tmp/catus-test
cactus create /tmp/catus-test

cd /tmp/catus-test

cactus build

echo '{% extends "base.html" %}
{% block content %}
Welcome to Cactus! It worked!
{% endblock %}' > pages/index.html

cactus serve

echo '{
    "aws-access-key": "AKIAIV5C2U4YJM6DRMRQ", 
    "aws-bucket-name": "cactus-test-test", 
    "aws-bucket-website": "cactus-test-test.s3-website-us-east-1.amazonaws.com"
}' > config.json

cactus deploy

curl http://cactus-test-test.s3-website-us-east-1.amazonaws.com/versions.txt

