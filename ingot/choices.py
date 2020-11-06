from enum import IntFlag


class SettingsSource(IntFlag):

    FALLBACK = 0
    SERVICE = 1
    VAULT = 2
    ENVIRONMENT = 4

    # Shortcuts
    S = SERVICE  # 001
    V = VAULT  # 010
    E = ENVIRONMENT  # 100

    VS = VAULT | SERVICE
    ES = ENVIRONMENT | SERVICE
    EV = ENVIRONMENT | VAULT

    EVS = ENVIRONMENT | VAULT | SERVICE

    def binary(self) -> str:
        places = self.max_bits()
        return "{0:b}".format(self).zfill(places)

    @classmethod
    def max_bits(cls):
        return 3
