import asyncio
from device import Factory
from asyncua import Client
from config import Config


async def main():
    config = Config()

    async with Client(url=config.factory_url) as client:
        factory = await Factory.create(client)
        await factory.list_devices(True)


if __name__ == '__main__':
    asyncio.run(main())
