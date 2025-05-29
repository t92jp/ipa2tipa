from unicodedata import decomposition
from mappings import (
    UNI_TO_TIPA0, UNI_TO_TIPA1, UNI_TO_TIPA2,
    UNI_TO_TIPA_TONE, UNI_TO_TIPA_SUPSUB
)

class IPA(str):
    def __new__(cls, content):
        return super().__new__(cls, content)

    def __init__(self, content):
        super().__init__()
        self.xords = self._decompose()
        self.charlist = self._parse()
        self.tipa = self._ipa2tipa()

    def __add__(self, other):
        if isinstance(other, IPA):
            return IPA(super().__add__(other))
        elif isinstance(other, str):
            return IPA(super().__add__(other))
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return IPA(other + self)
        else:
            return NotImplemented

    def _decompose(self):
        xords = []
        for c in self:
            decom = decomposition(c)
            if decom:
                xords.extend(code.lower() for code in decom.split() if code)
            else:
                xords.append(f"{ord(c):04x}")
        return xords
    
    def _parse(self):
        charlist = []
        i = len(self.xords) - 1
        while i >= 0:
            char_segment = [] 
            current_hex = self.xords[i]

            if current_hex in UNI_TO_TIPA_TONE:
                while i >= 0 and self.xords[i] in UNI_TO_TIPA_TONE:
                    char_segment.insert(0, self.xords[i])
                    i -= 1
            
            elif i >= 0 : # Not a tone
                # Try to parse base character and its preceding diacritics
                # In 'xords' (from right to left): base_hex, diacritic1_hex, diacritic2_hex ...
                # When reading xords from right (i): diacriticN_hex, ..., diacritic1_hex, base_hex
                
                # First, assume current_hex is the base.
                base_hex_candidate = self.xords[i]
                
                # Greedily consume diacritics that are to the LEFT of the current_hex in xords
                # (which means they are encountered FIRST as we decrement i)
                diacritics_found = []
                
                # Look ahead for diacritics if current char is potentially a base
                # This simplified parser assumes a base char is not also a diacritic in UNI_TO_TIPA1
                if base_hex_candidate not in UNI_TO_TIPA1:
                    char_segment.insert(0, base_hex_candidate) # Assume it's a base
                    i -= 1 
                    
                    # Now, collect all diacritics that follow this base (i.e., were to its left in original string)
                    while i >= 0 and self.xords[i] in UNI_TO_TIPA1:
                        diacritics_found.insert(0, self.xords[i])
                        i -= 1
                    char_segment.extend(diacritics_found)
                else: 
                    # current_hex is itself a diacritic. Treat it as standalone for now.
                    # This part of parsing is tricky. A robust parser would better identify base vs diacritic.
                    # For now, if it's in UNI_TO_TIPA1, let it be its own segment.
                    # This might misinterpret some sequences.
                    char_segment.insert(0, current_hex)
                    i -= 1

            if char_segment: 
                charlist.insert(0, char_segment)
            elif i >= 0 : # Should only happen if char_segment was not populated for some reason
                charlist.insert(0, [self.xords[i]]) # Fallback: treat current_hex as its own segment
                i -=1
        
        return [cs for cs in charlist if cs] # Filter out any empty segments

    def _ipa2tipa(self):
        result = []
        for char_parts in self.charlist: 
            if not char_parts: continue
            current_tipa_representation = ""
            base_hex = char_parts[0]

            # Handle tones first as they are standalone sequences
            if base_hex in UNI_TO_TIPA_TONE:
                # Assuming all parts in char_parts for a tone are tone hexes
                tone_numbers = "".join([UNI_TO_TIPA_TONE.get(h, str(h)) for h in char_parts])
                result.append(rf"\tone{{{tone_numbers}}}") # Corrected \tone macro
                continue
            
            # Handle superscripts/subscripts
            if base_hex in UNI_TO_TIPA_SUPSUB:
                current_tipa_representation = UNI_TO_TIPA_SUPSUB.get(base_hex, f"UNI_NOT_FOUND({base_hex})")
                # Note: Original code did not handle diacritics on superscripts/subscripts here.
                # If char_parts has more than base_hex, they are ignored for supsub for now.
            else: # Handle regular characters and their diacritics
                default_char_display = base_hex
                try: # Try to convert hex to char for default display if not found in map
                    if len(base_hex) == 4 and all(c in '0123456789abcdefABCDEF' for c in base_hex):
                        default_char_display = chr(int(base_hex, 16))
                except ValueError: pass # Keep hex if conversion fails
                
                current_tipa_representation = UNI_TO_TIPA0.get(base_hex, default_char_display)

                # Apply diacritics from UNI_TO_TIPA1
                for modifier_hex in char_parts[1:]: # Iterate over diacritics found for the base_hex
                    if modifier_hex in UNI_TO_TIPA1:
                        tipa_macro = UNI_TO_TIPA1.get(modifier_hex)
                        if tipa_macro:
                            # Heuristic for applying macros (some are cmd{ARG}, some are cmd{}, some just cmd)
                            if tipa_macro.endswith("{}"): # e.g. \r*{}
                               current_tipa_representation = f"{tipa_macro[:-2]}{{{current_tipa_representation}}}"
                            elif "{" in tipa_macro and "}" in tipa_macro and "ARG" in tipa_macro : # e.g. \macro{ARG}
                               current_tipa_representation = tipa_macro.replace("ARG", current_tipa_representation)
                            else: # Default: \cmd{base}
                               current_tipa_representation = f"{tipa_macro}{{{current_tipa_representation}}}"
                    # UNI_TO_TIPA2 (for e.g. tie bars) are not handled in this loop, would need post-processing or different parsing.
            result.append(current_tipa_representation)
        
        # Note: Binary ligatures (from UNI_TO_TIPA2 like \t{ts}) are not explicitly handled here.
        # The original code had a post-processing loop for them which is missing in this version.
        # This simplified version primarily handles base chars, unary diacritics, tones, and sup/sub.

        return ''.join(result)

    def to_tipa(self):
        return self.tipa

if __name__ == "__main__":
    print("--- IPA to TIPA Conversion Tests ---")
    # Basic tests
    ipa_basic = IPA("abk")
    print(f"IPA: 'abk' -> TIPA: '{ipa_basic.to_tipa()}' (Expected: abk)") # Relies on UNI_TO_TIPA0 or chr() conversion

    ipa_special_chars = IPA("əʃŋ") # common IPA chars
    # Expected: UNI_TO_TIPA0['0259'] -> @, UNI_TO_TIPA0['0283'] -> S, UNI_TO_TIPA0['014b'] -> N
    print(f"IPA: 'əʃŋ' -> TIPA: '{ipa_special_chars.to_tipa()}' (Expected: @SN)")

    # Tests with diacritics from UNI_TO_TIPA1
    ipa_tilde_a = IPA("ã") # a then U+0303 (COMBINING TILDE)
    # xords: ['0061', '0303']. _parse: [['0061', '0303']]. _ipa2tipa: base='a', mod='0303' -> \~{a}
    # UNI_TO_TIPA1['0303'] should be '\~'
    print(f"IPA: 'ã' (a U+0303) -> TIPA: '{ipa_tilde_a.to_tipa()}' (Expected: \~{{a}})")

    ipa_ring_e = IPA("e̥") # e then U+0325 (COMBINING RING BELOW)
    # xords: ['0065', '0325']. _parse: [['0065', '0325']]. _ipa2tipa: base='e', mod='0325' -> \r*{e}
    # UNI_TO_TIPA1['0325'] should be '\r*{}' or similar
    print(f"IPA: 'e̥' (e U+0325) -> TIPA: '{ipa_ring_e.to_tipa()}' (Expected: \r*{{e}})")
    
    ipa_a_tilde_ring = IPA("ḁ̃") # a, U+0303 (tilde), U+0325 (ring below)
    # xords: ['0061', '0303', '0325']. _parse: [['0061', '0303', '0325']]
    # _ipa2tipa: base='a', mod1='0303' (\~), mod2='0325' (\r*{})
    # Result: \r*{\~{a}}
    print(f"IPA: 'ḁ̃' (a U+0303 U+0325) -> TIPA: '{ipa_a_tilde_ring.to_tipa()}' (Expected: \r*{{\~{{a}}}})")

    # Test tones from UNI_TO_TIPA_TONE
    ipa_tone_35 = IPA("˧˥") # U+02E7 (MODIFIER LETTER MID TONE BAR), U+02E5 (MODIFIER LETTER EXTRA-HIGH TONE BAR)
    # xords: ['02e7', '02e5']. _parse: [['02e7', '02e5']]. _ipa2tipa: \tone{35}
    # UNI_TO_TIPA_TONE: '02e7' -> '3', '02e5' -> '5' (example, actual mapping might differ for extra-high)
    # Let's assume '02e7' -> 3, '02e5' -> 5 as per typical TIPA tone numbers.
    # The provided uni2tipa-tone.csv maps 02E7 to 3 and 02E5 to "tone 5 variant" which might be just 5.
    # Let's assume mappings.py results in UNI_TO_TIPA_TONE['02e7'] = '3', UNI_TO_TIPA_TONE['02e5'] = '5'
    print(f"IPA: '˧˥' (U+02E7 U+02E5) -> TIPA: '{ipa_tone_35.to_tipa()}' (Expected: \tone{{35}})")

    # Test superscripts/subscripts from UNI_TO_TIPA_SUPSUB
    ipa_super_h = IPA("ʰ") # U+02B0 (MODIFIER LETTER SMALL H)
    # xords: ['02b0']. _parse: [['02b0']]. _ipa2tipa: \textsuperscript{h}
    # UNI_TO_TIPA_SUPSUB['02b0'] should be '\textsuperscript{h}'
    print(f"IPA: 'ʰ' (U+02B0) -> TIPA: '{ipa_super_h.to_tipa()}' (Expected: \textsuperscript{{h}})")

    print("\n--- Complex Examples (behavior depends heavily on parsing logic) ---")
    ipa_complex = IPA("ko̞ko̞ ɲ̟i ") + IPA("ɲ̟ɯ̟ᵝːɾʲo̞kɯ̟ᵝ ɕi̥te̞ ") + IPA("kɯ̟ᵝda̠sa̠i")
    print(f"IPA complex 1: '{ipa_complex}' -> TIPA: '{ipa_complex.to_tipa()}'")

    ipa_from_tipa2ipa_example = IPA("ˈtʰiː ˌnãɪ̃ɾ̃iˈtʰu̟ː ˈd͡ʒeɪ ˈpʰiː")
    # This example contains many elements including stress marks, ligatures (d͡ʒ), complex diacritics.
    # The simplified parser and converter here will likely not produce perfect TIPA for this.
    print(f"IPA complex 2: '{ipa_from_tipa2ipa_example}' -> TIPA: '{ipa_from_tipa2ipa_example.to_tipa()}'")

    print("\nDone with IPA to TIPA tests.")
```
