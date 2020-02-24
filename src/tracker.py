import logging
import time

from kubernetes import client, config
from openshift.dynamic import DynamicClient, exceptions


class DeploymentConfigInfo:
    __slots__ = ['name', 'image_triggers', 'latest_version']

    def __init__(self, name, latest_version):
        self.name = name
        self.latest_version = latest_version
        self.image_triggers = []

    def __repr__(self):
        return f'DeploymentConfigInfo(name={self.name}, ' \
               f'latest_versiot={self.latest_version})'

    def to_dict(self):
        return {
            'name': self.name,
            'latest_version': self.latest_version,
            'image_triggers': [trigger.to_dict() for trigger
                               in self.image_triggers]
        }

    def has_image_change(self):
        return any([trigger.is_image_change() for trigger
                    in self.image_triggers])

    def __eq__(self, other):
        if self.name != other.name:
            return False
        # If there is no difference in sets
        if not set(self.image_triggers).difference(other.image_triggers):
            return True
        return False

    def prune(self):
        # Remove not image change triggers
        self.image_triggers = [trigger for trigger in self.image_triggers
                               if trigger.is_image_change()]
        return self

    def __hash__(self):
        return hash(repr(self))


class ImageTriggerInfo:
    __slots__ = ['image_name', 'trigger_type']

    def __init__(self, image_name, trigger_type):
        self.image_name = image_name
        self.trigger_type = trigger_type

    def __repr__(self):
        return f'ImageTriggerInfo(image_name={self.image_name}, ' \
               f'trigger_type={self.trigger_type})'

    def is_image_change(self):
        return self.trigger_type == 'ImageChange'

    def to_dict(self):
        return {
            'image_name': self.image_name,
            'trigger_type': self.trigger_type
        }

    def __eq__(self, other):
        return self.image_name == other.image_name

    def __hash__(self):
        return hash(repr(self))


class DeploymetConfigManager:
    """Class handles connection to OpenShift and gets a list of deployment
    configs, then processes it into info objects.
    """
    def __init__(self, client, namespace):
        self.client = client
        self.namespace = namespace

    def _get_deployment_configs_list(self):
        """Queries and returns DeploymentConfigList object:
        :param client: DynamicClient from openshift package
        :param namespace: OpenShift project name
        :return: DeploymentConfigList
        """
        v1_delpoyment_config_list = self.client.resources.get(
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


if __name__ == '__main__':
    cache = {}
    k8s_client = config.new_client_from_config()
    i = 0
    while (i < 10):
        try:
            dyn_client = DynamicClient(k8s_client)
            manager = DeploymetConfigManager(client=dyn_client,
                                             namespace='zz-test')
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