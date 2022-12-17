import asyncio
from device import Factory
from asyncua import Client

FACTORY_URL = 'opc.tcp://192.168.100.21:4840/'


async def main():
    async with Client(url=FACTORY_URL) as client:
        factory = await Factory.create(client)
        await factory.list_devices(True)


if __name__ == '__main__':
    asyncio.run(main())
