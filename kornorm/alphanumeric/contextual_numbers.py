# [KorNorm 숫자 문맥 정규화 모듈]
#
# 날짜, 시간, 전화번호 등 숫자가 포함된 문맥을 개별 함수로 정규화합니다.


import re
from typing import List, Tuple

from kornorm.alphanumeric.constants import (
    SINO_DIGITS, RE_COMMAS, RE_DATE, RE_TIME, RE_PHONE, RE_FLOAT, RE_BOUND_NUM, RE_SINO_NUM,
    RE_INTERPUNCT_NUM,
)
from kornorm.alphanumeric.base import num_to_sino, num_to_native


def _find_pattern_matches(pattern: re.Pattern, text: str) -> List[Tuple[int, int, str]]:
    """
    컴파일된 패턴의 모든 매치를 (시작, 끝, 매치 문자열)로 수집합니다.

    Args:
        pattern (re.Pattern): 대응 컨버터가 치환에 쓰는 바로 그 패턴.
        text (str): 검사할 원본 텍스트.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def remove_commas(text: str) -> str:
    """
    큰 숫자의 천 단위 쉼표(,)를 제거합니다.

    Ref:
        https://github.com/Kyubyong/g2pK/blob/master/g2pk/numerals.py#L24
    
    Args:
        text (str): 원본 텍스트.
        
    Returns:
        str: 쉼표가 제거된 텍스트.
    """
    return RE_COMMAS.sub('', text)

def read_phone_number(text: str, zero_char: str = "공", digit_map: dict = SINO_DIGITS) -> str:
    """
    전화번호 패턴을 감지하여 숫자를 개별적으로 변환하고 구분 기호를 제거합니다.

    패턴이 선행 구분자로 소비하는 공백("번호는 010-…"의 앞 공백)은 구분 기호가
    아니라 어절 경계이므로 지우지 않고 보존합니다.

    Args:
        text (str): 원본 텍스트.
        zero_char (str): 숫자 '0'을 읽을 방식 (기본값: "공").
        digit_map (dict): 숫자별 한자어 매핑 사전.

    Returns:
        str: 전화번호가 한글 발음으로 변환된 텍스트.
    """
    def _repl(m):
        raw = m.group(0)
        prefix = raw[:len(raw) - len(raw.lstrip())]
        digits = [c for c in raw if c.isdigit()]
        return prefix + "".join(digit_map.get(d, d) if d != '0' else zero_char for d in digits)
    return RE_PHONE.sub(_repl, text)

def find_phone_number(text: str) -> List[Tuple[int, int, str]]:
    """
    전화번호 패턴 매치를 텍스트 무변경으로 위치와 함께 보고합니다.

    read_phone_number가 단독 실행으로 치환하는 바로 그 매치들을 돌려주는 조회 전용
    짝꿍입니다. read(text) != text와 find(text) != [] 는 동치입니다. 패턴이 선행
    구분자로 소비하는 공백은 보고 스팬에서 잘라내고 번호 시작 위치를 돌려줍니다
    (read_phone_number도 그 공백은 지우지 않고 보존 — 양쪽 다 번호만 대상입니다).

    Args:
        text (str): 검사할 원본 텍스트.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    results = []
    for match in RE_PHONE.finditer(text):
        surface = match.group(0)
        stripped = surface.lstrip()
        start = match.start() + (len(surface) - len(stripped))
        results.append((start, match.end(), stripped))
    return results

def read_date_format(text: str) -> str:
    """
    날짜 형식(YYYY.MM.DD 등)을 '년, 월, 일' 형식의 한글로 통일합니다.

    Ref:
        https://github.com/hash2430/pitchtron/blob/hard/text/datestime.py
    
    Args:
        text (str): 원본 텍스트.
        
    Returns:
        str: 날짜가 한글 포맷으로 변환된 텍스트.
    """
    return RE_DATE.sub(lambda m: f"{m.group(1)}년 {int(m.group(2))}월 {int(m.group(3))}일", text)

def find_date_format(text: str) -> List[Tuple[int, int, str]]:
    """
    날짜 형식(YYYY.MM.DD 등) 매치를 텍스트 무변경으로 위치와 함께 보고합니다.

    read_date_format이 단독 실행으로 치환하는 바로 그 매치들을 돌려주는 조회 전용
    짝꿍입니다. read(text) != text와 find(text) != [] 는 동치입니다.

    Args:
        text (str): 검사할 원본 텍스트.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    return _find_pattern_matches(RE_DATE, text)

def read_time_format(text: str) -> str:
    """
    시간 형식(HH:MM:SS 등)을 '시, 분, 초' 형식의 한글로 통일합니다.

    Ref:
        https://github.com/hash2430/pitchtron/blob/hard/text/datestime.py
    
    Args:
        text (str): 원본 텍스트.
        
    Returns:
        str: 시간이 한글 포맷으로 변환된 텍스트.
    """
    def _repl(m):
        h, m_val, s = m.groups()
        res = f"{int(h)}시 {int(m_val)}분"
        if s:
            res += f" {int(s)}초"
        return res
    return RE_TIME.sub(_repl, text)

def find_time_format(text: str) -> List[Tuple[int, int, str]]:
    """
    시간 형식(HH:MM:SS 등) 매치를 텍스트 무변경으로 위치와 함께 보고합니다.

    read_time_format이 단독 실행으로 치환하는 바로 그 매치들을 돌려주는 조회 전용
    짝꿍입니다. read(text) != text와 find(text) != [] 는 동치입니다.

    Args:
        text (str): 검사할 원본 텍스트.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    return _find_pattern_matches(RE_TIME, text)

def read_decimal_point(text: str, point_char: str = " 쩜 ", digit_map: dict = SINO_DIGITS) -> str:
    """
    소수점 아래의 숫자들을 한글 발음으로 개별 변환합니다.

    Ref:
        https://github.com/carpedm20/multi-speaker-tacotron-tensorflow/blob/master/text/korean.py#L297-L299
    
    Args:
        text (str): 원본 텍스트.
        point_char (str): 소수점을 읽을 방식 (기본값: " 쩜 ").
        digit_map (dict): 숫자별 한자어 매핑 사전.
        
    Returns:
        str: 소수점이 한글 발음으로 변환된 텍스트.
    """
    def _repl(m):
        integer = m.group(1)
        fraction = "".join(digit_map.get(d, d) for d in m.group(2))
        return f"{integer}{point_char}{fraction}"
    return RE_FLOAT.sub(_repl, text)

def read_interpunct_digits(text: str, digit_map: dict = SINO_DIGITS) -> str:
    """
    가운뎃점으로 묶인 숫자 표기(6·25, 3·1절)를 낱자 한자어 발음으로 변환합니다.

    자릿수 읽기(25 -> 이십오)가 아니라 낱자 읽기(2, 5 -> 이오)를 적용해
    "6·25[유기오]", "3·1절[사밀쩔]" 같은 관용 독법의 표기를 만듭니다.

    Args:
        text (str): 원본 텍스트.
        digit_map (dict): 숫자별 한자어 매핑 사전.

    Returns:
        str: 가운뎃점 숫자가 낱자 발음으로 변환된 텍스트.
    """
    return RE_INTERPUNCT_NUM.sub(
        lambda m: "".join(digit_map.get(c, c) for c in m.group(0) if c != '·'),
        text,
    )

def find_interpunct_digits(text: str) -> List[Tuple[int, int, str]]:
    """
    가운뎃점으로 묶인 숫자 표기(6·25, 3·1절) 매치를 텍스트 무변경으로 보고합니다.

    read_interpunct_digits가 단독 실행으로 치환하는 바로 그 매치들을 돌려주는 조회
    전용 짝꿍입니다. read(text) != text와 find(text) != [] 는 동치입니다.

    Args:
        text (str): 검사할 원본 텍스트.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    return _find_pattern_matches(RE_INTERPUNCT_NUM, text)

def convert_bound_numerals(text: str) -> str:
    """
    단위 명사(분류사)가 결합된 숫자를 고유어 수사로 치환합니다.

    Ref:
        https://github.com/Kyubyong/g2pK/blob/master/g2pk/numerals.py#L109-L117
    
    Args:
        text (str): 원본 텍스트.
        
    Returns:
        str: 단위 결합 숫자가 정규화된 텍스트.
    """
    return RE_BOUND_NUM.sub(lambda m: num_to_native(m.group(1)) + m.group(2), text)

def find_bound_numerals(text: str) -> List[Tuple[int, int, str]]:
    """
    단위 명사(분류사)가 결합된 숫자 수사 매치를 텍스트 무변경으로 보고합니다.

    convert_bound_numerals가 단독 실행으로 치환하는 바로 그 매치들을 돌려주는 조회
    전용 짝꿍입니다. convert(text) != text와 find(text) != [] 는 동치이며,
    dealers_choice 파이프라인 순서 문맥은 반영하지 않습니다.

    Args:
        text (str): 검사할 원본 텍스트.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    return _find_pattern_matches(RE_BOUND_NUM, text)

def convert_standalone_numerals(text: str) -> str:
    """
    단위가 없는 일반 숫자를 한자어 기수사로 치환합니다.

    Ref:
        https://github.com/Kyubyong/g2pK/blob/master/g2pk/numerals.py#L119-L123
    
    Args:
        text (str): 원본 텍스트.
        
    Returns:
        str: 숫자가 한자어 발음으로 변환된 텍스트.
    """
    return RE_SINO_NUM.sub(lambda m: num_to_sino(m.group(0)), text)

def fix_num_exceptions(text: str, exception_map: dict = None) -> str:
    """
    잘못된 수사 결합이나 특수 읽기 방식(유월, 시월 등)을 보정합니다.

    Ref:
        https://github.com/hash2430/pitchtron/blob/hard/text/ko_dictionary.py#L27-L28
        https://github.com/Kyubyong/g2pK/blob/master/g2pk/idioms.txt#L133
    
    Args:
        text (str): 원본 텍스트.
        exception_map (dict): 보정할 단어들의 매핑 사전.
        
    Returns:
        str: 수사 예외 사항이 보정된 텍스트.
    """
    exceptions = exception_map if exception_map is not None else {
        "육월": "유월", "십월": "시월", "한번째": "첫번째", "한 번째": "첫번째",
    }
    for old, new in exceptions.items():
        text = text.replace(old, new)
    return text
