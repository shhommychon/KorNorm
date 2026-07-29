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
    sino_thousands: list = SINO_THOUSANDS
) -> str:
    """
    숫자 문자열을 한자어 기수사(일, 이, 삼...)로 변환합니다.

    Ref:
        https://github.com/SMART-TTS/SMART-G2P/blob/master/utils.py#L133-L160
    
    Args:
        num_str (str): 변환할 숫자 문자열.
        sino_digits (dict): 숫자별 한자어 매핑 사전.
        sino_tens (list): 십 단위 한자어 리스트.
        sino_thousands (list): 천 단위 이상의 큰 숫자 한자어 리스트.
        
    Returns:
        str: 한자어 수사로 변환된 문자열.
    """
    # clean_num = num_str.lstrip('0')
    # if not clean_num:
    #     return sino_digits.get('0', '영')
        
    length = len(num_str) # clean_num)
    res = []
    
    for i, char in enumerate(num_str): # clean_num):
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
