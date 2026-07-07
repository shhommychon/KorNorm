# [KorNorm 정규화 프리셋 모듈]
#
# 복잡한 정규화 단계를 하나의 파이프라인으로 묶은 프리셋을 제공합니다.


import re

from kornorm.alphanumeric.contextual_numbers import (
    remove_commas, read_phone_number, read_date_format, read_time_format,
    read_decimal_point, read_interpunct_digits,
    convert_bound_numerals, convert_standalone_numerals, fix_num_exceptions
)
from kornorm.alphanumeric.entities import (
    read_currencies, read_unit_exceptions, read_units,
    read_alphanum_combos, read_abbreviations, read_special_symbols
)
from kornorm.alphanumeric.base import alphabet_to_hangul
from kornorm.alphanumeric.english import read_english_words


def dealers_choice(text: str) -> str:
    """
    기호, 단위, 숫자, 영문 정규화를 순차적으로 수행하는 통합 프리셋입니다.

    Args:
        text (str): 원본 텍스트.

    Returns:
        str: 14단계 정규화가 모두 완료된 한글 텍스트.
    """
    # 1. 쉼표 제거
    text = remove_commas(text)
    
    # 2. 통화
    text = read_currencies(text)
    
    # 3. 전화번호
    text = read_phone_number(text)
    
    # 4. 날짜 및 시간
    text = read_date_format(text)
    text = read_time_format(text)

    # 5. 가운뎃점 숫자 낱자 읽기 (6·25 -> 육이오, 3·1절 -> 삼일절)
    text = read_interpunct_digits(text)
    
    # 6. 단위 (소수점 변환보다 먼저 실행해야 "3.5GHz"의 단위가 숫자 소실 전에 붙는다:
    #    소수점이 먼저 돌면 "삼 쩜 오GHz"가 되어 단위 패턴(숫자+단위)이 빗나간다)
    text = read_unit_exceptions(text)
    text = read_units(text)

    # 7. 소수점
    text = read_decimal_point(text)
    
    # 8. 소문자+숫자 / 대문자+숫자
    text = read_alphanum_combos(text)
    
    # 9. 대문자 약어
    text = read_abbreviations(text)
    
    # 10. 수사 (기수/서수 및 일반 숫자)
    text = convert_bound_numerals(text)
    text = convert_standalone_numerals(text)

    # 11. 단일 특수 기호 및 그리스 문자 처리
    text = read_special_symbols(text)
    
    # 12. 예외 사항 적용
    text = fix_num_exceptions(text)
    
    # 13. 영어 단어 발음 변환 (CMU 사전 등재어: "old school" -> "올드 스쿨")
    text = read_english_words(text)

    # 14. 잔류 알파벳 처리 (사전 미등재 단어·낱자는 알파벳 이름으로 읽기)
    text = re.sub(r"[a-zA-Z]", lambda m: alphabet_to_hangul(m.group(0)), text)

    return text
