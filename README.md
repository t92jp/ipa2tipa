# IPA2TIPA

Convert International Phonetic Alphabet (IPA) to TeX IPA (TIPA).

Demo: https://t92jp.github.io/ipa2tipa/

# Project layout

- uni2tipa: mapping tables
- py/ipa2tipa: Python library
- rs: Dioxus web app

## uni2tipa (mapping tables)

Shared mapping tables used by both implementations.

| File name | Description |
| :-------- | :---------- |
| uni2tipa0.tsv | TIPA macro taking 0 args (codepoint -> macro) |
| uni2tipa1.tsv | TIPA macro taking 1 arg (codepoint -> macro) |
| uni2tipa2.tsv | TIPA macro taking 2 args (codepoint -> macro) |
| uni2tipa-tone.tsv | Tone letters (codepoint -> tone number) |
| uni2tipa-rtone.tsv | Reverse tone letters (codepoint -> tone number) |
| uni2tipa-supsub.tsv | Superscript/subscript markers (codepoint -> macro) |

## py (Python library)

```python
from ipa2tipa import IPA

print(IPA("ˈtʰiː").to_tipa())
```

Examples:

```python
from ipa2tipa import IPA

print(IPA("tʰiː").to_tipa())     # t\super{h}i:
print(IPA("nãɪ̃").to_tipa())     # n\~{a}\~{I}
print(IPA("tʰjɛn˧˥").to_tipa()) # t\super{h}jEn\tone{35}
```

## rs (Dioxus web app)

```bash
cd rs
dx serve
```

## License

MIT