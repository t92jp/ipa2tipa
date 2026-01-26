from unicodedata import decomposition
import csv
from typedefs import UnicodeUnit, IPA

UNI2TIPA: list[dict[str, str]] = []
for i in range(3):
    with open(f"uni2tipa/uni2tipa{i}.tsv", encoding="utf-8") as f:
        UNI2TIPA.append({row[0]: row[1] for row in csv.reader(f, quoting=csv.QUOTE_NONE, delimiter="\t")})

with open("uni2tipa/uni2tipa-tone.tsv", encoding="utf-8") as f:
    UNI2TIPA_TONE = {row[0]: row[1] for row in csv.reader(f, quoting=csv.QUOTE_NONE, delimiter="\t")}

with open("uni2tipa/uni2tipa-supsub.tsv", encoding="utf-8") as f:
    UNI2TIPA_SUPSUB = {row[0]: row[1] for row in csv.reader(f, quoting=csv.QUOTE_NONE, delimiter="\t")}


class _IPAToTIPAConverter:
    def convert(self, ipa_string: str) -> str:
        xords = self._decompose(ipa_string)
        chars = self._group_characters(xords)
        return self._to_tipa(chars)

    @staticmethod
    def _decompose(text: str) -> list[str]:
        xords = []
        for c in text:
            decom = decomposition(c)
            xords.extend(code.lower() for code in decom.split()) if decom else xords.append(f"{ord(c):04x}")
        return xords
    
    def _group_characters(self, xords: list[str]) -> list[UnicodeUnit]:
        chars = []
        i = len(xords) - 1
        
        while i >= 0:
            modifiers = []
            base = None
            
            if xords[i] in UNI2TIPA_TONE:
                base = xords[i]
                i -= 1
                while i >= 0 and xords[i] in UNI2TIPA_TONE:
                    modifiers.insert(0, xords[i])
                    i -= 1
            else:
                while i >= 0 and xords[i] in UNI2TIPA[1]:
                    modifiers.insert(0, xords[i])
                    i -= 1
                if i >= 0: 
                    base = xords[i]
                    i -= 1
                if i >= 0 and xords[i] in UNI2TIPA_SUPSUB:
                    modifiers.append(xords[i])
                    i -= 1

            if base is not None:
                chars.insert(0, UnicodeUnit(base, modifiers) if modifiers else UnicodeUnit(base))
        
        return chars
    
    def _to_tipa(self, chars: list[UnicodeUnit]) -> str:
        result = []
        
        for char in chars:
            if char.base in UNI2TIPA_TONE:
                tone = "".join(UNI2TIPA_TONE.get(m, m) for m in char.modifiers)
                tone += UNI2TIPA_TONE.get(char.base, char.base)
                result.append(rf"\tone{{{tone}}}")
                continue
            
            base = UNI2TIPA[0].get(char.base, char.base)
            for modifier in char.modifiers:
                if modifier in UNI2TIPA[1]:
                    base = f"{UNI2TIPA[1][modifier]}{{{base}}}"
                if modifier in UNI2TIPA_SUPSUB:
                    base = f"{UNI2TIPA_SUPSUB[modifier]}{{{base}}}"
            result.append(base)

        i = 0
        while i < len(result) - 1:
            if result[i] in UNI2TIPA[2]:
                result[i-1] = f"{UNI2TIPA[2][result[i]]}{{{result[i-1]}{result[i+1]}}}"
                result = result[:i] + result[i+2:]
            else:
                i += 1

        return ''.join(result)


if __name__ == "__main__":
    print("# IPA sequence")
    ipa = IPA("ˈtʰiː ˌnãɪ̃ɾ̃iˈtʰu̟ː ˈd͡ʒeɪ ˈpʰiː")
    tipa = ipa.to_tipa()
    print(f"IPA: {ipa}")
    print(f"TIPA: {tipa}")
    converter = _IPAToTIPAConverter()
    print(converter._group_characters(converter._decompose("tʰiː")))
    print()
    
    print("# tonal")
    ipa2 = IPA("tʰjɛn˧˥ ʈʂʊŋ˥ pɑŋ˥ pʰɤŋ˧˥")
    print(f"IPA: {ipa2}")
    print(f"TIPA: {ipa2.to_tipa()}")
    print()
    
    print("# string manipulation")
    ipa3 = IPA("ko̞ko̞")
    print(f"Length: {len(ipa3)}")
    print(f"Upper: {ipa3.upper()}")
    print(f"Concatenation: {ipa3 + ' test'}")
    print(f"Upper: {ipa3.upper()}")
    print(f"Concatenation: {ipa3 + ' test'}")