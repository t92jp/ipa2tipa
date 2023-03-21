from unicodedata import decomposition
import csv
from itertools import chain

class ipa():
    # set dict
    UNI2TIPA = list()
    for i in range(3):
        d = dict()
        with open(f"uni2tipa{i}.csv", 'r', encoding="utf-8") as f:
            for l in csv.reader(f, quoting=csv.QUOTE_NONE):
                d[l[0]] = l[1]
        UNI2TIPA.append(d)

    def __init__(self, txt):
        self.ipa = txt
        self.xords = self.decompose()
        self.charlist = self.parse()
        self.tipa = self.ipa2tipa()

    def decompose(self):
        """ "ccc" -> "xxxx xxxx xxxx" """
        xords = list()
        for c in self.ipa:
            decom = decomposition(c) # 'c' -> "cc"
            if decom: xords += decom.split() # 'XXXX XXXX' -> ['XXXX', 'XXXX']
            else: xords.append(hex(ord(c))[2:].rjust(4, '0')) # 'c' -> 'XXXX'
        return list(map(lambda x: x.lower(), xords)) 
    
    def parse(self): 
        """ "xxxx xxxx xxxx" -> [["xxxx", "xxxx"], ["xxxx"]] """
        i = len(self.xords)-1
        xords = self.xords
        charlist = list()
        while i >= 0: 
            l = list()
            while xords[i] in self.UNI2TIPA[1]: # recognize modifier
                l.insert(0, xords[i])
                i -= 1
            l.insert(0, xords[i])
            i -= 1
            charlist.insert(0, l)
        return charlist

    def ipa2tipa(self):
        result = self.charlist
        for i in range(len(self.charlist)):
            # convert 0-ary char
            try: result[i][0] = self.UNI2TIPA[0][result[i][0]]
            except KeyError: continue
            # convert 1-ary modifier
            while result[i][-1] in self.UNI2TIPA[1]:
                result[i][0] =  self.UNI2TIPA[1][result[i].pop()] + '{' + result[i][0] + '}'
        result = list(chain.from_iterable(result)) # flatten
        
        # convert 2-ary modifier
        i = 0
        while i < len(result):
            if result[i] in self.UNI2TIPA[2]:
                result[i-1] = self.UNI2TIPA[2][result[i]] + '{' + result[i-1] + result[i+1] + '}'
                result = result[:i] + result[i+2:]
            else: i += 1
        return ''.join(result)

if __name__ == "__main__":
    txt = ipa("ko̞ko̞ ɲ̟i ɲ̟ɯ̟ᵝːɾʲo̞kɯ̟ᵝ ɕi̥te̞ kɯ̟ᵝda̠sa̠i")
    print("TIPA:", txt.tipa)
        