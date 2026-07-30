import unittest
from kornorm.alphanumeric.base import num_to_sino, num_to_native, alphabet_to_hangul

class TestBase(unittest.TestCase):
    def test_num_to_sino(self):
        """숫자를 한자어 수사로 변환하는지 테스트"""
        self.assertEqual(num_to_sino("1234"), "천이백삼십사")
        self.assertEqual(num_to_sino("10"), '십')

    def test_num_to_sino_zero(self):
        """0으로만 이루어진 수를 영으로 읽는지 테스트"""
        self.assertEqual(num_to_sino('0'), '영')
        self.assertEqual(num_to_sino("00"), '영')
        self.assertEqual(num_to_sino("007"), '칠')

    def test_num_to_native(self):
        """숫자를 고유어 수사로 변환하는지 테스트"""
        self.assertEqual(num_to_native('3'), '세')
        self.assertEqual(num_to_native("120"), "백스무")

    def test_alphabet_to_hangul(self):
        """단일 알파벳을 한글 발음으로 변환하는지 테스트"""
        self.assertEqual(alphabet_to_hangul('A'), "에이")
        self.assertEqual(alphabet_to_hangul('z'), '즤')

if __name__ == "__main__":
    unittest.main()
