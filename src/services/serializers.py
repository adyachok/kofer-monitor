from models import dao, faust_dao


class DeploymentConfigInfoSerializer:

    def __init__(self, deployment_config_info: dao.DeploymentConfigInfo):
        self.deployment_config_info = deployment_config_info

    def __call__(self):
        return faust_dao.DeploymentConfigInfo(
            name=self.deployment_config_info.name,
            latest_version=self.deployment_config_info.latest_version,
            image_triggers=[ImageTriggerInfoSerializer(it)() for it
                            in self.deployment_config_info.image_triggers]
        )


class ImageTriggerInfoSerializer:

    def __init__(self, image_trigger_info: dao.ImageTriggerInfo):
        self.image_trigger_info = image_trigger_info

    def __call__(self):
        return faust_dao.ImageTriggerInfo(
            image_name=self.image_trigger_info.image_name,
            trigger_type=self.image_trigger_info.trigger_type
        )
