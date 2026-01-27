from unicodedata import decomposition
from .typedefs import UnicodeUnit, IPA
from .data import UNI2TIPA, UNI2TIPA_TONE, UNI2TIPA_RTONE, UNI2TIPA_SUPSUB


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
            
            if xords[i] in UNI2TIPA_RTONE:
                base = xords[i]
                i -= 1
                while i >= 0 and xords[i] in UNI2TIPA_RTONE:
                    modifiers.insert(0, xords[i])
                    i -= 1
            elif xords[i] in UNI2TIPA_TONE:
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
            if char.base in UNI2TIPA_RTONE:
                tone = "".join(UNI2TIPA_RTONE.get(m, r"\*" + chr(int(m, 16))) for m in char.modifiers)
                tone += UNI2TIPA_RTONE.get(char.base, r"\*" + chr(int(char.base, 16)))
                result.append(rf"\rtone{{{tone}}}")
                continue

            if char.base in UNI2TIPA_TONE:
                tone = "".join(UNI2TIPA_TONE.get(m, r"\*" + chr(int(m, 16))) for m in char.modifiers)
                tone += UNI2TIPA_TONE.get(char.base, r"\*" + chr(int(char.base, 16)))
                result.append(rf"\tone{{{tone}}}")
                continue
            
            if char.base in UNI2TIPA[0]:
                base = UNI2TIPA[0][char.base]
            elif char.base in UNI2TIPA[2]:
                base = char.base
            else:
                base = r"\*" + chr(int(char.base, 16))

            for modifier in char.modifiers:
                if modifier in UNI2TIPA[1]:
                    base = f"{UNI2TIPA[1][modifier]}{{{base}}}"
                elif modifier in UNI2TIPA_SUPSUB:
                    base = f"{UNI2TIPA_SUPSUB[modifier]}{{{base}}}"
                else:
                    base = rf"\*{chr(int(modifier, 16))}{{{base}}}"
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