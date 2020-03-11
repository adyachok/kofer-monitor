# Monitor

### Description
The microservice will track for changes in the projects. It should notify new
models added (pods) and transmit this data through Kafka topics to interested
listeners.

### Useful links
- [Access OpenShift API from pod container](https://developers.redhat.com/blog/2019/07/25/controlling-red-hat-openshift-from-an-openshift-pod/)
  implemented in _tracker.py:DeploymetConfigManager.get_openshift_client_
  
### Installation
  1. Create Kafka topic:
  
    oc exec -it bus-kafka-1 -c kafka -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic model-updates --create --partitions 3 --replication-factor 3