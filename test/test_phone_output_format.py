import unittest
from kornorm.phonology.engine import apply_phonology
from kornorm.utils.jamo import decompose

class TestOutputFormat(unittest.TestCase):
    def test_hangul_with_punctuation(self):
        """문장부호가 섞여도 완성형 조립이 무너지지 않는지 테스트"""
        self.assertEqual(apply_phonology("같이 갈래?", output_format="hangul"), "가치 갈래?")
        self.assertEqual(apply_phonology("꽃이 피었다!", output_format="hangul"), "꼬치 피얻따!")
        self.assertEqual(apply_phonology("책 읽는 중...", output_format="hangul"), "챙 닝는 중...")

    def test_hangul_with_latin_and_digits(self):
        """영문·숫자 토큰이 표면형 그대로 보존되는지 테스트"""
        self.assertEqual(apply_phonology("MP3 파일 목록", output_format="hangul"), "MP3 파일 몽녹")
        self.assertEqual(apply_phonology("3연대 막사", output_format="hangul"), "3연대 막싸")
        self.assertEqual(apply_phonology("A4 용지 값", output_format="hangul"), "A4 용지 갑")

    def test_untaggable_scripts_passthrough(self):
        """어휘 태그로 오태깅되는 한자 원문·호환 자모 낱자가 표면형 그대로 보존되는지 테스트"""
        self.assertEqual(apply_phonology("漢字 공부", output_format="hangul"), "漢字 공부")
        self.assertEqual(apply_phonology("ㄱㄴㄷ 순서", output_format="hangul"), "ㄱㄴㄷ 순서")
        self.assertEqual(apply_phonology("ㅋㅋㅋ 웃겨", output_format="hangul"), "ㅋㅋㅋ 욷껴")

    def test_non_hangul_only(self):
        """한글이 없는 입력도 세 포맷 모두 원문 그대로 돌려주는지 테스트"""
        for output_format in ("hangul", "positional", "compat"):
            self.assertEqual(apply_phonology("!!", output_format=output_format), "!!")
            self.assertEqual(apply_phonology("abc", output_format=output_format), "abc")

    def test_format_equivalence(self):
        """세 포맷이 같은 발음을 서로 다른 표기로 내놓는지 테스트"""
        self.assertEqual(apply_phonology("독립문", output_format="hangul"), "동님문")
        self.assertEqual(apply_phonology("독립문", output_format="positional"), decompose("동님문"))
        self.assertEqual(apply_phonology("독립문", output_format="compat"), "ㄷㅗㅇㄴㅣㅁㅁㅜㄴ")

if __name__ == "__main__":
    unittest.main()
