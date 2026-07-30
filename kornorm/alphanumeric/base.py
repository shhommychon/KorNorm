# [KorNorm 기초 변환 엔진 모듈]
#
# 수사와 알파벳의 가장 원초적인 치환 로직을 담당합니다.


from kornorm.alphanumeric.constants import (
    SINO_DIGITS, SINO_TENS, SINO_THOUSANDS, NATIVE_DIGITS, NATIVE_TENS, LATIN_MAP
)


def num_to_sino(
    num_str: str,
    sino_digits: dict = SINO_DIGITS,
    sino_tens: list = SINO_TENS,
    sino_thousands: list = SINO_THOUSANDS,
    zero_char: str = '공'
) -> str:
    """
    숫자 문자열을 한자어 기수사(일, 이, 삼...)로 변환합니다.
    선행 0이 붙은 다자리 수는 자릿수 독법이 무의미하므로 낱자로 읽고("007" -> 공공칠),
    0으로만 이루어진 한 자리 수는 '영'으로 읽습니다.

    Ref:
        https://github.com/SMART-TTS/SMART-G2P/blob/master/utils.py#L133-L160

    Args:
        num_str (str): 변환할 숫자 문자열.
        sino_digits (dict): 숫자별 한자어 매핑 사전.
        sino_tens (list): 십 단위 한자어 리스트.
        sino_thousands (list): 천 단위 이상의 큰 숫자 한자어 리스트.
        zero_char (str): 낱자 독법에서 0을 읽을 글자 (기본값 '공').

    Returns:
        str: 한자어 수사로 변환된 문자열.
    """
    # 선행 0이 붙은 다자리 수(코드·번호류)는 낱자 독법으로 읽는다
    if len(num_str) > 1 and num_str[0] == '0':
        return "".join(
            zero_char if char == '0' else sino_digits.get(char, char)
            for char in num_str
        )

    length = len(num_str)
    res = []

    for i, char in enumerate(num_str):
        if char == '0':
            continue
            
        pos = length - 1 - i
        chunk = pos // 4
        tens = pos % 4
        
        name = sino_digits.get(char, char)
        if char == '1' and tens > 0:
            name = ''
            
        res.append(name + sino_tens[tens])
        if tens == 0 and chunk > 0:
            res.append(sino_thousands[chunk])

    # 단독 '0'은 자릿수 이름이 하나도 쌓이지 않으므로 영으로 읽는다
    if num_str and not res:
        return sino_digits.get('0', '영')

    return "".join(res)

def num_to_native(
    num_str: str, 
    sino_digits: dict = SINO_DIGITS, 
    sino_tens: list = SINO_TENS, 
    sino_thousands: list = SINO_THOUSANDS,
    native_digits: dict = NATIVE_DIGITS, 
    native_tens: dict = NATIVE_TENS
) -> str:
    """
    숫자 문자열을 고유어 서수사(한, 두, 세...)로 변환합니다. 100 이상일 경우 한자어와 혼합합니다.

    Ref:
        https://github.com/SMART-TTS/SMART-G2P/blob/master/utils.py#L77-L86
    
    Args:
        num_str (str): 변환할 숫자 문자열.
        sino_digits (dict): 숫자별 한자어 매핑 사전.
        sino_tens (list): 십 단위 한자어 리스트.
        sino_thousands (list): 천 단위 이상의 큰 숫자 한자어 리스트.
        native_digits (dict): 일 단위 고유어 매핑 사전.
        native_tens (dict): 십 단위 고유어 매핑 사전.
        
    Returns:
        str: 고유어(또는 혼합형) 수사로 변환된 문자열.
    """
    val = int(num_str)
    if val == 0:
        return sino_digits.get('0', '영')

    res = ""
    if val >= 100:
        sino_part_str = num_str[:-2]
        if sino_part_str:
            sino_val = int(sino_part_str) * 100
            res += num_to_sino(str(sino_val), sino_digits, sino_tens, sino_thousands)
            
    remainder = val % 100
    ten, unit = divmod(remainder, 10)
    
    if ten > 0:
        res += native_tens.get(str(ten), "")
    if unit > 0:
        res += native_digits.get(str(unit), "")
    
    # "스무" 예외 처리
    #   ref: https://github.com/Kyubyong/g2pK/blob/master/g2pk/numerals.py#L28-L29
    if res.endswith("스물"):
        return res[:-1] + "무"
    return res

def alphabet_to_hangul(char: str, latin_map: dict = LATIN_MAP) -> str:
    """
    단일 영문 알파벳을 한글 발음으로 변환합니다.

    Ref:
        https://github.com/ORI-Muchim/MB-iSTFT-VITS-Korean/blob/main/text/korean.py#L105-L108
    
    Args:
        char (str): 변환할 영문 알파벳 문자.
        latin_map (dict): 알파벳별 한글 발음 매핑 사전.
        
    Returns:
        str: 한글 발음으로 변환된 문자열.
    """
    return latin_map.get(char.lower(), char)
