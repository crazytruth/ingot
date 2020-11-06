from ingot.choices import SettingsSource
from collections import UserDict


class SettingsRegistry(UserDict):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for i in range(SettingsSource.max_bits()):
            flag = pow(2, i) | SettingsSource.FALLBACK
            self.update({flag: {}})

    def register(self, source, varname, value):
        self[source][varname] = value

    def retrieve(self, source, varname):
        return self.get(source, {}).get(varname, None)


settings_registry = SettingsRegistry()
