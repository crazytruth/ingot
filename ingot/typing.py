import ujson as json

from insanic.exceptions import ImproperlyConfigured
from varname import varname

from ingot.choices import SettingsSource
from ingot.fetchers import unevaluated, get_fetchers, IngotFallbackFetcher


class IngotBaseField:
    caster = None

    def __init__(self, default=unevaluated, *, source=SettingsSource.EVS):

        self._varname = varname()
        if not self._varname.isupper():
            raise ImproperlyConfigured(
                f"{self._varname} should be all uppercase."
            )

        self._source = source
        self._fetchers = get_fetchers(source)

        self._values = {
            s: f(self._varname, unevaluated) for s, f in self._fetchers.items()
        }

        if default is not unevaluated:
            self._values.update(
                {
                    SettingsSource.FALLBACK: IngotFallbackFetcher(
                        self._varname, default
                    )
                }
            )

        self.final_value = unevaluated

    @property
    def source(self):
        return self._source

    def __get__(self, instance, owner) -> str:

        if self.final_value is unevaluated:
            for _, f in self._values.items():
                try:
                    self.final_value = self._get_value(f)
                except Exception:
                    pass
                else:
                    # This is here because we WANT to raise
                    # if casting failed
                    if self.caster:
                        self.final_value = self.caster(self.final_value)
                    break
            else:
                raise Exception(f"Cannot resolve {self._varname}.")

        return self.final_value

    def _get_value(self, f):
        return f.value


class IntField(IngotBaseField):
    caster = int


class FloatField(IngotBaseField):
    caster = float


class StringField(IngotBaseField):
    caster = str


class JSONField(IngotBaseField):
    def _get_value(self, f):
        val = super()._get_value(f)
        return json.loads(val)


class DictField(JSONField):
    caster = dict


class ListField(JSONField):
    caster = list


class TupleField(JSONField):
    caster = tuple


class SetField(IngotBaseField):
    caster = set
