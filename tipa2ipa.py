import re
# Remove csv and Path imports, as loading is now handled by mappings.py
from mappings import TIPA_TO_UNI0, TIPA_TO_UNI1, TIPA_TO_UNI2, TIPA_TO_UNI_TONE, TIPA_TO_UNI_SUPSUB

class TIPA(str):
    # Remove direct loading of TIPA2UNI, TIPA2UNI_TONE, TIPA2UNI_SUPSUB, and SUPERSCRIPT_MAP
    # These will be imported from mappings.py

    def __new__(cls, content):
        return super().__new__(cls, content)

    def __init__(self, content):
        super().__init__()
        self.ipa = self._tipa2ipa()

    def _tipa2ipa(self):
        text = str(self) # Work on a string copy

        # Process tone markers first
        # Example: \tone{35}
        tone_pattern = r'\\tone\{([1-5]+)\}' # Assuming tones are 1-5
        text = self._process_tone(text, tone_pattern)

        # Process superscript and subscript macros using TIPA_TO_UNI_SUPSUB
        # This map contains entries like: '\\super{h}': '02b0', '\\textsuperscript{n}': '207f'
        # We iterate through the map and replace occurrences in the text.
        # Sorting by length of key (desc) can help avoid partial replacements if keys overlap,
        # but since keys are full commands, direct replacement should be mostly fine.
        # For safety, one could sort: sorted_supsub = sorted(TIPA_TO_UNI_SUPSUB.items(), key=lambda item: len(item[0]), reverse=True)
        for tipa_cmd, unicode_hex in TIPA_TO_UNI_SUPSUB.items():
            if tipa_cmd in text:
                try:
                    char_val = chr(int(unicode_hex, 16))
                    text = text.replace(tipa_cmd, char_val)
                except ValueError:
                    print(f"Warning: Invalid Unicode hex '{unicode_hex}' for TIPA command '{tipa_cmd}' in supersub processing.")
        
        # Process 2-ary ligature macros (e.g., \t{dZ} for d͡ʒ)
        # TIPA_TO_UNI2 maps the TIPA macro command (e.g., "\t") to the Unicode hex of the combining character (e.g., "0361" for COMBINING DOUBLE INVERTED BREVE).
        # Example: \t{dN} should become d + chr(0x0361) + N.
        for tipa_macro, unicode_hex_combiner in TIPA_TO_UNI2.items():
            # Regex to find the pattern: \macro{char1char2} or \macro{char}
            # The pattern needs to be specific to the macro.
            # Example for \t{..}: r'\\t\{([^{}]+)\}'
            pattern = fr'{re.escape(tipa_macro)}\{{([^}}]+)\}}'
            
            def replace_binary_ligature(match):
                content = match.group(1) # Content inside braces e.g. "dZ"
                if len(content) == 2:
                    char1 = content[0]
                    char2 = content[1]
                    try:
                        combining_char = chr(int(unicode_hex_combiner, 16))
                        return char1 + combining_char + char2
                    except ValueError:
                        return match.group(0) # Return original on error
                elif len(content) == 1: # e.g. \t{S} for t͡S
                    # This implies the combining mark applies over the single character.
                    # Or it's part of a sequence like \tS to mean tS ligature.
                    # This case is ambiguous without more specific rules per macro.
                    # For now, let's assume it means content + combiner if one char.
                    try:
                        combining_char = chr(int(unicode_hex_combiner, 16))
                        return content + combining_char 
                    except ValueError:
                        return match.group(0)
                return match.group(0) # Return original if content not 1 or 2 chars

            text = re.sub(pattern, replace_binary_ligature, text)

        # Process 1-ary diacritic macros (e.g., \~{a})
        # TIPA_TO_UNI1 maps the TIPA diacritic command (e.g., "\~") to the Unicode hex of the combining diacritic mark (e.g., "0303" for COMBINING TILDE).
        # Example: \~{a} should become a + chr(0x0303).
        for tipa_diacritic_cmd, unicode_hex_diacritic in TIPA_TO_UNI1.items():
            # Regex to find the pattern: \diacritic_cmd{char}
            pattern = fr'{re.escape(tipa_diacritic_cmd)}\{{([^}}]+)\}}'

            def replace_unary_diacritic(match):
                base_char_text = match.group(1) # Content inside braces e.g. "a"
                # Assuming the base_char_text is a single character for simplicity here.
                # If base_char_text can be complex, further processing might be needed.
                if len(base_char_text) == 1: # Or check if it's a single IPA char already
                    try:
                        diacritic_char = chr(int(unicode_hex_diacritic, 16))
                        # IPA convention: base character followed by combining diacritic mark.
                        return base_char_text + diacritic_char
                    except ValueError:
                        return match.group(0) # Return original on error
                return match.group(0) # Return original if base_char_text is not simple

            text = re.sub(pattern, replace_unary_diacritic, text)
            
        # Process remaining simple TIPA commands (direct symbol replacements from TIPA_TO_UNI0)
        # This includes single symbols (e.g., "H" -> "ɦ") and some macros not caught above.
        # Sort by length to replace longer sequences first (e.g. "\textturnh" before "\h" if that was a thing)
        sorted_tipa0_items = sorted(TIPA_TO_UNI0.items(), key=lambda item: len(item[0]), reverse=True)
        for tipa_cmd, unicode_hex in sorted_tipa0_items:
            if tipa_cmd in text:
                try:
                    char_val = chr(int(unicode_hex, 16))
                    text = text.replace(tipa_cmd, char_val)
                except ValueError:
                    print(f"Warning: Invalid Unicode hex '{unicode_hex}' for TIPA command '{tipa_cmd}' in TIPA_TO_UNI0.")
        
        return text

    def _process_tone(self, text, pattern):
        """Process tone markers using TIPA_TO_UNI_TONE."""
        def replace_tone(match):
            tone_digits = match.group(1)  # e.g., "35"
            result = ''
            for digit in tone_digits:  # e.g., "3", then "5"
                hex_code = TIPA_TO_UNI_TONE.get(digit)
                if hex_code:
                    try:
                        result += chr(int(hex_code, 16))
                    except ValueError:
                        print(f"Warning: Invalid Unicode hex '{hex_code}' for tone digit '{digit}'.")
                else:
                    # If digit itself is a key (e.g. for custom tone mappings if any)
                    # This case should ideally not happen if TIPA_TO_UNI_TONE is TIPA number -> IPA hex
                    print(f"Warning: No IPA mapping for tone digit '{digit}'.")
            return result
        
        return re.sub(pattern, replace_tone, text)

    # _process_binary_macros and _process_unary_macros are being refactored and integrated into _tipa2ipa above.
    # Keeping the definitions here commented out or removed if fully integrated.
    # def _process_binary_macros(self, text, pattern, unicode_hex): ...
    # def _process_unary_macros(self, text, pattern): ...

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
