# IPA2TIPA
`ipa2tipa` is a script to convert International Phonetic Alphabet (IPA) into TeX IPA (TIPA), an IPA notation for $\LaTeX$.

## Usage

### Simple Usage
```python
from ipa2tipa import IPA

# Create IPA string and convert to TIPA
ipa = IPA("ˈtʰiː")
tipa = ipa.to_tipa()
print(tipa)  # "t\super{h}i:

# IPA and TIPA are str subclasses
print(isinstance(ipa, str))    # True
print(isinstance(tipa, str))   # True
print(len(ipa))                # 4 (Unicode character count)
```

### Examples

```python
from ipa2tipa import IPA

# Aspiration and length
ipa = IPA("tʰiː")
print(ipa.to_tipa())  # t\super{h}i:

# Nasalization
ipa = IPA("nãɪ̃")
print(ipa.to_tipa())  # n\~{a}\~{I}

# Tone marks
ipa = IPA("tʰjɛn˧˥")
print(ipa.to_tipa())  # t\super{h}jEn\tone{35}

# String operations work as expected
ipa = IPA("ko̞ko̞")
print(ipa.upper())           # KO̞KO̞
print(ipa + " test")         # ko̞ko̞ test
```

## Architecture

The library provides two main classes:

**`IPA(str)`** → `.to_tipa()` → **`TIPA(str)`**

Both `IPA` and `TIPA` are subclasses of `str`, representing actual IPA and TIPA strings respectively.

### Components

| Component | Description |
|-----------|-------------|
| `IPA` | IPA string class with `.to_tipa()` method |
| `TIPA` | TIPA string class (str subclass) |
| `UnicodeUnit` | Internal representation of a Unicode character with base and modifiers |

### UnicodeUnit Structure

`UnicodeUnit` is used internally to represent the structure of Unicode characters:
- `base`: The base character codepoint (e.g., `'0074'` for 't')
- `modifiers`: List of modifier codepoints (e.g., aspiration, nasalization)

### Conversion Process

Internally, the conversion follows these steps:
1. Decompose IPA string into Unicode codepoints
2. Group codepoints into base + modifiers (`UnicodeUnit`)
3. Convert to TIPA notation

## Files
| Name                  | Content 
|--                     |--
| `README.md`           | what you are reading right now
| `LICENSE.md`          | this script is distributed under MIT License
| `ipa2tipa.py`         | main script 
| `ipa2tipa_test.py`    | brief unittests implemented with a standard library `unittest`
| `uni2tipa/uni2tipa-supsub.tsv` | data in the format of `UTF-8 (hex), tipa macro denoting next super/subscript`
| `uni2tipa/uni2tipa-tone.tsv`   | data in the format of `UTF-8 (hex), tipa macro of tone letters`
| `uni2tipa/uni2tipa0.tsv`       | data in the format of `UTF-8 (hex), tipa macro taking 0 args`
| `uni2tipa/uni2tipa1.tsv`       | data in the format of `UTF-8 (hex), tipa macro taking 1 arg`
| `uni2tipa/uni2tipa2.tsv`       | data in the format of `UTF-8 (hex), tipa macro taking 2 args`
