import csv
import os

# --- Predefined Mappings ---
SUPERSCRIPT_MAP = {
    'h': '02b0', 'H': '02b1', 'j': '02b2', 'l': '02e1', 'n': '207f', 's': '02e2',
    'S': '02e2', 'x': '02e3', 'X': '02e3', 'Z': '02e0', 'w': '02b7', 'W': '02b8',
    'P': '0360', 't': '0361', 'K': '1d4f', 'N': '1d3a', 'L': '1d38', 'G': '1d33',
    'J': '02b2', 'v': '1d5b', 'V': '1d5b', 'f': '1da0', 'F': '1da0',
    'T': '03b8',  # Greek theta symbol
    '(': '207d', ')': '207e', '+': '207a', '-': '207b', '=': '207c',
    '0': '2070', '1': '00b9', '2': '00b2', '3': '00b3', '4': '2074',
    '5': '2075', '6': '2076', '7': '2077', '8': '2078', '9': '2079',
    'a': '1d43', 'A': '1d2c', 'b': '1d47', 'B': '1d2e', 'd': '1d48', 'D': '1d30',
    'e': '1d49', 'E': '1d31', 'g': '1d4d', 'i': '2071', 'I': '1d35', 'k': '1d4f',
    'm': '1d50', 'M': '1d39', 'o': '1d52', 'O': '1d3c', 'p': '1d56', 'r': '02b3',
    'R': '1d3f', 'u': '1d58', 'U': '1d41', 'y': '02b8'
}

SUBSCRIPT_MAP = { # As TIPA doesn't have a generic \sub command, we map IPA subscript hex to TIPA char
    '0': '2080', '1': '2081', '2': '2082', '3': '2083', '4': '2084',
    '5': '2085', '6': '2086', '7': '2087', '8': '2088', '9': '2089',
    '+': '208a', '-': '208b', '=': '208c', '(': '208d', ')': '208e',
    'a': '2090', 'e': '2091', 'h': '2095', 'i': '1d62', 'j': '2c7c', 'k': '2096',
    'l': '2097', 'm': '2098', 'n': '2099', 'o': '2092', 'p': '209a', 'r': '1d63',
    's': '209b', 't': '209c', 'u': '1d64', 'v': '1d65', 'x': '2093', 'S': '209b'
    # No direct TIPA commands for these, typically just the Unicode subscript character is used if available
    # or specific workarounds are needed in LaTeX.
}


# --- Helper Functions ---
def _load_csv_map(filepath, key_col_idx, val_col_idx, directory="uni2tipa/"):
    """
    Loads a CSV file into a dictionary, mapping values from key_col_idx to val_col_idx.
    Skips empty lines or improperly formatted rows.
    Values are read as-is, without stripping.
    """
    mapping = {}
    full_path = os.path.join(directory, filepath)
    if not os.path.exists(full_path):
        print(f"Warning: CSV file not found: {full_path}")
        return mapping
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if not row:  # Skip empty lines
                    # print(f"Skipping empty row {i+1} in {filepath}")
                    continue
                if len(row) > max(key_col_idx, val_col_idx):
                    key = row[key_col_idx]
                    val = row[val_col_idx]
                    if key and val: # Ensure key and value are not empty
                        mapping[key] = val
                    # else:
                        # print(f"Skipping row {i+1} in {filepath} due to empty key/value: {row}")
                # else:
                    # print(f"Skipping improperly formatted row {i+1} in {filepath}: {row}")
    except Exception as e:
        print(f"Error loading CSV file {full_path}: {e}")
    return mapping

def _invert_map(original_map):
    """Inverts a dictionary. If multiple keys map to the same value, one will be chosen arbitrarily."""
    inverted = {}
    for key, value in original_map.items():
        if value not in inverted: # To avoid overwriting if multiple keys map to the same value (e.g. \textturnh vs \textreversedh)
            inverted[value] = key
        # else:
            # print(f"Warning: Duplicate value '{value}' encountered while inverting map. Key '{key}' will not overwrite existing key '{inverted[value]}'.")
    return inverted

# --- Load Unicode to TIPA Mappings ---
UNI_TO_TIPA0 = _load_csv_map('uni2tipa0.csv', 0, 1)          # Unicode hex -> TIPA string
UNI_TO_TIPA1 = _load_csv_map('uni2tipa1.csv', 0, 1)          # Unicode hex -> TIPA macro (1-ary diacritics)
UNI_TO_TIPA2 = _load_csv_map('uni2tipa2.csv', 0, 1)          # Unicode hex -> TIPA macro (2-ary combining marks)
UNI_TO_TIPA_TONE = _load_csv_map('uni2tipa-tone.csv', 0, 1)    # Unicode hex -> TIPA tone numbers
UNI_TO_TIPA_SUPSUB = _load_csv_map('uni2tipa-supsub.csv', 0, 1) # Unicode hex -> TIPA super/subscript macros

# --- Create TIPA to Unicode Mappings (Inverse Mappings) ---
TIPA_TO_UNI0 = _invert_map(UNI_TO_TIPA0)
TIPA_TO_UNI1 = _invert_map(UNI_TO_TIPA1)
TIPA_TO_UNI2 = _invert_map(UNI_TO_TIPA2)
TIPA_TO_UNI_TONE = _invert_map(UNI_TO_TIPA_TONE)
TIPA_TO_UNI_SUPSUB = _invert_map(UNI_TO_TIPA_SUPSUB)


# --- Integrate SUPERSCRIPT_MAP and SUBSCRIPT_MAP ---

# UNI_TO_TIPA_SUPSUB: IPA hex -> TIPA command (e.g. '02b0': '\textsuperscript{h}')
# We need to add entries from SUPERSCRIPT_MAP (TIPA char -> IPA hex)
# and SUBSCRIPT_MAP (TIPA char -> IPA hex) into UNI_TO_TIPA_SUPSUB.
# The CSV uni2tipa-supsub.csv already maps IPA hex to TIPA commands like \textsuperscript{ARG} or \textsubscript{ARG}
# We should ensure SUPERSCRIPT_MAP and SUBSCRIPT_MAP align with this.

# For SUPERSCRIPT_MAP: TIPA char -> IPA hex
# Example: 'h': '02b0'
# We want UNI_TO_TIPA_SUPSUB['02b0'] = '\textsuperscript{h}' (or similar)
# The CSV uni2tipa-supsub.csv should ideally already provide this.
# If not, we might need to generate the TIPA command.
# Let's assume uni2tipa-supsub.csv is comprehensive for IPA hex to TIPA command.

# For TIPA_TO_UNI_SUPSUB: TIPA command -> IPA hex
# Example: '\textsuperscript{h}': '02b0'
# We need to add entries based on SUPERSCRIPT_MAP.
# TIPA commands can be \super{X} or \textsuperscript{X}. We'll prioritize \textsuperscript{X}.

for char, uni_hex in SUPERSCRIPT_MAP.items():
    tipa_command_super = f"\\super{{{char}}}"
    tipa_command_textsuperscript = f"\\textsuperscript{{{char}}}"

    # Add to TIPA_TO_UNI_SUPSUB
    if tipa_command_textsuperscript not in TIPA_TO_UNI_SUPSUB:
        TIPA_TO_UNI_SUPSUB[tipa_command_textsuperscript] = uni_hex
    # Also add \super{} form if it's not already there (could conflict if \super and \textsuperscript map differently)
    if tipa_command_super not in TIPA_TO_UNI_SUPSUB:
         TIPA_TO_UNI_SUPSUB[tipa_command_super] = uni_hex

    # Add to UNI_TO_TIPA_SUPSUB (inverse mapping)
    # Only add if the uni_hex is not already mapped, or if the existing mapping is generic
    # and we can provide a more specific one (e.g. from \textsuperscript{h} vs a generic one from the CSV)
    # The CSV uni2tipa-supsub.csv is expected to have forms like \textsuperscript{ARG}
    # We prefer the specific mapping from SUPERSCRIPT_MAP if the CSV provides a generic placeholder.
    if uni_hex not in UNI_TO_TIPA_SUPSUB or "ARG" in UNI_TO_TIPA_SUPSUB.get(uni_hex, ""):
        UNI_TO_TIPA_SUPSUB[uni_hex] = tipa_command_textsuperscript


for char, uni_hex in SUBSCRIPT_MAP.items():
    tipa_command_sub = f"\\sub{{{char}}}" # TIPA doesn't have a standard \sub command like this
    tipa_command_textsubscript = f"\\textsubscript{{{char}}}"

    # Add to TIPA_TO_UNI_SUPSUB
    # Since TIPA doesn't have a generic \sub or \textsubscript command that takes an arbitrary character,
    # this mapping is more for completeness if such commands were used.
    # The primary way to get subscript characters is often by direct Unicode input or specific LaTeX packages.
    if tipa_command_textsubscript not in TIPA_TO_UNI_SUPSUB:
         TIPA_TO_UNI_SUPSUB[tipa_command_textsubscript] = uni_hex
    # if tipa_command_sub not in TIPA_TO_UNI_SUPSUB: # Less standard
    #     TIPA_TO_UNI_SUPSUB[tipa_command_sub] = uni_hex


    # Add to UNI_TO_TIPA_SUPSUB (inverse mapping)
    # This means if we see a subscript IPA character, what TIPA command would produce it?
    # For many, it's just the character itself if not part of a specific TIPA macro.
    # The uni2tipa-supsub.csv should ideally handle this.
    # If uni2tipa-supsub.csv has \textsubscript{ARG}, we can make it specific.
    if uni_hex not in UNI_TO_TIPA_SUPSUB or "ARG" in UNI_TO_TIPA_SUPSUB.get(uni_hex, ""):
         # If TIPA has a command like \textsubscript{a} for U+2090
        corresponding_tipa_cmd_from_csv = UNI_TO_TIPA_SUPSUB.get(uni_hex)
        if corresponding_tipa_cmd_from_csv and char in corresponding_tipa_cmd_from_csv : # e.g. uni2tipa has 2090 -> \textsubscript{a}
            UNI_TO_TIPA_SUPSUB[uni_hex] = corresponding_tipa_cmd_from_csv
        # else: # If no specific TIPA command, the "TIPA representation" might just be the character itself
              # or rely on specific LaTeX packages beyond simple macro replacement.
              # For now, we'll assume uni2tipa-supsub.csv is the primary source for these.
              # UNI_TO_TIPA_SUPSUB[uni_hex] = char # This would be problematic as it's not a TIPA command.
              pass


# Special case for \i and \j as they are dotless i and j in TIPA
# but map to regular i and j with diacritics in IPA.
# Their base characters are U+0131 (dotless i) and U+0237 (dotless j).
# From uni2tipa0.csv: 0131 -> \i, 0237 -> \j
# TIPA_TO_UNI0 already handles this from uni2tipa0.csv.
# We need to ensure that if SUPERSCRIPT_MAP had 'i' or 'j', it's handled correctly.
# SUPERSCRIPT_MAP: 'i': '2071' (superscript i)
# SUPERSCRIPT_MAP: 'j': '02b2' (modifier letter small j)
# The current logic for SUPERSCRIPT_MAP should correctly create:
# TIPA_TO_UNI_SUPSUB['\textsuperscript{i}'] = '2071'
# TIPA_TO_UNI_SUPSUB['\textsuperscript{j}'] = '02b2'
# UNI_TO_TIPA_SUPSUB['2071'] = '\textsuperscript{i}'
# UNI_TO_TIPA_SUPSUB['02b2'] = '\textsuperscript{j}'
# This seems fine.

# --- For Testing Purposes (Optional) ---
if __name__ == "__main__":
    print("UNI_TO_TIPA0:", len(UNI_TO_TIPA0))
    # print(UNI_TO_TIPA0)
    print("TIPA_TO_UNI0:", len(TIPA_TO_UNI0))
    # print(TIPA_TO_UNI0)
    print("UNI_TO_TIPA1:", len(UNI_TO_TIPA1))
    # print(UNI_TO_TIPA1)
    print("TIPA_TO_UNI1:", len(TIPA_TO_UNI1))
    # print(TIPA_TO_UNI1)
    print("UNI_TO_TIPA2:", len(UNI_TO_TIPA2))
    # print(UNI_TO_TIPA2)
    print("TIPA_TO_UNI2:", len(TIPA_TO_UNI2))
    # print(TIPA_TO_UNI2)
    print("UNI_TO_TIPA_TONE:", len(UNI_TO_TIPA_TONE))
    # print(UNI_TO_TIPA_TONE)
    print("TIPA_TO_UNI_TONE:", len(TIPA_TO_UNI_TONE))
    # print(TIPA_TO_UNI_TONE)
    print("UNI_TO_TIPA_SUPSUB (before SUPERSCRIPT_MAP integration):", len(_load_csv_map('uni2tipa-supsub.csv', 0, 1)))
    print("UNI_TO_TIPA_SUPSUB (after):", len(UNI_TO_TIPA_SUPSUB))
    # print(UNI_TO_TIPA_SUPSUB)
    print("TIPA_TO_UNI_SUPSUB (after):", len(TIPA_TO_UNI_SUPSUB))
    # print(TIPA_TO_UNI_SUPSUB)

    # Test specific SUPERSCRIPT_MAP integrations
    print("\n--- SUPERSCRIPT_MAP Integration Tests ---")
    test_chars = ['h', 'n', '(', 'a', 'L']
    for char_key in test_chars:
        ipa_hex = SUPERSCRIPT_MAP.get(char_key)
        if ipa_hex:
            tipa_cmd_super = f"\\super{{{char_key}}}"
            tipa_cmd_textsuper = f"\\textsuperscript{{{char_key}}}"
            print(f"Original: '{char_key}' -> '{ipa_hex}'")
            print(f"  TIPA_TO_UNI_SUPSUB['{tipa_cmd_super}'] = {TIPA_TO_UNI_SUPSUB.get(tipa_cmd_super)}")
            print(f"  TIPA_TO_UNI_SUPSUB['{tipa_cmd_textsuper}'] = {TIPA_TO_UNI_SUPSUB.get(tipa_cmd_textsuper)}")
            print(f"  UNI_TO_TIPA_SUPSUB['{ipa_hex}'] = {UNI_TO_TIPA_SUPSUB.get(ipa_hex)}")

    print("\n--- SUBSCRIPT_MAP Integration Tests ---")
    test_sub_chars = ['a', '1', 'h']
    for char_key in test_sub_chars:
        ipa_hex = SUBSCRIPT_MAP.get(char_key)
        if ipa_hex:
            tipa_cmd_textsub = f"\\textsubscript{{{char_key}}}"
            print(f"Original Subscript: '{char_key}' -> '{ipa_hex}'")
            print(f"  TIPA_TO_UNI_SUPSUB['{tipa_cmd_textsub}'] = {TIPA_TO_UNI_SUPSUB.get(tipa_cmd_textsub)}")
            print(f"  UNI_TO_TIPA_SUPSUB['{ipa_hex}'] = {UNI_TO_TIPA_SUPSUB.get(ipa_hex)}")


    # Check for potential conflicts or specific values
    print("\n--- Specific Value Checks ---")
    print(f"TIPA_TO_UNI0['\\textturnh'] (should be 0265): {TIPA_TO_UNI0.get('\\textturnh')}")
    print(f"UNI_TO_TIPA0['0265'] (should be \\textturnh): {UNI_TO_TIPA0.get('0265')}")
    print(f"TIPA_TO_UNI_SUPSUB['\\textsuperscript{{h}}'] (should be 02b0): {TIPA_TO_UNI_SUPSUB.get('\\textsuperscript{h}')}")
    print(f"UNI_TO_TIPA_SUPSUB['02b0'] (should be \\textsuperscript{{h}}): {UNI_TO_TIPA_SUPSUB.get('02b0')}")
    print(f"TIPA_TO_UNI0['f\\kern-0.1emN']: {TIPA_TO_UNI0.get('f\\kern-0.1emN')}") # Expected: None or the value if present in uni2tipa0
    # This specific command "f\kern-0.1emN" is unlikely to be a key in TIPA_TO_UNI0 as it's a complex command, not a direct symbol mapping.
    # It would be a value in UNI_TO_TIPA0 if some Unicode char maps to it.
    # Check if '207f' (superscript n) is correctly mapped
    print(f"UNI_TO_TIPA_SUPSUB['207f'] (superscript n): {UNI_TO_TIPA_SUPSUB.get('207f')}") # Should be \textsuperscript{n}
    print(f"TIPA_TO_UNI_SUPSUB['\\textsuperscript{{n}}']: {TIPA_TO_UNI_SUPSUB.get('\\textsuperscript{n}')}") # Should be 207f

    # Check if files exist (will print warnings if not)
    _load_csv_map('nonexistent.csv',0,1)

    print("\nDone with basic tests.")
    # print(UNI_TO_TIPA_SUPSUB)
    # print(TIPA_TO_UNI_SUPSUB)
    # Example: 'uni2tipa-supsub.csv' might have:
    # 02b0,\textsuperscript{ARG}
    # 02b1,\textsuperscript{ARG}
    # The goal is for UNI_TO_TIPA_SUPSUB['02b0'] to become '\textsuperscript{h}'
    # and TIPA_TO_UNI_SUPSUB['\textsuperscript{h}'] to become '02b0'.
    # Also TIPA_TO_UNI_SUPSUB['\super{h}'] to become '02b0'.

    # Check 'N' from SUPERSCRIPT_MAP
    # 'N': '1d3a'
    # UNI_TO_TIPA_SUPSUB['1d3a'] should be '\textsuperscript{N}'
    # TIPA_TO_UNI_SUPSUB['\textsuperscript{N}'] should be '1d3a'
    print(f"UNI_TO_TIPA_SUPSUB['1d3a'] (superscript N): {UNI_TO_TIPA_SUPSUB.get('1d3a')}")
    print(f"TIPA_TO_UNI_SUPSUB['\\textsuperscript{{N}}']: {TIPA_TO_UNI_SUPSUB.get('\\textsuperscript{N}')}")
    print(f"TIPA_TO_UNI_SUPSUB['\\super{{N}}']: {TIPA_TO_UNI_SUPSUB.get('\\super{N}')}")

    # Check 'SUBSCRIPT_MAP' integration for 'a'
    # 'a': '2090'
    # UNI_TO_TIPA_SUPSUB['2090'] should be '\textsubscript{a}' (if defined in uni2tipa-supsub.csv)
    # TIPA_TO_UNI_SUPSUB['\textsubscript{a}'] should be '2090'
    print(f"UNI_TO_TIPA_SUPSUB['2090'] (subscript a): {UNI_TO_TIPA_SUPSUB.get('2090')}")
    print(f"TIPA_TO_UNI_SUPSUB['\\textsubscript{{a}}']: {TIPA_TO_UNI_SUPSUB.get('\\textsubscript{a}')}")

    # Check for a value from uni2tipa-supsub.csv that might have "ARG"
    # Example: If 0360,\textsuperscript{ARG} is in uni2tipa-supsub.csv
    # SUPERSCRIPT_MAP has 'P': '0360'
    # We expect UNI_TO_TIPA_SUPSUB['0360'] to become \textsuperscript{P}
    print(f"UNI_TO_TIPA_SUPSUB['0360'] (should be \\textsuperscript{{P}}): {UNI_TO_TIPA_SUPSUB.get('0360')}")

    # Verify that values are not stripped
    # Manually add a test case to uni2tipa0.csv:
    # TESTHEX," \testcommand "
    # Then check:
    # print(f"UNI_TO_TIPA0['TESTHEX']: '{UNI_TO_TIPA0.get('TESTHEX')}'")
    # print(f"TIPA_TO_UNI0[' \\testcommand ']: '{TIPA_TO_UNI0.get(' \\testcommand ')}'")
    # This requires modifying the CSVs, so can't be run directly here without setup.
    # The _load_csv_map function is designed not to strip.

    # Check uni2tipa1.csv for a key like "0301" (COMBINING ACUTE ACCENT)
    # Example: 0301,"\'"
    print(f"UNI_TO_TIPA1['0301'] (acute accent): {UNI_TO_TIPA1.get('0301')}") # Expected: "\'"
    print(f"TIPA_TO_UNI1[\"\\'\"] (acute accent): {TIPA_TO_UNI1.get("\\'")}") # Expected: "0301"

    # Check uni2tipa2.csv for a key like "035c" (DOUBLE BREVE BELOW)
    # Example: 035c,\textdoublebrevebelow
    print(f"UNI_TO_TIPA2['035c'] (double breve below): {UNI_TO_TIPA2.get('035c')}")
    print(f"TIPA_TO_UNI2['\\textdoublebrevebelow'] (double breve below): {TIPA_TO_UNI2.get('\\textdoublebrevebelow')}")

    # Check uni2tipa-tone.csv
    # Example: 02E5,\tone{11}
    print(f"UNI_TO_TIPA_TONE['02E5'] (tone 11): {UNI_TO_TIPA_TONE.get('02E5')}")
    print(f"TIPA_TO_UNI_TONE['\\tone{{11}}'] (tone 11): {TIPA_TO_UNI_TONE.get('\\tone{11}')}")


# Ensure all top-level dicts are defined
expected_dicts = [
    "UNI_TO_TIPA0", "UNI_TO_TIPA1", "UNI_TO_TIPA2", "UNI_TO_TIPA_TONE", "UNI_TO_TIPA_SUPSUB",
    "TIPA_TO_UNI0", "TIPA_TO_UNI1", "TIPA_TO_UNI2", "TIPA_TO_UNI_TONE", "TIPA_TO_UNI_SUPSUB"
]
for d_name in expected_dicts:
    if d_name not in globals():
        raise NameError(f"Mapping dictionary '{d_name}' is not defined.")

print("All mapping dictionaries are defined.")

```
