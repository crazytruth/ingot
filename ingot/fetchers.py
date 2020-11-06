import os
from collections import OrderedDict

from ingot.choices import SettingsSource
from ingot.registry import settings_registry

unevaluated = object()

source_fetcher_mapping = {}


def get_fetchers(source):

    binary = source.binary()

    fetchers = []

    for i in range(len(binary)):

        flag = source & pow(2, i)
        if flag:
            fetchers.append((flag, source_fetcher_mapping[flag]))

    return OrderedDict(reversed(fetchers))


class IngotFetcherType(type):
    def __new__(mcs, name, bases, attr, *args, **kwargs):
        new_type = super().__new__(mcs, name, bases, attr)

        source = attr.get("source", 0)

        for base in bases:
            if issubclass(base, IngotFetcherBase) and hasattr(base, "source"):
                source |= base.source

        if source > 0:
            source_fetcher_mapping.update({source: new_type})

        return new_type


class IngotFetcherBase(metaclass=IngotFetcherType):
    source = 0

    def __new__(cls, varname, value=unevaluated):

        if cls.source:
            fetcher = settings_registry.retrieve(cls.source, varname)
            if fetcher:
                return fetcher

        new = super().__new__(cls)

        if cls.source:
            settings_registry.register(cls.source, varname, new)

        return new

    def __init__(self, varname, value=unevaluated):
        self._varname = varname
        self._value = value

    def fetch(self):
        self._value = self.__fetch__()

    @property
    def value(self):
        if self._value is unevaluated:
            self.fetch()
        return self._value

    def __fetch__(self):
        raise NotImplementedError("Implement this.")


class IngotFallbackFetcher(IngotFetcherBase):
    def __fetch__(self):
        return self._value


class IngotEnvironmentFetcher(IngotFetcherBase):
    source = SettingsSource.E

    def __fetch__(self):
        return os.environ[self._varname]


class IngotServiceFetcher(IngotFetcherBase):
    source = SettingsSource.S


class IngotVaultFetcher(IngotFetcherBase):
    source = SettingsSource.V
