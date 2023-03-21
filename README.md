Note that this is a program for personal practicing

# IPA to TIPA
ipa2tipa is a program to convert IPA: International Phonetid Alphabet to TIPA, a IPA notation for TeX.

## Attribute
ipa2tipa offers a class named "ipa" having some attribute shown below.

| Attribute        | Content 
| --               | -- 
| `ipa.ipa`        | International Phonetic Alphabet itself 
| `ipa.xords`[^*]  | IPA decomposed and express by hex according to UTF-8 
| `ipa.charset`    | xords arranged in the unit of character 
| `ipa.tipa`       | TIPA translated from IPA 

IPA is translated into TIPA in this order.

[^*]: xords stands for "hexadecimal `ord`s. <br>
(`ord` is a built-in function translating char into Unicode decimal)

## Method
To realize translation above, ipa2tipa has some methods.

| Method          | In -> Out      | Content 
|--               | --             | --
| `ipa.init`      | ipa -> void    | convert IPAs into each attribute 
| `ipa.decompose` | ipa -> str[]   | decompose IPAs into UTF-8 hexadecimals
| `ipa.recognize` | ipa -> str[][] | put a character and modifiers together
| `ipa.ipa2tipa`  | ipa -> str     | translate parsed UTF-8s into TIPA