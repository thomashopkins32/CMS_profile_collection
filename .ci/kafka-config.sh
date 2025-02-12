#!/bin/bash

set -veo pipefail

# Kafka config:
cat << EOF > kafka.yml
---
abort_run_on_kafka_exception: false
bootstrap_servers:
    - localhost:9092
runengine_producer_config:
    security.protocol: PLAINTEXT
EOF

sudo mkdir -v -p /etc/bluesky/
sudo mv -v kafka.yml /etc/bluesky/kafka.yml  # TODO: put it into the home directory via an env var
cat /etc/bluesky/kafka.yml