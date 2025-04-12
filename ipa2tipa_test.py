import unittest
from ipa2tipa import IPA
from tipa2ipa import TIPA

class IPATest(unittest.TestCase):
    def test_super(self):
        ipa = IPA("ˈtʰiː ˌnãɪ̃ɾ̃iˈtʰu̟ː ˈd͡ʒeɪ ˈpʰiː")
        self.assertEqual(ipa.to_tipa(), r""""t\super{h}i: ""n\~{a}\~{I}\~{R}i"t\super{h}\|+{u}: "\t{dZ}eI "p\super{h}i:""")

    def test_tone(self):
        ipa = IPA("tʰjɛn˧˥ ʈʂʊŋ˥ pɑŋ˥ pʰɤŋ˧˥")
        self.assertEqual(ipa.to_tipa(), r"""t\super{h}jEn\tone{35} \:t{}\:s{}UN\tone{5} pAN\tone{5} p\super{h}7N\tone{35}""")

    def test_tipa2ipa_basic(self):
        # 基本的な変換テスト
        tipa_text = r"""a b c"""
        ipa_result = TIPA(tipa_text).to_ipa()
        self.assertEqual(ipa_result, "a b c")
    
    def test_tipa2ipa_round_trip(self):
        # (IPA → TIPA → IPA)
        original_ipa = "ˈtʰiː"
        tipa = IPA(original_ipa).to_tipa()
        back_to_ipa = TIPA(tipa).to_ipa()
        # just check if normal characters are kept
        self.assertIn("t", back_to_ipa)
        self.assertIn("i", back_to_ipa)


if __name__ == "__main__":
    unittest.main()