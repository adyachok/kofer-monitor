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
