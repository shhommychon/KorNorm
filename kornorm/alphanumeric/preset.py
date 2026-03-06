# [KorNorm 정규화 프리셋 모듈]
#
# 복잡한 정규화 단계를 하나의 파이프라인으로 묶은 프리셋을 제공합니다.


import re

from kornorm.alphanumeric.contextual_numbers import (
    remove_commas, read_phone_number, read_date_format, read_time_format,
    read_decimal_point, convert_bound_numerals, convert_standalone_numerals, fix_num_exceptions
)
from kornorm.alphanumeric.entities import (
    read_currencies, read_unit_exceptions, read_units,
    read_alphanum_combos, read_abbreviations, read_special_symbols
)
from kornorm.alphanumeric.base import alphabet_to_hangul


def dealers_choice(text: str) -> str:
    """
    기호, 단위, 숫자, 영문 정규화를 순차적으로 수행하는 통합 프리셋입니다.
    
    Args:
        text (str): 원본 텍스트.
        
    Returns:
        str: 12단계 정규화가 모두 완료된 한글 텍스트.
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
    
    # 5. 소수점
    text = read_decimal_point(text)
    
    # 6. 단위
    text = read_unit_exceptions(text)
    text = read_units(text)
    
    # 7. 소문자+숫자 / 대문자+숫자
    text = read_alphanum_combos(text)
    
    # 8. 대문자 약어
    text = read_abbreviations(text)
    
    # 9. 수사 (기수/서수 및 일반 숫자)
    text = convert_bound_numerals(text)
    text = convert_standalone_numerals(text)

    # 10. 단일 특수 기호 및 그리스 문자 처리
    text = read_special_symbols(text)
    
    # 11. 예외 사항 적용
    text = fix_num_exceptions(text)
    
    # 12. 잔류 알파벳 처리
    text = re.sub(r"[a-zA-Z]", lambda m: alphabet_to_hangul(m.group(0)), text)
    
    return text
