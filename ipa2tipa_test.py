import unittest
from ipa2tipa import IPA, TIPA


class IPAToTIPATest(unittest.TestCase):
    """ipa to tipa conversion tests"""
    
    def test_convert_basic(self):
        """basics"""
        ipa = IPA("ti")
        tipa = ipa.to_tipa()
        self.assertIsInstance(tipa, TIPA)
        self.assertIsInstance(tipa, str)
        self.assertIn("t", tipa)
        self.assertIn("i", tipa)
    
    def test_ipa_is_str(self):
        """see if IPA is subclass of str"""
        ipa = IPA("tʰiː")
        self.assertIsInstance(ipa, str)
        self.assertEqual(len(ipa), 4)  # Unicode文字数
        self.assertTrue(ipa.startswith("t"))
    
    def test_tipa_is_str(self):
        """see if TIPA is subclass of str"""
        ipa = IPA("ti")
        tipa = ipa.to_tipa()
        self.assertIsInstance(tipa, str)
        self.assertTrue(isinstance(tipa, TIPA))


class IntegrationTest(unittest.TestCase):
    """Integration tests"""
    
    def test_basic_conversion(self):
        """basics"""
        ipa = IPA("ˈtʰiː")
        tipa = ipa.to_tipa()
        self.assertIsInstance(tipa, str)
        self.assertIn("t", tipa)
    
    def test_super(self):
        """test with superscripts"""
        ipa = IPA("ˈtʰiː ˌnãɪ̃ɾ̃iˈtʰu̟ː ˈd͡ʒeɪ ˈpʰiː")
        tipa = ipa.to_tipa()
        expected = r""""t\super{h}i: ""n\~{a}\~{I}\~{R}i"t\super{h}\|+{u}: "\t{dZ}eI "p\super{h}i:"""
        self.assertEqual(tipa, expected)

    def test_tone(self):
        """test with tone marks"""
        ipa = IPA("tʰjɛn˧˥ ʈʂʊŋ˥ pɑŋ˥ pʰɤŋ˧˥")
        tipa = ipa.to_tipa()
        expected = r"""t\super{h}jEn\tone{35} \:t{}\:s{}UN\tone{5} pAN\tone{5} p\super{h}7N\tone{35}"""
        self.assertEqual(tipa, expected)


if __name__ == "__main__":
    unittest.main()
