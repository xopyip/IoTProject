import asyncio
import time

from log import logger
from asyncua import Client
from asyncua.common.subscription import Subscription
from device import Factory
from config import Config
from agent import Agent


async def main():
    config = Config()

    agents = []
    subscriptions = []
    try:
        logger.info("Connecting to OPC UA server...")
        async with Client(url=config.get_factory_url()) as client:
            logger.info("Connected!")
            factory = await Factory.create(client)
            logger.info("Enumerating devices...")
            for device in factory.devices:
                if not config.has_agent_connection_str(device.name):
                    config.set_agent_connection_str(device.name,
                                                    input(f"Please provide azure connection string for {device.name}:"))
                connection_str = config.get_agent_connection_str(device.name)
                logger.info(f"Spawning agent for device: {device.name}...")
                agent = Agent(device, connection_str)
                logger.info("Agent connected!")

                subscription: Subscription = await client.create_subscription(200, agent)
                await subscription.subscribe_data_change(agent.get_observed_properties())

                subscriptions.append(subscription)
                agents.append(agent)

            while True:
                await asyncio.gather(*[task for agent in agents for task in agent.get_tasks()])
                time.sleep(0.1)

    except KeyboardInterrupt:
        for subscription in subscriptions:
            await subscription.delete()
        for agent in agents:
            agent.close()

    except asyncio.exceptions.TimeoutError:
        logger.error("Can't connect to OPC UA server")


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
