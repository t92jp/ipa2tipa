Visit [here](https://t92jp.github.io/ipa2tipa/) to try it out.

# IPA2TIPA
`ipa2tipa` is a script to convert International Phonetic Alphabet (IPA) into TeX IPA (TIPA), an IPA notation for $\LaTeX$.

## Attributes
`ipa2tipa` offers an `IPA` class whose attributes are shown below.

| Attribute        | Content 
| --               | -- 
| `ipa.xords`[^*]  | IPA decomposed and express by hex according to UTF-8 
| `ipa.charset`    | xords arranged in the unit of character 
| `ipa.tipa`       | TIPA converted from IPA 

IPA is converted into TIPA in this order.

[^*]: xords stands for "hexadecimal `ord`s". <br>
(`ord` is a built-in function translating char into Unicode decimal)

## Methods
To realize translation above, ipa2tipa has some methods.

| Method           | In -> Out      | Content 
|--                | --             | --
| `ipa._decompose` | ipa -> str[]   | decompose IPAs into UTF-8 hexadecimals
| `ipa._parse`     | ipa -> str[][] | put a character and modifiers together
| `ipa._ipa2tipa`  | ipa -> str     | convert parsed UTF-8s into TIPA
| `ipa.to_tipa`    | ipa -> str     | get ipa.tipa

## Files
| Name                  | Content 
|--                     |--
| `README.md`           | what you are reading right now
| `LICENSE.md`          | this script is distributed under MIT License
| `ipa2tipa.py`         | main script 
| `test_ipa2tipa.py`    | brief unittests implemented with a standard library `unittest`
| `uni2tipa-subsup.csv` | data in the format of `UTF-8 (hex), tipa macro denoting next superscript or subscript`
| `uni2tipa-tone.csv`   | data in the format of `UTF-8 (hex), tipa macro of tone letters`
| `uni2tipa0.csv`       | data in the format of `UTF-8 (hex), tipa macro taking 0 args`
| `uni2tipa1.csv`       | data in the format of `UTF-8 (hex), tipa macro taking 1 arg`
| `uni2tipa2.csv`       | data in the format of `UTF-8 (hex), tipa macro taking 2 args`