from configparser import ConfigParser


class Config:
    def __init__(self):
        self.config = ConfigParser()
        self.load()

    def get_factory_url(self):
        return self.config["FACTORY"]["url"]

    def has_agent_connection_str(self, name):
        return name in self.config["AGENT"].keys()

    def get_agent_connection_str(self, name):
        return self.config["AGENT"].get(name, None)

    def load(self):
        invalidated = False

        self.config.read("config.ini")

        if not self.config.has_section("FACTORY"):
            self.config.add_section("FACTORY")

        if not self.config.has_section("AGENT"):
            self.config.add_section("AGENT")

        if not self.config.has_option("FACTORY", "url"):
            print("Config file not found")
            url = input("OPC UA server url: ")
            self.config.set("FACTORY", "url", url)
            invalidated = True

        if invalidated:
            self.save()

    def set_agent_connection_str(self, name, value):
        self.config.set("AGENT", name, value)
        self.save()

    def save(self):
        with open("config.ini", "w") as f:
            self.config.write(f)
