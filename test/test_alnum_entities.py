import unittest
from kornorm.alphanumeric.entities import (
    read_currencies, read_unit_exceptions, read_units,
    read_alphanum_combos, read_abbreviations, read_special_symbols
)

class TestEntities(unittest.TestCase):
    def test_read_currencies(self):
        """통화 기호를 한글로 치환하는지 테스트"""
        self.assertEqual(read_currencies("$100"), "100달러")
        self.assertEqual(read_currencies("100₩"), "100원")

    def test_read_unit_exceptions(self):
        """단위 정규화 전 예외 영숫자 결합을 처리하는지 테스트"""
        self.assertEqual(read_unit_exceptions("mp3"), "엠피쓰리")
        self.assertEqual(read_unit_exceptions("5G"), "파이브쥐")

    def test_read_units(self):
        """물리 단위 기호를 한글로 치환하는지 테스트"""
        self.assertEqual(read_units("10 km"), "10킬로미터")
        self.assertEqual(read_units("5kg"), "5킬로그램")

    def test_read_compound_units(self):
        """전하량·전력량·퍼센트포인트류 합성 단위를 통째로 치환하는지 테스트"""
        self.assertEqual(read_units("3400mAh"), "3400밀리암페어시")
        self.assertEqual(read_units("77kWh"), "77킬로와트시")
        self.assertEqual(read_units("5%p"), "5퍼센트포인트")
        # 합성 단위가 구성 요소 단위(ma·kw·%)로 쪼개 읽히지 않아야 함
        self.assertEqual(read_units("30ma"), "30밀리암페어")

    def test_read_alphanum_combos(self):
        """영문과 숫자가 혼합된 토큰을 낱자 발음으로 변환하는지 테스트"""
        self.assertEqual(read_alphanum_combos("H2O"), "에이치투오")
        self.assertEqual(read_alphanum_combos("3M"), "쓰리엠")

    def test_read_abbreviations(self):
        """대문자 약어를 한글로 치환하는지 테스트"""
        self.assertEqual(read_abbreviations("GPT"), "쥐피티")

    def test_read_special_symbols(self):
        """특수 기호 및 그리스 문자를 한글로 치환하는지 테스트"""
        self.assertEqual(read_special_symbols("A+B"), "A플러스B")
        self.assertEqual(read_special_symbols("100%"), "100퍼센트")

if __name__ == "__main__":
    unittest.main()
