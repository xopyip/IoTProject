from configparser import ConfigParser


def load():
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


class Config:
    def __init__(self):
        config = load()
        self.factory_url = config["FACTORY"]["url"]
