# [KorNorm 기호 및 단위 정규화 모듈]
#
# 통화 기호, 물리 단위 및 로마자 기반 약어를 개별 함수로 정규화합니다.


import re
from typing import Iterator, List, Tuple

from kornorm.alphanumeric.constants import (
    CURRENCY_MAP, UNITS_MAP, SYMBOL_MAP, ENG_DIGITS, SPECIAL_SYMBOL_MAP, GREEK_MAP
)
from kornorm.alphanumeric.base import alphabet_to_hangul


def _claim_matches(
    patterns: Iterator[Tuple[re.Pattern, str]], text: str
) -> List[Tuple[int, int, str]]:
    """
    패턴들을 순서대로 스캔하며 먼저 선점된 스팬과 겹치지 않는 매치만 수집합니다.

    컨버터의 순차 sub(앞선 패턴이 먼저 치환해 뒤 패턴의 재료를 소거)와 등가인
    탐지 결과를 만들기 위한 공용 루프입니다.

    Args:
        patterns (Iterator[Tuple[re.Pattern, str]]): (패턴, 치환값) 쌍의 순회.
        text (str): 검사할 원본 텍스트.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    claimed = []
    for pattern, _ in patterns:
        for match in pattern.finditer(text):
            if any(match.start() < end and start < match.end() for start, end, _ in claimed):
                continue
            claimed.append((match.start(), match.end(), match.group(0)))
    return sorted(claimed)

def _iter_currency_patterns(currency_map: dict) -> Iterator[Tuple[re.Pattern, str]]:
    """
    통화 사전을 순회하며 기호별 전위·후위 (패턴, 치환 템플릿) 쌍을 순서대로 냅니다.
    read_currencies와 find_currencies가 같은 패턴을 쓰도록 하는 단일 소스입니다.
    """
    for sym, kor in currency_map.items():
        escaped_sym = re.escape(sym)
        yield re.compile(f"({escaped_sym})(\\d+[\\.]?\\d*)"), f"\\2{kor}"
        yield re.compile(f"(\\d+[\\.]?\\d*)({escaped_sym})"), f"\\1{kor}"

def read_currencies(text: str, currency_map: dict = CURRENCY_MAP) -> str:
    """
    통화 특수기호($, ₩ 등)를 감지하여 한글 발음으로 변환합니다.

    Ref:
        https://github.com/SMART-TTS/SMART-G2P/blob/master/utils.py#L30C1-L31
    
    Args:
        text (str): 원본 텍스트.
        currency_map (dict): 통화 기호별 한글 발음 매핑 사전.
        
    Returns:
        str: 통화 기호가 한글로 치환된 텍스트.
    """
    for pattern, repl in _iter_currency_patterns(currency_map):
        text = pattern.sub(repl, text)
    return text

def find_currencies(
    text: str, currency_map: dict = CURRENCY_MAP
) -> List[Tuple[int, int, str]]:
    """
    통화 기호가 결합된 금액 매치를 텍스트 무변경으로 위치와 함께 보고합니다.

    read_currencies가 단독 실행으로 치환하는 바로 그 매치들을 돌려주는 조회 전용
    짝꿍입니다. read(text) != text와 find(text) != [] 는 동치입니다.

    Args:
        text (str): 검사할 원본 텍스트.
        currency_map (dict): 통화 기호별 한글 발음 매핑 사전.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    return _claim_matches(_iter_currency_patterns(currency_map), text)

def _iter_unit_exception_patterns(symbol_map: dict) -> Iterator[Tuple[re.Pattern, str]]:
    """
    영숫자 결합 예외 사전을 순회하며 대소문자 변형별 (경계 가드 패턴, 독법) 쌍을 냅니다.
    read_unit_exceptions와 find_unit_exceptions가 같은 패턴을 쓰도록 하는 단일 소스입니다.
    """
    for key, val in symbol_map.items():
        for variant in {key, key.upper(), key.lower()}:
            yield re.compile(
                f"(?<![A-Za-z0-9.]){re.escape(variant)}(?![A-Za-z0-9])"), val

def read_unit_exceptions(text: str, symbol_map: dict = SYMBOL_MAP) -> str:
    """
    단위 정규화 전, 5G나 mp3와 같이 관용적으로 읽히는 영숫자 결합 예외를 처리합니다.

    더 큰 영숫자 토큰의 일부를 오인 치환하지 않도록 앞뒤 경계를 검사합니다
    (예: "3.5GHz"의 "5G", "15GB"의 "5G"는 치환하지 않고 단위 정규화에 넘긴다).

    Args:
        text (str): 원본 텍스트.
        symbol_map (dict): 예외 단어별 한글 발음 매핑 사전.

    Returns:
        str: 예외 단어들이 한글로 치환된 텍스트.
    """
    for pattern, val in _iter_unit_exception_patterns(symbol_map):
        text = pattern.sub(val, text)
    return text

def find_unit_exceptions(
    text: str, symbol_map: dict = SYMBOL_MAP
) -> List[Tuple[int, int, str]]:
    """
    관용적으로 읽히는 영숫자 결합 예외(5G, mp3 등) 매치를 텍스트 무변경으로 보고합니다.

    read_unit_exceptions가 단독 실행으로 치환하는 바로 그 매치들을 돌려주는 조회
    전용 짝꿍입니다. read(text) != text와 find(text) != [] 는 동치이며, 더 큰
    영숫자 토큰의 일부("3.5GHz"의 "5G" 등)는 컨버터와 똑같이 매치되지 않습니다.

    Args:
        text (str): 검사할 원본 텍스트.
        symbol_map (dict): 예외 단어별 한글 발음 매핑 사전.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    return _claim_matches(_iter_unit_exception_patterns(symbol_map), text)

def _iter_unit_patterns(units_map: dict) -> Iterator[Tuple[re.Pattern, str]]:
    """
    단위 사전을 긴 키 우선으로 순회하며 (숫자+단위 패턴, 독법) 쌍을 냅니다.
    read_units와 find_units가 같은 패턴을 쓰도록 하는 단일 소스입니다.
    """
    for unit in sorted(units_map.keys(), key=len, reverse=True):
        yield re.compile(
            f"(\\d+)\\s*{re.escape(unit)}(?![a-zA-Z])", re.IGNORECASE), units_map[unit]

def read_units(text: str, units_map: dict = UNITS_MAP) -> str:
    """
    물리 단위(kg, km, hz 등)를 감지하여 한글 발음으로 변환합니다.

    Ref:
        https://github.com/jwj7140/Bert-VITS2-Korean/blob/main/text/korean.py#L238-L256
    
    Args:
        text (str): 원본 텍스트.
        units_map (dict): 단위별 한글 발음 매핑 사전.
        
    Returns:
        str: 영문 단위가 한글로 변환된 텍스트.
    """
    for pattern, kor in _iter_unit_patterns(units_map):
        text = pattern.sub(f"\\1{kor}", text)
    return text

def find_units(text: str, units_map: dict = UNITS_MAP) -> List[Tuple[int, int, str]]:
    """
    숫자와 결합된 물리 단위(kg, km, hz 등) 매치를 텍스트 무변경으로 보고합니다.

    read_units가 단독 실행으로 치환하는 바로 그 매치들을 돌려주는 조회 전용
    짝꿍입니다. read(text) != text와 find(text) != [] 는 동치이며, 긴 단위가
    선점한 스팬("10m/s"의 "m/s")과 겹치는 짧은 단위 후보("m")는 컨버터의
    긴 키 우선 치환과 똑같이 제외됩니다. dealers_choice 순서 문맥은 반영하지
    않으므로 "3.5GHz"에서는 컨버터와 마찬가지로 "5GHz"가 매치됩니다.

    Args:
        text (str): 검사할 원본 텍스트.
        units_map (dict): 단위별 한글 발음 매핑 사전.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    return _claim_matches(_iter_unit_patterns(units_map), text)

def read_alphanum_combos(text: str, digit_map: dict = ENG_DIGITS) -> str:
    """
    영문과 숫자가 혼용된 토큰(예: H2O)의 각 문자를 한글 발음으로 변환합니다.
    숫자의 경우 영어식 발음(원, 투, 쓰리)을 기본값으로 사용합니다.

    Ref:
        https://github.com/hash2430/pitchtron/blob/hard/text/letters_and_numbers.py
        https://github.com/SMART-TTS/SMART-G2P/blob/master/utils.py#L115-L131
    
    Args:
        text (str): 원본 텍스트.
        digit_map (dict): 숫자별 한자어 매핑 사전.
        
    Returns:
        str: 영숫자 혼합 토큰이 낱자 발음으로 변환된 텍스트.
    """
    def _repl(m):
        raw = m.group(0)
        res = []
        for c in raw:
            if c.isdigit():
                res.append(digit_map.get(c, c))
            else:
                res.append(alphabet_to_hangul(c))
        return "".join(res)

    # 숫자 선행 분기는 한 자리 숫자로 제한한다 (3M -> 쓰리엠). 여러 자리 숫자가 앞서는
    # 토큰(220V 등)은 낱자 조합이 아니라 수사+낱자(이백이십븨)로 읽히도록 남겨 둔다.
    return re.sub(r"([a-zA-Z]\d+|(?<!\d)\d[a-zA-Z])[a-zA-Z\d]*", _repl, text)

def read_abbreviations(text: str) -> str:
    """
    대문자로만 구성된 약어(예: NASA, H&M)를 한글 낱자 발음으로 변환합니다.

    Ref:
        https://github.com/ORI-Muchim/MB-iSTFT-VITS-Korean/blob/main/text/korean.py#L105-L108
    
    Args:
        text (str): 원본 텍스트.
        
    Returns:
        str: 대문자 약어가 한글 발음으로 변환된 텍스트.
    """
    def _repl(m):
        raw = m.group(0)
        return "".join(alphabet_to_hangul(c) if c.isalpha() else c for c in raw)
        
    return re.sub(r"\b[A-Z&]{2,}\b", _repl, text)

def read_special_symbols(
    text: str, 
    symbol_map: dict = SPECIAL_SYMBOL_MAP, 
    greek_map: dict = GREEK_MAP
) -> str:
    """
    일상적인 특수 기호(+, -, @ 등) 및 그리스 문자를 한글 발음으로 변환합니다.

    Ref:
        https://github.com/SMART-TTS/SMART-G2P/blob/master/utils.py#L27-L28
        
    Args:
        text (str): 원본 텍스트.
        symbol_map (dict): 범용 특수 기호 매핑 사전.
        greek_map (dict): 그리스 문자 매핑 사전.
        
    Returns:
        str: 기호 및 문자가 한글 발음으로 치환된 텍스트.
    """
    combined_map = {**symbol_map, **greek_map}
    for sym, kor in combined_map.items():
        text = text.replace(sym, kor)
    return text

def find_special_symbols(
    text: str,
    symbol_map: dict = SPECIAL_SYMBOL_MAP,
    greek_map: dict = GREEK_MAP
) -> List[Tuple[int, int, str]]:
    """
    특수 기호(+, -, @ 등)와 그리스 문자 매치를 텍스트 무변경으로 보고합니다.

    read_special_symbols가 단독 실행으로 치환하는 바로 그 매치들을 돌려주는 조회
    전용 짝꿍입니다. read(text) != text와 find(text) != [] 는 동치입니다.

    Args:
        text (str): 검사할 원본 텍스트.
        symbol_map (dict): 범용 특수 기호 매핑 사전.
        greek_map (dict): 그리스 문자 매핑 사전.

    Returns:
        List[Tuple[int, int, str]]: 매치별 (시작, 끝, 매치 문자열) 목록 (시작 위치순).
    """
    combined_map = {**symbol_map, **greek_map}
    results = []
    for sym in combined_map:
        start = text.find(sym)
        while start != -1:
            results.append((start, start + len(sym), sym))
            start = text.find(sym, start + len(sym))
    return sorted(results)
