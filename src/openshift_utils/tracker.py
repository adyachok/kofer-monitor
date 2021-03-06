import os
import time

from kubernetes import client, config
from openshift.dynamic import DynamicClient, exceptions

from models.dao import DeploymentConfigInfo, ImageTriggerInfo
from utils.logger import get_logger


logger = get_logger('tracker')


class DeploymetConfigManager:
    """Class handles connection to OpenShift and gets a list of deployment
    configs, then processes it into info objects.
    """
    def __init__(self, namespace):
        self.dyn_client = self.get_openshift_client()
        self.namespace = namespace

    def _get_deployment_configs_list(self):
        """Queries and returns DeploymentConfigList object:
        :param client: DynamicClient from openshift package
        :param namespace: OpenShift project name
        :return: DeploymentConfigList
        """
        v1_delpoyment_config_list = self.dyn_client.resources.get(
            api_version='v1', kind='DeploymentConfig')
        return v1_delpoyment_config_list.get(namespace=self.namespace)

    def _process_deployment_config_list(self, deployment_config_list):
        """Parses DeploymentConfigList data
        :param deployment_config_list:
        :return: DeploymentConfigInfo object, if we convert it to dict it will
        look like:
        {'name': 'kafdrop',
         'latest_version': 27,
         'image_triggers': [
                {'image_name': '1.2.3.4:5000/z-test/kafdrop@sha256:46f005e...',
                'trigger_type': 'ImageChange'}]
         }

          or

        {'name': 'tweet-producer',
         'latest_version': 14,
         'image_triggers': [
                {'image_name': None, 'trigger_type': 'ConfigChange'}]
        }
        """
        parsed_data = []
        for item in deployment_config_list.get('items', []):
            dc_name = item.get('metadata').get('name')
            # Select only model's deployment configs. Model deployment config
            # name should start with 'mod-'
            if not dc_name.startswith('mod-'):
                continue
            _status = item.get('status', {})
            _details = _status.get('details', {})
            _causes = _details.get('causes', {})
            dc_latest_version = _status.get('latestVersion')
            dc_info = DeploymentConfigInfo(dc_name, dc_latest_version)
            for _resource in _causes:
                _image_trigger = _resource.get('imageTrigger', {})
                image_name = _image_trigger.get('from', {}).get('name')
                trigger_type = _resource.get('type')
                image_trigger_info = ImageTriggerInfo(image_name,
                                                      trigger_type)
                dc_info.image_triggers.append(image_trigger_info)
            parsed_data.append(dc_info)
        return parsed_data

    def filter_changes(self, info):
        # Remove not image change triggers
        info = [dc_info.prune() for dc_info in info]
        # Get only those with image change
        info = filter(lambda dc_info: dc_info.has_image_change(), info)
        return info

    def track_changes(self):
        dc_list = self._get_deployment_configs_list()
        info = self._process_deployment_config_list(dc_list)
        info = self.filter_changes(info)
        return info

    def get_openshift_client(self):
        # Check if code is running in OpenShift
        if "OPENSHIFT_BUILD_NAME" in os.environ:
            config.load_incluster_config()
            file_namespace = open(
                "/run/secrets/kubernetes.io/serviceaccount/namespace", "r"
            )
            if file_namespace.mode == "r":
                namespace = file_namespace.read()
                logger.info("namespace: %s\n" % (namespace))
        else:
            config.load_kube_config()

        # Create a client config
        k8s_config = client.Configuration()
        k8s_client = client.api_client.ApiClient(configuration=k8s_config)
        return DynamicClient(k8s_client)


if __name__ == '__main__':
    cache = {}
    i = 0
    while (i < 10):
        try:
            manager = DeploymetConfigManager(namespace='zz-test')
            info = manager.track_changes()
            for dc_info in info:
                cached = cache.get(dc_info.name)
                if not cached or dc_info != cached:
                    print(dc_info.to_dict())
                    print(dc_info.__hash__())
                    cache[dc_info.name] = dc_info
                    i += 1
                    time.sleep(2)
        except (client.rest.ApiException, exceptions.UnauthorizedError) as e:
            print(e)
