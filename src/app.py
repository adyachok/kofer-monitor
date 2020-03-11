#!/usr/bin/env python
import faust

from kubernetes import client
from openshift.dynamic import exceptions

from config import Config
from models.faust_dao import DeploymentConfigInfo
from services.serializers import DeploymentConfigInfoSerializer
from openshift_utils.tracker import DeploymetConfigManager
from utils.logger import get_logger


logger = get_logger('app')

config = Config()


app = faust.App('monitor', broker=config.KAFKA_BROKER_URL, web_port=6067)
topic = app.topic('model-updates', value_type=DeploymentConfigInfo)
manager = DeploymetConfigManager(namespace=config.NAMESPACE)
cache = {}


@app.timer(interval=config.REQUEST_INTERVAL)
async def monitor(app):
    try:
        logger.info('Checking the cluster state.')
        info = manager.track_changes()
        for dc_info in info:
            cached = cache.get(dc_info.name)
            if not cached or dc_info != cached:
                logger.info(dc_info.to_dict())
                cache[dc_info.name] = dc_info
                await topic.send(
                    value=DeploymentConfigInfoSerializer(dc_info)()
                )
    except (client.rest.ApiException, exceptions.UnauthorizedError) as e:
        logger.info(e)


if __name__ == '__main__':
    app.main()
