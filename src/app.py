#!/usr/bin/env python
import logging
import asyncio

from kubernetes import client, config
from openshift.dynamic import DynamicClient, exceptions

from tracker import DeploymetConfigManager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app.py')


async def track():
    cache = {}
    k8s_client = config.new_client_from_config()
    i = 0
    while True:
        try:
            dyn_client = DynamicClient(k8s_client)
            manager = DeploymetConfigManager(client=dyn_client,
                                             namespace='zz-test')
            info = manager.track_changes()
            for dc_info in info:
                cached = cache.get(dc_info.name)
                if not cached or dc_info != cached:
                    logger.info(dc_info.to_dict())
                    logger.info(dc_info.__hash__())
                    cache[dc_info.name] = dc_info
                    i += 1
                    await asyncio.sleep(2)
        except (client.rest.ApiException, exceptions.UnauthorizedError) as e:
            logger.info(e)


if __name__ == '__main__':
    asyncio.run(track())
