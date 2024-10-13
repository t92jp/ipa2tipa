import unittest
from ipa2tipa import IPA

class IPATest(unittest.TestCase):
    def test_super(self):
        ipa = IPA("ˈtʰiː ˌnãɪ̃ɾ̃iˈtʰu̟ː ˈd͡ʒeɪ ˈpʰiː")
        self.assertEqual(ipa.to_tipa(), r""""t\super{h}i: ""n\~{a}\~{I}\~{R}i"t\super{h}\|+{u}: "\t{dZ}eI "p\super{h}i:""")

    def test_tone(self):
        ipa = IPA("tʰjɛn˧˥ ʈʂʊŋ˥ pɑŋ˥ pʰɤŋ˧˥")
        self.assertEqual(ipa.to_tipa(), r"""t\super{h}jEn\tone{35} \:t{}\:s{}UN\tone{5} pAN\tone{5} p\super{h}7N\tone{35}""")


if __name__ == "__main__":
    unittest.main()