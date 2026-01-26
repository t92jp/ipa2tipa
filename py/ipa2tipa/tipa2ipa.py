import re
from .typedefs import IPA, TIPA
from .data import UNI2TIPA, UNI2TIPA_TONE

TIPA2UNI = [{v: k for k, v in d.items() if v} for d in UNI2TIPA]
TIPA2UNI_TONE = {v: k for k, v in UNI2TIPA_TONE.items() if v}


class _TIPAToIPAConverter:
    def convert(self, tipa_string: str) -> str:
        """TIPA文字列をIPA文字列に変換（簡易実装）"""
        result = tipa_string
        
        superscript_map = {
            'h': '\u02b0', 'ɦ': '\u02b1', 'j': '\u02b2', 'r': '\u02b3',
            'ɹ': '\u02b4', 'ʁ': '\u02b6', 'w': '\u02b7', 'y': '\u02b8',
            'ʕ': '\u02c1', 'l': '\u02e1', 's': '\u02e2', 'x': '\u02e3',
            'ɣ': '\u02e0', 'n': '\u207f', 'ŋ': '\u1d45',
        }
        for base, superscript in superscript_map.items():
            result = result.replace(rf'\super{{{base}}}', superscript)
        
        # accents
        result = result.replace('""', 'ˌ')  # secondary stress
        result = result.replace('"', 'ˈ')  # primary stress
        
        # tonals
        tone_pattern = r'\\tone\{([0-9]+)\}'
        def replace_tone(match):
            digits = match.group(1)
            return ''.join(chr(int(TIPA2UNI_TONE[d], 16)) for d in digits if d in TIPA2UNI_TONE)
        result = re.sub(tone_pattern, replace_tone, result)
        
        # 2-aries
        for tipa_cmd, uni in sorted(TIPA2UNI[2].items(), key=lambda x: -len(x[0])):
            pattern = re.escape(tipa_cmd) + r'\{(.+?)\}'
            replacement = chr(int(uni, 16)) + r'\1'
            result = re.sub(pattern, replacement, result)
        
        # 1-aries
        for tipa_cmd, uni in sorted(TIPA2UNI[1].items(), key=lambda x: -len(x[0])):
            pattern = re.escape(tipa_cmd) + r'\{(.+?)\}'
            replacement = r'\1' + chr(int(uni, 16))
            result = re.sub(pattern, replacement, result)
        
        # 0-aries
        for tipa_cmd, uni in sorted(TIPA2UNI[0].items(), key=lambda x: -len(x[0])):
            result = result.replace(tipa_cmd, chr(int(uni, 16)))
        
        return result


if __name__ == "__main__":
    print("TIPA -> IPA")
    tipa = TIPA(r'"t\super{h}i:')
    ipa = tipa.to_ipa()
    print(f"TIPA: {tipa}")
    print(f"IPA: {ipa}")
    print(f"TIPA is str: {isinstance(tipa, str)}")
    print(f"IPA is str: {isinstance(ipa, str)}")
    print()

    print("IPA -> TIPA -> IPA")
    original_ipa = IPA("ˈtʰiː")
    tipa = original_ipa.to_tipa()
    back_to_ipa = tipa.to_ipa()
    print(f"Original IPA: {original_ipa}")
    print(f"TIPA: {tipa}")
    print(f"Back to IPA: {back_to_ipa}")
    print(f"Match: {original_ipa == back_to_ipa}")

