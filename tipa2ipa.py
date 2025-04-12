import re
import csv
from pathlib import Path

class TIPA(str):
    # inverse mapping dictionaries
    TIPA2UNI: list[dict[str, str]] = [{}, {}, {}]
    TIPA2UNI_TONE: dict[str, str] = {}
    TIPA2UNI_SUPSUB: dict[str, str] = {}
    
    # superscript mapping
    SUPERSCRIPT_MAP = {
        'h': '02b0',  # ʰ
        'H': '02b1',  # ʱ
        'j': '02b2',  # ʲ
        'w': '02b7',  # ʷ
        'G': '02e0',  # ˠ
        'P': '02c0',  # ˀ
        'Q': '02e4',  # ˤ
    }
    
    script_dir = Path(__file__).parent
    
    # load dictionaries
    for i in range(3):
        with open(script_dir / f"uni2tipa/uni2tipa{i}.csv", 'r', encoding="utf-8") as f:
            for row in csv.reader(f, quoting=csv.QUOTE_NONE):
                if len(row) == 2 and row[1]:  # 空でない値のみ逆マッピング
                    # 値からスペースとカンマを除去して保存
                    TIPA2UNI[i][row[1].strip()] = row[0]
    
    with open(script_dir / "uni2tipa/uni2tipa-tone.csv", 'r', encoding="utf-8") as f:
        for row in csv.reader(f, quoting=csv.QUOTE_NONE):
            if len(row) == 2 and row[1]:
                # 値からスペースとカンマを除去
                TIPA2UNI_TONE[row[1].strip()] = row[0]
    
    with open(script_dir / "uni2tipa/uni2tipa-supsub.csv", 'r', encoding="utf-8") as f:
        for row in csv.reader(f, quoting=csv.QUOTE_NONE):
            if len(row) == 2 and row[1]:
                TIPA2UNI_SUPSUB[row[1].strip()] = row[0]
    
    def __new__(cls, content):
        return super().__new__(cls, content)
    
    def __init__(self, content):
        super().__init__()
        self.ipa = self._tipa2ipa()
    
    def _tipa2ipa(self):
        text = self
        
        # process tone markers
        tone_pattern = r'\\tone\{([1-5]+)\}'
        text = self._process_tone(text, tone_pattern)
        
        # process 2-ary modifiers
        for macro, unicode_hex in self.TIPA2UNI[2].items():
            pattern = fr'{re.escape(macro)}\{{([^}}]+)\}}' 
            text = self._process_binary_macros(text, pattern, unicode_hex)
        
        # process 1-ary modifiers
        pattern = r'\\([^{}\s]+)\{([^{}]+)\}'
        text = self._process_unary_macros(text, pattern)
        
        for tipa, unicode_hex in self.TIPA2UNI[0].items():
            if tipa and len(tipa) > 0:
                text = text.replace(tipa, chr(int(unicode_hex, 16)))
        
        return text
    
    def _process_tone(self, text, pattern):
        """process tone markers"""
        def replace_tone(match):
            tone_digits = match.group(1)
            result = ''
            for digit in tone_digits:
                hex_code = self.TIPA2UNI_TONE.get(digit)
                if hex_code:
                    result += chr(int(hex_code, 16))
            return result
        
        return re.sub(pattern, replace_tone, text)
    
    def _process_binary_macros(self, text, pattern, unicode_hex):
        """process binary macros"""
        def replace_binary(match):
            content = match.group(1)
            return content
        
        return re.sub(pattern, replace_binary, text)
    
    def _process_unary_macros(self, text, pattern):
        """process unary macros"""
        def replace_unary(match):
            macro = '\\' + match.group(1)
            content = match.group(2)
            
            if macro == '\\textsuperscript' or macro == '\\super':
                hex_code = self.SUPERSCRIPT_MAP.get(content)
                if hex_code:
                    return chr(int(hex_code, 16))
                return content
            
            # super/subscripts
            for supsub, code in self.TIPA2UNI_SUPSUB.items():
                if macro == supsub:
                    # return as-is
                    return content
            
            # 1-ary modifiers
            for tipa, hex_code in self.TIPA2UNI[1].items():
                if macro == tipa:
                    # 修飾子を適用
                    char = chr(int(hex_code, 16))
                    return char + content
            
            # no match, return as-is
            return content
        
        # process 1-ary modifiers
        text = re.sub(pattern, replace_unary, text)
        
        # process superscripts
        superscript_pattern = r'\\(?:textsuperscript|super)\{([^{}]+)\}'
        text = re.sub(superscript_pattern, lambda m: replace_unary(re.match(r'\\((?:textsuperscript|super))\{([^{}]+)\}', '\\' + m.group(0))), text)
        
        return text
    
    def to_ipa(self):
        return self.ipa

def tipa2ipa(tipa_text):
    return TIPA(tipa_text).to_ipa()

if __name__ == "__main__":
    tipa_example = r""""t\super{h}i: ""n\~{a}\~{I}\~{R}i"t\super{h}\|+{u}: "\t{dZ}eI "p\super{h}i:"""
    ipa_result = tipa2ipa(tipa_example)
    print(f"TIPA: {tipa_example}")
    print(f"-> IPA: {ipa_result}")
    
    tipa_tone = r"""t\super{h}jEn\tone{35} \:t{}\:s{}UN\tone{5} pAN\tone{5} p\super{h}7N\tone{35}"""
    ipa_tone = tipa2ipa(tipa_tone)
    print(f"TIPA with tones: {tipa_tone}")
    print(f"-> IPA with tones: {ipa_tone}")
