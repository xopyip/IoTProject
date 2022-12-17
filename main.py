import asyncio
from device import Factory
from asyncua import Client
from configparser import ConfigParser


def load_config():
    config_object = ConfigParser()
    invalidated = False

    config_object.read("config.ini")

    if not config_object.has_section("FACTORY"):
        config_object.add_section("FACTORY")

    if not config_object.has_option("FACTORY", "url"):
        print("Config file not found")
        url = input("OPC UA server url: ")
        config_object.set("FACTORY", "url", url)
        invalidated = True

    if invalidated:
        with open("config.ini", "w") as f:
            config_object.write(f)

    return config_object


async def main():
    config = load_config()

    async with Client(url=config["FACTORY"]["URL"]) as client:
        factory = await Factory.create(client)
        await factory.list_devices(True)


if __name__ == '__main__':
    asyncio.run(main())
