Visit [here](https://t92jp.github.io/ipa2tipa/) to try it out.

# IPA to TIPA
ipa2tipa is a program to convert International Phonetic Alphabet (IPA) into TeX IPA (TIPA), an IPA notation for $\LaTeX$.

## Attributes
ipa2tipa offers an `ipa` class having some attributes shown below.

| Attribute        | Content 
| --               | -- 
| `ipa.ipa`        | International Phonetic Alphabet itself 
| `ipa.xords`[^*]  | IPA decomposed and express by hex according to UTF-8 
| `ipa.charset`    | xords arranged in the unit of character 
| `ipa.tipa`       | TIPA converted from IPA 

IPA is converted into TIPA in this order.

[^*]: xords stands for "hexadecimal `ord`s. <br>
(`ord` is a built-in function translating char into Unicode decimal)

## Methods
To realize translation above, ipa2tipa has some methods.

| Method          | In -> Out      | Content 
|--               | --             | --
| `ipa.init`      | ipa -> void    | convert IPAs into each attribute 
| `ipa.decompose` | ipa -> str[]   | decompose IPAs into UTF-8 hexadecimals
| `ipa.recognize` | ipa -> str[][] | put a character and modifiers together
| `ipa.ipa2tipa`  | ipa -> str     | convert parsed UTF-8s into TIPA

## Files
| Name            | Content 
|--               |--
| `docs`          | files for https://t92jp.github.io/ipa2tipa/
| `README.md`     | what you're reading right now
| `uni2tipa0.csv` | data in the format of `UTF-8 (hex), tipa macro taking 0 args`
| `uni2tipa1.csv` | data in the format of `UTF-8 (hex), tipa macro taking 1 arg`
| `uni2tipa2.csv` | data in the format of `UTF-8 (hex), tipa macro taking 2 args`
