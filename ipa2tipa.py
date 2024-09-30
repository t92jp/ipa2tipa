from unicodedata import decomposition
import csv
from pathlib import Path

class IPA(str):
    # Load dictionaries
    UNI2TIPA = []
    script_dir = Path(__file__).parent
    for i in range(3):
        with open(script_dir / f"uni2tipa{i}.csv", 'r', encoding="utf-8") as f:
            UNI2TIPA.append({row[0]: row[1] for row in csv.reader(f, quoting=csv.QUOTE_NONE)})

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
        """Convert string to list of lowercase hex codes."""
        xords = []
        for c in self:
            decom = decomposition(c)
            if decom:
                xords.extend(code.lower() for code in decom.split())
            else:
                xords.append(f"{ord(c):04x}")
        return xords
    
    def _parse(self):
        """Group hex codes into characters with modifiers."""
        charlist = []
        i = len(self.xords) - 1
        while i >= 0:
            char = []
            while i >= 0 and self.xords[i] in self.UNI2TIPA[1]:
                char.insert(0, self.xords[i])
                i -= 1
            if i >= 0:
                char.insert(0, self.xords[i])
                i -= 1
            charlist.insert(0, char)
        return charlist

    def _ipa2tipa(self):
        result = []
        for char in self.charlist:
            base = self.UNI2TIPA[0].get(char[0], char[0])
            for modifier in char[1:]:
                if modifier in self.UNI2TIPA[1]:
                    base = f"{self.UNI2TIPA[1][modifier]}{{{base}}}"
            result.append(base)

        # Handle 2-ary modifiers
        i = 0
        while i < len(result) - 1:
            if result[i] in self.UNI2TIPA[2]:
                result[i-1] = f"{self.UNI2TIPA[2][result[i]]}{{{result[i-1]}{result[i+1]}}}"
                result = result[:i] + result[i+2:]
            else:
                i += 1

        return ''.join(result)

    def to_tipa(self):
        """Convert IPA to TIPA."""
        return self.tipa

if __name__ == "__main__":
    ipa = IPA("ko̞ko̞ ɲ̟i ") + IPA("ɲ̟ɯ̟ᵝːɾʲo̞kɯ̟ᵝ ɕi̥te̞ ") + IPA("kɯ̟ᵝda̠sa̠i")
    print(type(ipa))
    print("Original:", ipa)
    print("TIPA:", ipa.to_tipa())