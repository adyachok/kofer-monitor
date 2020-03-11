import logging
import os

from utils.logger import get_logger


logger = get_logger('config')


class Config:

    REQUEST_INTERVAL = None
    NAMESPACE = None
    KAFKA_BROKER_URL = None

    def __init__(self):
        """
        Initiates microservice configuration
        :return: configuration object
        """
        self.REQUEST_INTERVAL = self._set_request_interval()
        self.NAMESPACE = self._set_namespace()
        self.KAFKA_BROKER_URL = self._set_kafka_url()

    def _set_request_interval(self):
        request_interval = os.getenv('ZZ_MONITOR_REQUEST_INTERVAL')
        return int(request_interval) if request_interval else 2

    def _set_namespace(self):
        namespace = os.getenv('NAMESPACE')
        if not namespace:
            raise Exception('Environment variable NAMESPACE is not defined')
        return namespace

    def _set_kafka_url(self):
        kafka_broker_url = os.getenv('KAFKA_BROKER_URL')
        if not kafka_broker_url:
            kafka_broker_url = 'kafka://localhost'
        return kafka_broker_url
