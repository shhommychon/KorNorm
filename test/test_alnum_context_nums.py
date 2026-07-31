import unittest
from kornorm.alphanumeric.contextual_numbers import (
    remove_commas, read_phone_number, read_date_format,
    read_time_format, read_decimal_point, convert_bound_numerals,
    convert_standalone_numerals, fix_num_exceptions
)

class TestContextualNumbers(unittest.TestCase):
    def test_remove_commas(self):
        """숫자 사이의 쉼표를 제거하는지 테스트"""
        self.assertEqual(remove_commas("1,234,567"), "1234567")

    def test_read_phone_number(self):
        """전화번호 패턴을 한글 발음으로 변환하는지 테스트"""
        self.assertEqual(read_phone_number("010-1234-5678"), "공일공일이삼사오육칠팔")
        self.assertEqual(read_phone_number("02-1588-1111"), "공이일오팔팔일일일일")

    def test_read_phone_number_keeps_leading_space(self):
        """패턴이 선행 구분자로 소비하는 공백을 지우지 않고 보존하는지 테스트"""
        self.assertEqual(
            read_phone_number("내 폰번호는 010-1234-5678이야"),
            "내 폰번호는 공일공일이삼사오육칠팔이야",
        )
        self.assertEqual(read_phone_number("A 010-1234-5678 B"), "A 공일공일이삼사오육칠팔 B")

    def test_read_date_format(self):
        """날짜 패턴(YYYY.MM.DD)을 한글로 변환하는지 테스트"""
        self.assertEqual(read_date_format("2023.10.05"), "2023년 10월 5일")
        self.assertEqual(read_date_format("23/1/1"), "23년 1월 1일")

    def test_read_time_format(self):
        """시간 패턴(HH:MM:SS)을 한글로 변환하는지 테스트"""
        self.assertEqual(read_time_format("14:30"), "14시 30분")
        self.assertEqual(read_time_format("14:30:05"), "14시 30분 5초")

    def test_read_decimal_point(self):
        """소수점 기호를 한글 발음으로 변환하는지 테스트"""
        self.assertEqual(read_decimal_point("3.14"), "3 쩜 일사")

    def test_convert_bound_numerals(self):
        """의존 명사가 결합된 숫자를 고유어로 치환하는지 테스트"""
        self.assertEqual(convert_bound_numerals("3 개"), "세개")
        self.assertEqual(convert_bound_numerals("20명"), "스무명")

    def test_convert_standalone_numerals(self):
        """단독 숫자를 한자어로 치환하는지 테스트"""
        self.assertEqual(convert_standalone_numerals("123"), "백이십삼")

    def test_fix_num_exceptions(self):
        """수사 결합 예외나 잘못된 읽기를 교정하는지 테스트"""
        self.assertEqual(fix_num_exceptions("육월"), "유월")
        self.assertEqual(fix_num_exceptions("한 번째"), "첫번째")

if __name__ == "__main__":
    unittest.main()
