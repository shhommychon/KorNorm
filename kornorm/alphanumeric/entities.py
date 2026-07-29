# [KorNorm 기호 및 단위 정규화 모듈]
#
# 통화 기호, 물리 단위 및 로마자 기반 약어를 개별 함수로 정규화합니다.


import re
from kornorm.alphanumeric.constants import (
    CURRENCY_MAP, UNITS_MAP, SYMBOL_MAP, ENG_DIGITS, SPECIAL_SYMBOL_MAP, GREEK_MAP
)
from kornorm.alphanumeric.base import alphabet_to_hangul

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
    for sym, kor in currency_map.items():
        escaped_sym = re.escape(sym)
        text = re.sub(f"({escaped_sym})(\\d+[\\.]?\\d*)", f"\\2{kor}", text)
        text = re.sub(f"(\\d+[\\.]?\\d*)({escaped_sym})", f"\\1{kor}", text)
    return text

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
    for key, val in symbol_map.items():
        for variant in {key, key.upper(), key.lower()}:
            pattern = re.compile(
                f"(?<![A-Za-z0-9.]){re.escape(variant)}(?![A-Za-z0-9])")
            text = pattern.sub(val, text)
    return text

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
    sorted_units = sorted(units_map.keys(), key=len, reverse=True)
    for unit in sorted_units:
        kor = units_map[unit]
        pattern = re.compile(f"(\\d+)\\s*{re.escape(unit)}(?![a-zA-Z])", re.IGNORECASE)
        text = pattern.sub(f"\\1{kor}", text)
    return text

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
