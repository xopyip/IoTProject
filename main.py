import asyncio
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
        input("Press any key to shutdown...")
        for agent in agents:
            agent.close()


if __name__ == '__main__':
    asyncio.run(main())
