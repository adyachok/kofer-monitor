# Monitor

![alt text][logo]

[logo]: img/lifeguard%20tower.png "Title"

### Description
The Monitor microservice tracks changes of data science models builds. In case 
model service update or new model service (pod) creation it submits an event to
through Kafka topics to interested listeners.

**DISCLAIMER** the service is the integral part of ZZ project, but because the 
project is build using **service choreography architecture pattern** there are 
no strong, tight relations in it. This means that every part of ZZ can be 
modified - removed - rewritten accordingly to the needs of customer.

### Interaction process


![alt text][schema]

[schema]: img/how%20monitor%20is%20working.png "Title"

  
### Installation

#### Run locally


To run locally application requires Kafka broker.

To install seamlessly **Kafka** broker we recommend 
[Kafka-docker](https://github.com/wurstmeister/kafka-docker) project. 
In the project you can find **docker-compose-single-broker.yml**

We suggest to create next alias

```bash alias kafka="docker-compose --file {PATH_TO}/kafka-docker/docker-compose-single-broker.yml up```

#### For local and dev/prod installations

  1. Create Kafka topic:
  
    oc exec -it bus-kafka-1 -c kafka -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic model-updates --create --partitions 3 --replication-factor 3
    
  2. OpenShift token should be available inside container. Please, check the following
  link for more information [Service Accounts](https://docs.openshift.com/container-platform/3.11/dev_guide/service_accounts.html)

### Debugging

We created instance of [Kafdrop](https://github.com/obsidiandynamics/kafdrop) with
the aim to facilitate debugging process. The running example instance can be found
in [BIX ZZ project](https://kafdrop-zz-test.22ad.bi-x.openshiftapps.com/)

Kafdrop has reach interface which helps a lot in tracking messages / events.

![alt text][kafdrop]

[kafdrop]: img/kafdrop.png "Title"

Yoiu can easily trace / read all messages in any topic:

![alt text][kafdrop_read]

[kafdrop_read]: img/kafdrop%202.png "Title"

 
### Useful links
- [Access OpenShift API from pod container](https://developers.redhat.com/blog/2019/07/25/controlling-red-hat-openshift-from-an-openshift-pod/)
  implemented in _tracker.py:DeploymetConfigManager.get_openshift_client_