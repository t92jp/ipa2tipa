from dataclasses import dataclass, field


@dataclass
class UnicodeUnit:
    base: str
    modifiers: list[str] = field(default_factory=list)


class IPA(str):
    def to_tipa(self) -> 'TIPA':
        from .ipa2tipa import _IPAToTIPAConverter
        return TIPA(_IPAToTIPAConverter().convert(self))


class TIPA(str):
    def to_ipa(self) -> 'IPA':
        from .tipa2ipa import _TIPAToIPAConverter
        return IPA(_TIPAToIPAConverter().convert(self))
