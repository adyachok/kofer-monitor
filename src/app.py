#!/usr/bin/env python
import asyncio
import os

from kubernetes import client
from openshift.dynamic import exceptions

from tracker import DeploymetConfigManager
from utils.logger import get_logger


logger = get_logger('app')


REQUEST_INTERVAL = os.getenv('ZZ_MONITOR_REQUEST_INTERVAL')
REQUEST_INTERVAL = int(REQUEST_INTERVAL) if REQUEST_INTERVAL else 2
NAMESPACE = os.getenv('NAMESPACE')
if not NAMESPACE:
    raise Exception('Environment variable NAMESPACE is not defined')


async def track():
    """Tracks changes in cluster."""
    cache = {}
    try:
        manager = DeploymetConfigManager(namespace=NAMESPACE)
        while True:
            logger.info('Checking the cluster state.')
            info = manager.track_changes()
            for dc_info in info:
                cached = cache.get(dc_info.name)
                if not cached or dc_info != cached:
                    logger.info(dc_info.to_dict())
                    # logger.info(dc_info.__hash__())
                    cache[dc_info.name] = dc_info
            await asyncio.sleep(REQUEST_INTERVAL)
    except (client.rest.ApiException, exceptions.UnauthorizedError) as e:
        logger.info(e)


if __name__ == '__main__':
    asyncio.run(track())
