import asyncio
import time

from asyncua import Client
from device import Factory
from config import Config
from agent import Agent


async def main():
    config = Config()

    async with Client(url=config.get_factory_url()) as client:
        factory = await Factory.create(client)
        agents = []
        for device in factory.devices:
            if not config.has_agent_connection_str(device.name):
                config.set_agent_connection_str(device.name, input(f"Connection string for {device.name}:"))
            connection_str = config.get_agent_connection_str(device.name)
            agents.append(Agent(device, connection_str))
        try:
            while True:
                tasks = [asyncio.create_task(agent.telemetry()) for agent in agents]
                await asyncio.gather(*tasks)
                time.sleep(1)
        except:
            for agent in agents:
                agent.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
