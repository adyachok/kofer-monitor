# Monitor

### Description
The microservice will track for changes in the projects. It should notify new
models added (pods) and transmit this data through Kafka topics to interested
listeners.

### Useful links
- [Access OpenShift API from pod container](https://developers.redhat.com/blog/2019/07/25/controlling-red-hat-openshift-from-an-openshift-pod/)
  implemented in _tracker.py:DeploymetConfigManager.get_openshift_client_