import asyncio
import time

from asyncua import Client
from asyncua.common.subscription import Subscription
from device import Factory
from config import Config
from agent import Agent


async def main():
    config = Config()

    async with Client(url=config.get_factory_url()) as client:
        factory = await Factory.create(client)
        agents = []
        subscriptions = []
        for device in factory.devices:
            if not config.has_agent_connection_str(device.name):
                config.set_agent_connection_str(device.name, input(f"Connection string for {device.name}:"))
            connection_str = config.get_agent_connection_str(device.name)
            agent = Agent(device, connection_str)

            subscription: Subscription = await client.create_subscription(200, agent)
            await subscription.subscribe_data_change([device.get_node(type) for type in agent.get_observed_properties()])

            subscriptions.append(subscription)
            agents.append(agent)
        try:
            while True:
                tasks = []
                for agent in agents:
                    agent_tasks = agent.get_tasks()
                    for task in agent_tasks:
                        tasks.append(task)
                await asyncio.gather(*tasks)
                time.sleep(1)
        except Exception as e:
            print(e)
            for subscription in subscriptions:
                await subscription.delete()
            for agent in agents:
                agent.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
