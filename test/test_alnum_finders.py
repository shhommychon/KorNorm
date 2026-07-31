import unittest
from kornorm.alphanumeric.contextual_numbers import (
    read_phone_number, read_date_format, read_time_format,
    read_interpunct_digits, convert_bound_numerals,
    find_phone_number, find_date_format, find_time_format,
    find_interpunct_digits, find_bound_numerals
)
from kornorm.alphanumeric.entities import (
    read_currencies, read_unit_exceptions, read_units, read_special_symbols,
    find_currencies, find_unit_exceptions, find_units, find_special_symbols
)

# read↔find 동치 계약 검증용 (finder, 대응 컨버터) 쌍
FIND_READ_PAIRS = [
    (find_currencies, read_currencies),
    (find_unit_exceptions, read_unit_exceptions),
    (find_units, read_units),
    (find_special_symbols, read_special_symbols),
    (find_phone_number, read_phone_number),
    (find_date_format, read_date_format),
    (find_time_format, read_time_format),
    (find_interpunct_digits, read_interpunct_digits),
    (find_bound_numerals, convert_bound_numerals),
]

# 동치 계약 공유 샘플 (매치 유무·다중 매치·경계 케이스 혼재)
SAMPLES = [
    "배터리 3400mAh 용량과 30km 구간",
    "$5와 300¥, €12.5",
    "MP3 파일과 5G 요금제",
    "3.5GHz와 15GB",
    "α+β=100%",
    "문의는 010-1234-5678",
    "1950-06-25 발발",
    "회의는 9:30, 종료는 11:00",
    "6·25와 3·1절",
    "커피 3잔과 장갑 3켤레",
    "정상 문장입니다",
    '',
]

class TestAlnumFinders(unittest.TestCase):
    def _assert_spans(self, text, result):
        """보고된 스팬을 원문에서 잘라내면 매치 문자열 그대로여야 함"""
        for start, end, surface in result:
            self.assertEqual(text[start:end], surface)

    def test_find_currencies(self):
        """전위·후위 통화 기호 결합 금액의 다중 탐지를 테스트"""
        text = "$5와 300¥, €12.5"
        result = find_currencies(text)
        self.assertEqual(result, [(0, 2, "$5"), (4, 8, "300¥"), (10, 15, "€12.5")])
        self._assert_spans(text, result)

    def test_find_unit_exceptions(self):
        """관용 영숫자 예외 탐지와 더 큰 토큰 경계 가드를 테스트"""
        text = "MP3 파일과 5G 요금제"
        result = find_unit_exceptions(text)
        self.assertEqual(result, [(0, 3, "MP3"), (8, 10, "5G")])
        self._assert_spans(text, result)

        # "3.5GHz"의 "5G", "15GB"의 "5G"는 컨버터와 똑같이 미탐지
        self.assertEqual(find_unit_exceptions("3.5GHz와 15GB"), [])

    def test_find_units(self):
        """숫자+단위 매치의 다중 탐지와 긴 단위 우선 선점을 테스트"""
        text = "배터리 3400mAh 용량과 30km 구간"
        result = find_units(text)
        self.assertEqual(result, [(4, 11, "3400mAh"), (16, 20, "30km")])
        self._assert_spans(text, result)

        # 긴 단위(m/s)가 선점한 스팬과 겹치는 짧은 단위(m) 후보는 제외
        self.assertEqual(find_units("속도 10m/s"), [(3, 8, "10m/s")])

        # 단독 실행 미러: 소수점 처리 전이므로 컨버터처럼 "5GHz"가 잡힌다
        self.assertEqual(find_units("3.5GHz"), [(2, 6, "5GHz")])

    def test_find_special_symbols(self):
        """특수 기호·그리스 문자 낱자 탐지를 테스트"""
        text = "α+β=100%"
        result = find_special_symbols(text)
        self.assertEqual(
            result, [(0, 1, 'α'), (1, 2, '+'), (2, 3, 'β'), (3, 4, '='), (7, 8, '%')])
        self._assert_spans(text, result)

    def test_find_phone_number(self):
        """전화번호 탐지를 테스트 (패턴이 소비하는 선행 구분 공백은 스팬에서 제외)"""
        text = "문의는 010-1234-5678"
        result = find_phone_number(text)
        self.assertEqual(result, [(4, 17, "010-1234-5678")])
        self._assert_spans(text, result)

    def test_find_date_format(self):
        """날짜 형식 탐지를 테스트"""
        text = "1950-06-25 발발"
        result = find_date_format(text)
        self.assertEqual(result, [(0, 10, "1950-06-25")])
        self._assert_spans(text, result)

    def test_find_time_format(self):
        """시간 형식의 다중 탐지를 테스트"""
        text = "회의는 9:30, 종료는 11:00"
        result = find_time_format(text)
        self.assertEqual(result, [(4, 8, "9:30"), (14, 19, "11:00")])
        self._assert_spans(text, result)

    def test_find_interpunct_digits(self):
        """가운뎃점 숫자 표기의 다중 탐지를 테스트"""
        text = "6·25와 3·1절"
        result = find_interpunct_digits(text)
        self.assertEqual(result, [(0, 4, "6·25"), (6, 9, "3·1")])
        self._assert_spans(text, result)

    def test_find_bound_numerals(self):
        """숫자+분류사 수사의 다중 탐지를 테스트"""
        text = "커피 3잔과 장갑 3켤레"
        result = find_bound_numerals(text)
        self.assertEqual(result, [(3, 5, "3잔"), (10, 13, "3켤레")])
        self._assert_spans(text, result)

    def test_find_matches_read(self):
        """컨버터가 치환하는 입력과 finder가 탐지하는 입력이 일치하는지 테스트"""
        for find_func, read_func in FIND_READ_PAIRS:
            for sample in SAMPLES:
                changed = (read_func(sample) != sample)
                found = (find_func(sample) != [])
                self.assertEqual(
                    changed, found, f"{find_func.__name__}: {sample}")

if __name__ == "__main__":
    unittest.main()
