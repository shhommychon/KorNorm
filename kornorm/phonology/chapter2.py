# [국립국어원 한국어 어문 규범 표준어규정 제2부 표준발음법 제2장 자음과 모음]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a388

from typing import List, Tuple
from kornorm.phonology.common import MorphToken

from kornorm.utils.jamo import (
    O_NIEUN, O_RIEUL, O_SIOT, O_SSANGSIOT, O_IEUNG,
    O_JIEUT, O_SSANGJIEUT, O_CHIEUT,

    N_EO, N_E, N_YEO, N_YE, N_I, N_UI,
)

# [제2항 Norm 2]
#
# 표준어의 자음은 다음 19개로 한다.
# ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅆ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ
# Standard Korean consonants consist of the following 19:
# ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅆ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a395


# [제3항 Norm 3]
#
# 표준어의 모음은 다음 21개로 한다.
# ㅏ ㅐ ㅑ ㅒ ㅓ ㅔ ㅕ ㅖ ㅗ ㅘ ㅙ ㅚ ㅛ ㅜ ㅝ ㅞ ㅟ ㅠ ㅡ ㅢ ㅣ
# Standard Korean vowels consist of the following 21:
# ㅏ ㅐ ㅑ ㅒ ㅓ ㅔ ㅕ ㅖ ㅗ ㅘ ㅙ ㅚ ㅛ ㅜ ㅝ ㅞ ㅟ ㅠ ㅡ ㅢ ㅣ
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a396


# [제4항 Norm 4]
#
# ‘ㅏ ㅐ ㅓ ㅔ ㅗ ㅚ ㅜ ㅟ ㅡ ㅣ’는 단모음(單母音)으로 발음한다.
# ‘ㅏ ㅐ ㅓ ㅔ ㅗ ㅚ ㅜ ㅟ ㅡ ㅣ’ are pronounced as monophthongs.
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a397


# [제4항 붙임 Addendum of Norm 4]
#
# ‘ㅚ, ㅟ’는 이중 모음으로 발음할 수 있다.
# ‘ㅚ, ㅟ’ can be pronounced as diphthongs.
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a397


# [제5항 Norm 5]
#
# ‘ㅑ ㅒ ㅕ ㅖ ㅘ ㅙ ㅛ ㅝ ㅞ ㅠ ㅢ’는 이중 모음으로 발음한다.
# ‘ㅑ ㅒ ㅕ ㅖ ㅘ ㅙ ㅛ ㅝ ㅞ ㅠ ㅢ’ are pronounced as diphthongs.
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a398


# [제5항 다만 1. Proviso 1 of Norm 5]
#
# 용언의 활용형에 나타나는 ‘져, 쪄, 쳐’는 [저, 쩌, 처]로 발음한다.
# ‘져, 쪄, 쳐’ appearing in inflected forms of predicates are pronounced as [저, 쩌, 처].
#
#     가지어 -> 가져[가저]
#     찌어 -> 쪄[쩌]
#     다치어 -> 다쳐[다처]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a398
def norm5_p1(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제5항 다만 1. 용언의 활용형 "져, 쪄, 쳐"를 [저, 쩌, 처]로 변환합니다.

    본 엔진은 일반 규칙으로 품사 제한 없이 일괄 적용합니다.

    Ref:
        g2pk.special.jyeo()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L15-L21
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L203-L209

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: "ㅈ/ㅉ/ㅊ + ㅕ" 조합이 "ㅈ/ㅉ/ㅊ + ㅓ"로 치환된 토큰 리스트.
    """
    for token in tokens:
        if token.pos.startswith('S'): continue # 공백(SP), 영문(SL), 숫자(SN), 기호(SY) 등 자모 치환에서 제외

        jamo = token.jamo_str
        jamo = jamo.replace(O_JIEUT + N_YEO, O_JIEUT + N_EO)            # ㅈ+ㅕ -> ㅈ+ㅓ
        jamo = jamo.replace(O_SSANGJIEUT + N_YEO, O_SSANGJIEUT + N_EO)  # ㅉ+ㅕ -> ㅉ+ㅓ
        jamo = jamo.replace(O_CHIEUT + N_YEO, O_CHIEUT + N_EO)          # ㅊ+ㅕ -> ㅊ+ㅓ
        token.jamo_str = jamo
    return tokens


# [제5항 다만 2. Proviso 2 of Norm 5]
#
# ‘예, 례’ 이외의 ‘ㅖ’는 [ㅔ]로도 발음한다.
# ‘ㅖ’ in syllables other than ‘예’ and ‘례’ is also pronounced as [ㅔ].
#
#     계집[계:집/게:집]
#     계시다[계:시다/게:시다]
#     시계[시계/시게](時計)
#     연계[연계/연게](連繫)
#     몌별[몌별/메별](袂別)
#     개폐[개폐/개페](開閉)
#     혜택[혜:택/헤:택](惠澤)
#     지혜[지혜/지헤](智慧)
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a398
def norm5_p2(
    tokens: List[MorphToken],
    exceptions: Tuple[str, ...] = (O_IEUNG, O_RIEUL, O_NIEUN, O_SIOT, O_SSANGSIOT),
) -> List[MorphToken]:
    """
    제5항 다만 2. "예, 례" 이외의 'ㅖ'를 [ㅔ]로 변환합니다.

    본 엔진은 g2pK의 구현 통찰("실제로 언중은 예, 녜, 셰, 쎼 이외의 'ㅖ'는 [ㅔ]로 발음한다")을 계승하여,
    국립국어원이 명시한 '예', '례'와 함께 언중의 발음을 반영한 '녜', '셰', '쎼' (ㅇ, ㄹ, ㄴ, ㅅ, ㅆ)를
    기본적으로 변환 예외로 처리합니다.

    단, 본 조항은 허용 조항이므로 사용자의 목적에 따라 예외를 수정할 수 있습니다.

    Ref:
        g2pk.special.ye()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L24-L33
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L211-L218

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.
        exceptions (Tuple[str, ...]): 'ㅔ'로 변환하지 않고 'ㅖ' 발음을 유지할 초성 자음(O_*)들의 튜플.
                                      기본값은 (ㅇ, ㄹ, ㄴ, ㅅ, ㅆ) 입니다.

    Returns:
        List[MorphToken]: 조건에 맞는 'ㅖ'가 'ㅔ'로 치환된 토큰 리스트.
    """
    for token in tokens:
        if token.pos.startswith('S'): continue # 공백(SP), 영문(SL), 숫자(SN), 기호(SY) 등 자모 치환에서 제외

        jamo = token.jamo_str
        new_jamo = ''
        for i in range(0, len(jamo), 3):
            cho, joong, jong = jamo[i:i+3]
            # 초성이 예외 사항('ㅇ', 'ㄹ' 등)에 없는데 중성이 'ㅖ'라면 'ㅔ'로 변경
            if cho not in exceptions and joong == N_YE:
                joong = N_E
            new_jamo += cho + joong + jong
        token.jamo_str = new_jamo
    return tokens


# [제5항 다만 3. Proviso 3 of Norm 5]
#
# 자음을 첫소리로 가지고 있는 음절의 ‘ㅢ’는 [ㅣ]로 발음한다.
# ‘ㅢ’ in syllables that have a consonant as the initial sound is pronounced as [ㅣ].
#
#     늴리리
#     닁큼
#     무늬
#     띄어쓰기
#     씌어
#     틔어
#     희어
#     희떱다
#     희망
#     유희
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a398
def norm5_p3(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제5항 다만 3. 자음을 첫소리로 가지는 음절의 'ㅢ'를 [ㅣ]로 변환합니다.

    Ref:
        g2pk.special.consonant_ui()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L36-L41
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L220-L226

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 초성 자음과 결합한 'ㅢ'가 'ㅣ'로 치환된 토큰 리스트.
    """
    for token in tokens:
        if token.pos.startswith('S'): continue # 공백(SP), 영문(SL), 숫자(SN), 기호(SY) 등 자모 치환에서 제외

        # 본 조항은 표기 기준이므로, 사전 발음이 선적용된 토큰의 자음+ㅢ는 연음 유래의
        # 원칙형(협의[혀븨])으로 보고 재변형하지 않는다.
        if getattr(token, "stdict_applied", False):
            continue

        jamo = token.jamo_str
        new_jamo = ''
        for i in range(0, len(jamo), 3):
            cho, joong, jong = jamo[i:i+3]
            # 초성이 'ㅇ'(모음으로 시작)이 아닌 자음인데 중성이 'ㅢ'라면 'ㅣ'로 변경
            if cho != O_IEUNG and joong == N_UI:
                joong = N_I
            new_jamo += cho + joong + jong
        token.jamo_str = new_jamo
    return tokens


# [제5항 다만 4. Proviso 4 of Norm 5]
#
# 단어의 첫음절 이외의 ‘ㅢ’는 [ㅣ]로, 조사 ‘의’는 [ㅔ]로 발음함도 허용한다.
# It is also permitted to pronounce ‘ㅢ’ in syllables other than the first syllable
# of a word as [ㅣ], and the postpositional particle ‘의’ as [ㅔ].
#
#     주의[주의/주이]
#     협의[혀븨/혀비]
#     우리의[우리의/우리에]
#     강의의[강:의의/강:이에]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a398
def norm5_p4_1(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제5항 다만 4-1. 단어의 첫음절 이외의 '의'를 [이]로 변환합니다.

    단어의 첫음절 여부를 판단하기 위해 토큰의 인덱스 및 공백 정보를 활용합니다.

    "실제로 언중은 높은 확률로 단어의 첫음절 이외의 '의'를 [ㅣ]로 발음한다"는 g2pK 원작자 박규병 님 및
    zeroth 기여자 Lucas Jo 님의 코드에서 확립된 언어학적 통찰을 계승합니다.

    본 엔진은 이 선행 연구들의 철학을 바탕으로 해당 허용 조항을 기본 변환 동작으로 지원합니다.

    Ref:
        g2pk.special.vowel_ui()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L55-L63
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L228-L235

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 메타데이터가 주입된 토큰 리스트.

    Returns:
        List[MorphToken]: 단어의 비첫음절 '의'가 '이'로 치환된 토큰 리스트.
    """
    for token_idx, token in enumerate(tokens):
        if token.pos.startswith('S'): continue # 공백(SP), 영문(SL), 숫자(SN), 기호(SY) 등 자모 치환에서 제외
        if token.pos.startswith('J'): continue # 조사 또한 5.4.2항에서 처리해야 하므로 제외

        # 단어(어절)의 첫 번째 형태소이면서, 형태소 내의 첫 번째 글자이면 첫음절임.
        # 이를 정확히 하려면 앞 토큰이 공백(SP)인지 등을 확인해야 함.

        jamo = token.jamo_str
        new_jamo = ''
        for i in range(0, len(jamo), 3):
            cho, joong, jong = jamo[i:i+3]

            # 첫음절 판단 로직 (g2pK의 \S 정규식과 동일한 효과)
            # 현재 글자가 형태소의 첫 글자(i==0)이면서,
            # 전체 텍스트의 맨 처음(token_idx==0)이거나 바로 앞 토큰이 공백(SP)이면 첫음절임.
            is_first_syllable = (i == 0) and (token_idx == 0 or tokens[token_idx - 1].pos == "SP")

            if not is_first_syllable and cho == O_IEUNG and joong == N_UI:
                joong = N_I

            new_jamo += cho + joong + jong
        token.jamo_str = new_jamo
    return tokens

def norm5_p4_2(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제5항 다만 4-2. 조사 '의'를 [에]로 변환합니다.

    "실제로 언중은 높은 확률로 조사 '의'를 [ㅔ]로 발음한다"는 g2pK 원작자 박규병 님 및 zeroth 기여자
    Lucas Jo 님의 코드에서 확립된 언어학적 통찰을 계승합니다.

    본 엔진은 형태소 분석기의 품사 태그 J(조사)를 식별하여 이를 자동 치환하는 방식으로 해당 허용 조항을
    일관성 있게 구현하였습니다.

    Ref:
        g2pk.special.josa_ui()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L44-L52
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L237-L244

    Args:
        tokens (List[MorphToken]): POS 태깅이 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 조사 '의'가 '에'로 치환된 토큰 리스트.
    """
    for token in tokens:
        if token.pos.startswith('S'): continue # 공백(SP), 영문(SL), 숫자(SN), 기호(SY) 등 자모 치환에서 제외

        # 품사가 J(조사)로 시작하고 글자가 '의'인 경우
        if token.pos.startswith('J'):
            jamo = token.jamo_str
            # '의' -> '에'
            token.jamo_str = jamo.replace(O_IEUNG + N_UI, O_IEUNG + N_E)
    return tokens
