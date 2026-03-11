# [국립국어원 한국어 어문 규범 표준어규정 제2부 표준발음법 제4장 받침의 발음]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a390

from typing import List
from kornorm.phonology.common import MorphToken
from kornorm.phonology.common import DERIV_SUFFIX_TAGS, SUBSTANTIVE_TAGS, _is_functional

from kornorm.utils.jamo import (
    O_GIYEOK, O_SSANGGIYEOK, O_NIEUN, O_DIGEUT, O_SSANGDIGEUT,
    O_RIEUL, O_MIEUM, O_BIEUP, O_SIOT, O_SSANGSIOT,
    O_IEUNG, O_JIEUT, O_SSANGJIEUT, O_CHIEUT, O_KIEUK,
    O_TIEUT, O_PIEUP, O_HIEUT,

    N_A, N_AE, N_EO, N_E, N_O, N_WA, N_WAE, N_OE,
    N_U, N_WEO, N_WE, N_WI, N_EU, N_UI,

    C_NONE,
    C_GIYEOK, C_SSANGGIYEOK, C_GIYEOK_SIOT, C_NIEUN, C_NIEUN_JIEUT,
    C_NIEUN_HIEUT, C_DIGEUT, C_RIEUL, C_RIEUL_GIYEOK, C_RIEUL_MIEUM,
    C_RIEUL_BIEUP, C_RIEUL_SIOT, C_RIEUL_TIEUT, C_RIEUL_PIEUP, C_RIEUL_HIEUT,
    C_MIEUM, C_BIEUP, C_BIEUP_SIOT, C_SIOT, C_SSANGSIOT,
    C_IEUNG, C_JIEUT, C_CHIEUT, C_KIEUK, C_TIEUT,
    C_PIEUP, C_HIEUT,
)

# [제8항 Norm 8]
#
# 받침소리로는 ‘ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅇ’의 7개 자음만 발음한다.
# Only the seven consonants ‘ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅇ’ are pronounced as final sounds (batchim).
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a401


# [제9항 Norm 9]
#
# 받침 ‘ㄲ, ㅋ’, ‘ㅅ, ㅆ, ㅈ, ㅊ, ㅌ’, ‘ㅍ’은 어말 또는 자음 앞에서 각각 대표음 [ㄱ, ㄷ, ㅂ]으로 발음한다.
# Final consonants ‘ㄲ, ㅋ’, ‘ㅅ, ㅆ, ㅈ, ㅊ, ㅌ’, and ‘ㅍ’ are pronounced as their representative sounds
# [ㄱ, ㄷ, ㅂ], respectively, at the end of a word or before a consonant.
#
#     닦다[닥따]
#     키윽[키윽]
#     키윽과[키윽꽈]
#     옷[얻]
#     웃다[욷:따]
#     있다[읻따]
#     젖[젇]
#     빚다[빋따]
#     꽃[꼳]
#     쫓다[쫃따]
#     솥[솓]
#     뱉다[밷:따]
#     앞[압]
#     덮다[덥따]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a402
def norm9(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제10항 Norm 10]
#
# 겹받침 ‘ㄳ’, ‘ㄵ’, ‘ㄼ, ㄽ, ㄾ’, ‘ㅄ’은 어말 또는 자음 앞에서 각각 [ㄱ, ㄴ, ㄹ, ㅂ]으로 발음한다.
# Double final consonants ‘ㄳ’, ‘ㄵ’, ‘ㄼ, ㄽ, ㄾ’, and ‘ㅄ’ are pronounced as [ㄱ, ㄴ, ㄹ, ㅂ],
# respectively, at the end of a word or before a consonant.
#
#     넉[넉]
#     넋과[넉꽈]
#     앉다[안따]
#     여덟[여덜]
#     넓다[널따]
#     외곬[외골]
#     핥다[할따]
#     값[갑]
#     없다[업:따]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a403
def norm10(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제10항 다만 Proviso of Norm 10]
#
# ‘밟-’은 자음 앞에서 [밥]으로 발음하고, ‘넓-’은 다음과 같은 경우에 [넙]으로 발음한다.
# ‘밟-’ is pronounced as [밥] before a consonant, and ‘넓-’ is pronounced as [넙] in the following cases.
#
# (1) ‘밟-’의 경우:
#     밟다[밥:따]
#     밟소[밥:쏘]
#     밟지[밥:찌]
#     밟는[밥:는 -> 밤:는]
#     밟게[밥:께]
#     밟고[밥:꼬]
#
# (2) ‘넓-’의 경우:
#     넓-죽하다[넙쭈카다]
#     넓-둥글다[넙뚱글다]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a403
def norm10_p(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제10항 다만. "밟-"은 자음 앞에서 [밥]으로, "넓-"은 예외적인 경우 [넙]으로 발음합니다.

    g2pK의 로직 `(너)ᆲ([ᄌᄍ]ᅮ|[ᄃᄄ]ᅮ)`을 반영하여, "넓-" 뒤에 ㅈ/ㅉ/ㄷ/ㄸ + ㅜ 가
    결합할 때 ㄼ을 ㅂ으로 치환합니다.

    Ref:
        g2pk.special.balb()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L129-L138
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L299-L309

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: "밟-", "넓-"의 ㄼ 받침이 예외 조건에서 ㅂ으로 치환된 리스트.
    """
    for i, token in enumerate(tokens):
        if token.pos.startswith('S'):
            continue

        curr_jamo = token.jamo_str

        # 1. "밟-" 처리
        if token.pos.startswith('V') and token.surface == '밟':
            # 다음 토큰들 중 공백이 아닌 첫 형태소 탐색
            next_cho = ''
            for next_token in tokens[i+1:]:
                if not next_token.pos.startswith('S'):
                    next_cho = next_token.jamo_str[0]
                    break
            
            if not next_cho or next_cho not in (O_IEUNG, O_HIEUT):
                token.jamo_str = curr_jamo[:-1] + C_BIEUP

        # 2. "넓-" 처리
        elif '넓' in token.surface:
            new_jamo = ''
            j = 0
            while j < len(curr_jamo):
                cho = curr_jamo[j]
                joong = curr_jamo[j+1] if j+1 < len(curr_jamo) else ''
                jong = curr_jamo[j+2] if j+2 < len(curr_jamo) else ''
                
                if cho == O_NIEUN and joong == N_EO and jong == C_RIEUL_BIEUP:
                    # 현재 위치가 단일 토큰 내부인지, 다음 토큰을 봐야 하는지 판단
                    if j + 3 < len(curr_jamo):
                        # 토큰 내부(Intra-token)에 다음 글자가 있음
                        next_cho = curr_jamo[j+3]
                        next_joong = curr_jamo[j+4] if j+4 < len(curr_jamo) else ''
                    else:
                        # 토큰 경계(Inter-token)에 있음: 다음 토큰 탐색
                        next_cho = ''
                        next_joong = ''
                        for next_token in tokens[i+1:]:
                            if not next_token.pos.startswith('S'):
                                next_cho = next_token.jamo_str[0]
                                next_joong = next_token.jamo_str[1] if len(next_token.jamo_str) >= 2 else ''
                                break

                    if next_cho in (O_JIEUT, O_SSANGJIEUT, O_DIGEUT, O_SSANGDIGEUT) and next_joong == N_U:
                        jong = C_BIEUP
                        
                new_jamo += cho + joong + jong
                j += 3
            token.jamo_str = new_jamo
    
    return tokens


# [제11항 Norm 11]
#
# 겹받침 ‘ㄺ, ㄻ, ㄿ’은 어말 또는 자음 앞에서 각각 [ㄱ, ㅁ, ㅂ]으로 발음한다.
# Double final consonants ‘ㄺ, ㄻ, ㄿ’ are pronounced as [ㄱ, ㅁ, ㅂ], respectively, at the end of a word
# or before a consonant.
#
#     닭[닥]
#     흙과[흑꽈]
#     맑다[막따]
#     늙지[늑찌]
#     삶[삼:]
#     젊다[점:따]
#     읊고[읍꼬]
#     읊다[읍따]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a404
def norm11(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제11항 다만 Proviso of Norm 11]
#
# 용언의 어간 말음 ‘ㄺ’은 ‘ㄱ’ 앞에서 [ㄹ]로 발음한다.
# The verb stem final sound ‘ㄺ’ is pronounced as [ㄹ] before ‘ㄱ’.
#
#     맑게[말께]
#     묽고[물꼬]
#     읽거나[일꺼나]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a404
def norm11_p(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제11항 다만. 용언의 어간 말음 'ㄺ'은 'ㄱ' 앞에서 [ㄹ]로 발음합니다.

    Ref:
        g2pk.special.rieulgiyeok()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L80-L87
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L321-L322

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 용언 'ㄺ'이 'ㄱ', 'ㄲ' 앞에서 ㄹ로 치환된 리스트.
    """
    for i in range(len(tokens) - 1):
        curr_token = tokens[i]
        next_token = tokens[i+1]

        if curr_token.pos.startswith('S') or next_token.pos.startswith('S'):
            continue

        curr_jamo = curr_token.jamo_str
        if curr_token.pos.startswith('V') and curr_jamo[-1] == C_RIEUL_GIYEOK:
            next_cho = next_token.jamo_str[0]
            if next_cho in (O_GIYEOK, O_SSANGGIYEOK):
                curr_token.jamo_str = curr_jamo[:-1] + C_RIEUL
                next_token.jamo_str = O_SSANGGIYEOK + next_token.jamo_str[1:]

    return tokens


# [제12항 Norm 12]
#
# 받침 ‘ㅎ’의 발음은 다음과 같다.
# The pronunciation of the final consonant ‘ㅎ’ is as follows.
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a405


# [제12항 1. Norm 12 Item 1]
#
# ‘ㅎ(ㄶ, ㅀ)’ 뒤에 ‘ㄱ, ㄷ, ㅈ’이 결합되는 경우에는, 뒤 음절 첫소리와 합쳐서 [ㅋ, ㅌ, ㅊ]으로 발음한다.
# When ‘ㄱ, ㄷ, ㅈ’ follow ‘ㅎ(ㄶ, ㅀ)’, they are combined with the initial sound of the following syllable
# and pronounced as [ㅋ, ㅌ, ㅊ].
#
#     놓고[노코]
#     좋던[조:턴]
#     쌓지[싸치]
#     많고[만:코]
#     않던[안턴]
#     닳지[달치]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a405
def norm12_1(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제12항 1. 해설 Commentary of Norm 12 Item 1]
#
# 1. ‘ㅎ(ㄶ, ㅀ)’ 뒤에 평음 ‘ㄱ, ㄷ, ㅈ’으로 시작하는 말이 결합하는 경우로 주로 용언 어간 뒤에 어미가
# 결합할 때 나타난다. 
# This refers to cases where words starting with the plain consonants ‘ㄱ, ㄷ, ㅈ’ follow ‘ㅎ(ㄶ, ㅀ)’, 
# which mainly occurs when an ending is combined with a predicate stem.
# 이때에는 ‘ㅎ’과 ‘ㄱ, ㄷ, ㅈ’이 합쳐져서 격음인 [ㅋ, ㅌ, ㅊ]으로 발음된다.
# In this case, ‘ㅎ’ is combined with ‘ㄱ, ㄷ, ㅈ’ and pronounced as the aspirated sounds [ㅋ, ㅌ, ㅊ].
#
# 용언 어간과 어미가 결합한 경우는 아니나 음운 환경이 같은 ‘싫증’에서는, ‘ㅎ’과 ‘ㅈ’이 [ㅊ]으로 줄지
# 않고 [실쯩]으로 발음된다.
# Although it is not a combination of a predicate stem and an ending, in the case of ‘싫증’, which has
# the same phonological environment, ‘ㅎ’ and ‘ㅈ’ do not reduce to [ㅊ] but are pronounced as [실쯩].
# 이는 ‘증(症)’이 붙는 말의 일반적인 발음 경향과 같다.
# This follows the general pronunciation tendency of words to which the suffix ‘-증(症)’ is attached.
# ‘염증[염쯩], 건조증[건조쯩]’에서 알 수 있듯이 ‘증(症)’이 단어의 둘째 음절 이하에 놓일 때에는 경음화가
# 잘 일어난다.
# As seen in ‘염증[염쯩]’ and ‘건조증[건조쯩]’, tensification (fortition) frequently occurs when
# ‘증(症)’ is placed in the second syllable or later in a word.
# ‘싫증’도 이러한 경향에 따라 [실쯩]으로 발음한다.
# Following this tendency, ‘싫증’ is also pronounced as [실쯩].
#
#     싫증[실쯩]
#     염증[염쯩]
#     건조증[건조쯩]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a405
def norm12_1_c(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제12항 1. 해설. "ㅎ(ㄶ, ㅀ)" 뒤에 한자어 "-증(症)"이 결합할 때 격음화(ㅊ)가 아닌 경음화(ㅉ)를 적용합니다.

    용언 어간과 어미가 결합하는 일반적인 격음화 환경과 달리, "싫증"의 경우 'ㅎ'과 'ㅈ'이 [ㅊ]으로
    축약되지 않고 [실쯩]으로 발음됩니다. 이를 반영하여 앞의 'ㅎ'을 탈락시키고 뒤의 'ㅈ'을 'ㅉ'으로 바꿉니다.

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: "-증(症)" 조건에서 'ㅎ' 탈락 및 경음화가 적용된 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'): 
            continue

        if '증' not in curr_token.surface:
            continue

        jamo = curr_token.jamo_str
        new_jamo = ''
        for j in range(0, len(jamo), 3):
            cho, joong, jong = jamo[j:j+3]
            
            if j >= 3:
                prev_jong = new_jamo[-1]
                # 현재 음절이 '증' (ㅈ + ㅡ + ㅇ)인지 확인
                if cho == O_JIEUT and joong == N_EU and jong == C_IEUNG:
                    if prev_jong in (C_HIEUT, C_NIEUN_HIEUT, C_RIEUL_HIEUT):
                        # 앞 음절의 ㅎ 탈락 처리
                        if prev_jong == C_HIEUT:
                            new_jamo = new_jamo[:-1] + C_NONE
                        elif prev_jong == C_NIEUN_HIEUT:
                            new_jamo = new_jamo[:-1] + C_NIEUN
                        elif prev_jong == C_RIEUL_HIEUT:
                            new_jamo = new_jamo[:-1] + C_RIEUL
                        
                        # 현재 음절의 ㅈ을 ㅉ으로 치환
                        cho = O_SSANGJIEUT

            new_jamo += cho + joong + jong
        curr_token.jamo_str = new_jamo

    return tokens


# [제12항 1. 붙임 1 Addendum 1 of Norm 12 Item 1]
#
# 받침 ‘ㄱ(ㄺ), ㄷ, ㅂ(ㄼ), ㅈ(ㄵ)’이 뒤 음절 첫소리 ‘ㅎ’과 결합되는 경우에도, 역시 두 음을 합쳐서
# [ㅋ, ㅌ, ㅍ, ㅊ]으로 발음한다.
# When final consonants ‘ㄱ(ㄺ), ㄷ, ㅂ(ㄼ), ㅈ(ㄵ)’ are combined with the initial sound ‘ㅎ’ of the
# following syllable, the two sounds are combined and pronounced as [ㅋ, ㅌ, ㅍ, ㅊ].
#
#     각하[가카]
#     먹히다[머키다]
#     밝히다[발키다]
#     맏형[마텽]
#     좁히다[조피다]
#     넓히다[널피다]
#     꽂히다[꼬치다]
#     앉히다[안치다]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a405
def norm12_1_a1(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제12항 1. 붙임 2 Addendum 2 of Norm 12 Item 1]
#
# 규정에 따라 ‘ㄷ’으로 발음되는 ‘ㅅ, ㅈ, ㅊ, ㅌ’의 경우에도 이에 준한다.
# This also applies to ‘ㅅ, ㅈ, ㅊ, ㅌ’, which are pronounced as [ㄷ] according to the rules.
#
#     옷 한 벌[오탄벌]
#     낮 한때[나탄때]
#     꽃 한 송이[꼬탄송이]
#     숱하다[수타다]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a405
def norm12_1_a2(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제12항 1. 붙임 2. 'ㄷ'으로 발음되는 'ㅅ, ㅆ, ㅈ, ㅊ, ㅌ'이 뒤 음절 첫소리 'ㅎ'과 결합할 때 [ㅌ]으로 발음합니다.

    토큰 내부(예: '숱하다')와 토큰 경계(예: '옷 한 벌', '낮 한때') 환경을 나누어 처리합니다. 앞 음절의 
    받침(ㅅ, ㅆ, ㅈ, ㅊ, ㅌ)을 탈락시키고 뒤 음절 초성의 'ㅎ'을 'ㅌ'으로 축약합니다. 단, 'ㅈ, ㅊ'은 
    실질 형태소 여부 등 경계 조건에 따라 [ㅊ]으로 축약되는 일반 격음화(예: '꽂히다')와 구분하여 적용합니다.

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 'ㅅ, ㅆ, ㅈ, ㅊ, ㅌ' 받침 뒤에 'ㅎ'이 올 때 [ㅌ]으로 축약이 적용된 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'): 
            continue

        # 1. 토큰 내부(Intra-token) 처리
        jamo = curr_token.jamo_str
        if len(jamo) >= 6:
            new_jamo = ""
            for j in range(0, len(jamo), 3):
                cho, joong, jong = jamo[j:j+3]
                if j >= 3:
                    prev_jong = new_jamo[-1]
                    if cho == O_HIEUT and prev_jong in (C_SIOT, C_SSANGSIOT, C_JIEUT, C_CHIEUT, C_TIEUT):
                        # 단일 토큰 내부는 기본적으로 어간+접미사 결합으로 간주.
                        # ㅈ, ㅊ은 단일 토큰 내부에서 ㅊ으로 축약되므로(예: 꽂히다) 건드리지 않음.
                        if prev_jong not in (C_JIEUT, C_CHIEUT):
                            new_jamo = new_jamo[:-1] + C_NONE  # 앞 받침 탈락
                            cho = O_TIEUT                      # 뒤 초성 ㅌ으로 변경
                new_jamo += cho + joong + jong
            curr_token.jamo_str = new_jamo

        # 2. 토큰 경계(Inter-token) 처리
        if i < len(tokens) - 1:
            curr_jamo = curr_token.jamo_str  # 갱신된 jamo_str 사용
            curr_jong = curr_jamo[-1]

            if curr_jong in (C_SIOT, C_SSANGSIOT, C_JIEUT, C_CHIEUT, C_TIEUT):
                next_idx = i + 1
                is_substantive = False
                
                # 다음 형태소 탐색 (SP 무시)
                if tokens[next_idx].pos == "SP":
                    is_substantive = True
                    next_idx += 1
                elif tokens[next_idx].pos.startswith(SUBSTANTIVE_TAGS):
                    # 피동·사동 접미사 '-히-'가 용언(VV)으로 오분석되는 태깅 이상 보정:
                    # 용언 어간 바로 뒤의 단음절 '히'는 실질 형태소로 보지 않음
                    # (예: "꽂히다시피" -> 꽂/VV + 히/VV 로 오분석되어 [꼬티]가 되는 것을 방지)
                    is_mistagged_hi = tokens[next_idx].surface == '히' and curr_token.pos.startswith('V')
                    if not is_mistagged_hi:
                        is_substantive = True
                    
                if next_idx < len(tokens):
                    next_token = tokens[next_idx]
                    next_cho = next_token.jamo_str[0]
                    
                    if next_cho == O_HIEUT:
                        # ㅈ, ㅊ은 뒤에 실질 형태소나 공백이 올 때만 ㅌ으로 치환
                        if curr_jong in (C_JIEUT, C_CHIEUT) and not is_substantive:
                            continue
                            
                        # 앞 토큰 종성 탈락 및 뒤 토큰 초성 ㅌ 치환
                        curr_token.jamo_str = curr_jamo[:-1] + C_NONE
                        next_token.jamo_str = O_TIEUT + next_token.jamo_str[1:]
                        
    return tokens


# [제12항 2. Norm 12 Item 2]
#
# ‘ㅎ(ㄶ, ㅀ)’ 뒤에 ‘ㅅ’이 결합되는 경우에는, ‘ㅅ’을 [ㅆ]으로 발음한다.
# When ‘ㅅ’ follows ‘ㅎ(ㄶ, ㅀ)’, the ‘ㅅ’ is pronounced as [ㅆ].
#
#     닿소[다쏘]
#     많소[만:쏘]
#     싫소[실쏘]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a405
def norm12_2(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제12항 3. Norm 12 Item 3]
#
# ‘ㅎ’ 뒤에 ‘ㄴ’이 결합되는 경우에는, [ㄴ]으로 발음한다.
# When ‘ㄴ’ follows ‘ㅎ’, it is pronounced as [ㄴ].
#
#     놓는[논는]
#     쌓네[싼네]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a405
def norm12_3(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제12항 3. 붙임 Addendum of Norm 12 Item 3]
#
# ‘ㄶ, ㅀ’ 뒤에 ‘ㄴ’이 결합되는 경우에는, ‘ㅎ’을 발음하지 않는다.
# When ‘ㄴ’ follows ‘ㄶ, ㅀ’, the ‘ㅎ’ is not pronounced.
#
# * ‘뚫네[뚤네→뚤레], 뚫는[뚤는→뚤른]’에 대해서는 제20항 참조.
#   Refer to Norm 20 for ‘뚫네[뚤네→뚤레]’ and ‘뚫는[뚤는→뚤른]’.
#
#     않네[안네]
#     않는[안는]
#     뚫네[뚤네 -> 뚤레]
#     뚫는[뚤는 -> 뚤른]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a405
def norm12_3_a(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제12항 4. Norm 12 Item 4]
#
# ‘ㅎ(ㄶ, ㅀ)’ 뒤에 모음으로 시작된 어미나 접미사가 결합되는 경우에는, ‘ㅎ’을 발음하지 않는다.
# When an ending or suffix starting with a vowel follows ‘ㅎ(ㄶ, ㅀ)’, the ‘ㅎ’ is not pronounced.
#
#     낳은[나은]
#     놓아[노아]
#     쌓이다[싸이다]
#     많아[마:나]
#     않은[아는]
#     닳아[다라]
#     싫어도[시러도]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a405
def norm12_4(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제12항 4. "ㅎ(ㄶ, ㅀ)" 뒤에 모음으로 시작된 어미나 접미사가 결합되는 경우에는, 'ㅎ'을 발음하지 않습니다.

    토큰 내부(예: '쌓이다')와 토큰 경계(예: '많아', '싫어도') 환경을 나누어 처리합니다.
    'ㅎ' 탈락 후 겹받침(ㄶ, ㅀ)에 남는 'ㄴ, ㄹ'은 뒤 음절 초성으로 즉시 연음합니다(예: 않은[아는]).
    본 함수는 파이프라인 설계 상 연음(제13·14항)이 모두 지나간 *후*에 동작하며, 제13·14항의 연음
    테이블은 ㅎ 계열 받침을 의도적으로 제외하므로, g2pK의 `link4`(`ᆭᄋ -> ᄂ`)처럼
    탈락과 연음을 후속 규칙에 맡기지 않고 자체적으로 동시에 수행합니다.

    형태소 분석기의 품사 태그를 활용해 조사(J), 어미(E), 접미사(XSN, XSV, XSA)를 식별합니다.

    Ref:
        g2pk.regular.link4()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/regular.py#L91-L104
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L417-L437

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 모음 어미/접미사 앞의 ㅎ, ㄶ, ㅀ에서 ㅎ이 탈락되고 남은 ㄴ, ㄹ이 연음된 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 1. 토큰 내부(Intra-token) 처리
        jamo = curr_token.jamo_str
        if len(jamo) >= 6:
            new_jamo = ''
            for j in range(0, len(jamo), 3):
                cho, joong, jong = jamo[j:j+3]
                if j >= 3:
                    prev_jong = new_jamo[-1]
                    # 단일 토큰 내부는 기본적으로 어간+접미사 결합으로 간주 (예: 쌓이/VV -> [싸이])
                    if cho == O_IEUNG:
                        if prev_jong == C_HIEUT:
                            new_jamo = new_jamo[:-1] + C_NONE
                        elif prev_jong == C_NIEUN_HIEUT:
                            new_jamo = new_jamo[:-1] + C_NONE
                            cho = O_NIEUN
                        elif prev_jong == C_RIEUL_HIEUT:
                            new_jamo = new_jamo[:-1] + C_NONE
                            cho = O_RIEUL
                new_jamo += cho + joong + jong
            curr_token.jamo_str = new_jamo

        # 2. 토큰 경계(Inter-token) 처리
        if i < len(tokens) - 1:
            next_token = tokens[i+1]
            if next_token.pos.startswith('S'):
                continue

            curr_jamo = curr_token.jamo_str  # 갱신된 jamo_str 사용
            next_cho = next_token.jamo_str[0]

            is_functional = _is_functional(curr_token, next_token)

            if next_cho == O_IEUNG and is_functional:
                curr_jong = curr_jamo[-1]
                if curr_jong == C_HIEUT:
                    curr_token.jamo_str = curr_jamo[:-1] + C_NONE
                elif curr_jong == C_NIEUN_HIEUT:
                    curr_token.jamo_str = curr_jamo[:-1] + C_NONE
                    next_token.jamo_str = O_NIEUN + next_token.jamo_str[1:]
                elif curr_jong == C_RIEUL_HIEUT:
                    curr_token.jamo_str = curr_jamo[:-1] + C_NONE
                    next_token.jamo_str = O_RIEUL + next_token.jamo_str[1:]

    return tokens


# [제13항 Norm 13]
#
# 홑받침이나 쌍받침이 모음으로 시작된 조사나 어미, 접미사와 결합되는 경우에는, 제 음가대로 뒤 음절 첫소리로
# 옮겨 발음한다.
# When a single or double final consonant is combined with a postpositional particle, ending, or suffix
# starting with a vowel, it is moved to the initial sound of the following syllable and pronounced with
# its original value.
#
#     깎아[까까]
#     옷이[오시]
#     있어[이써]
#     낮이[나지]
#     꽂아[꼬자]
#     꽃을[꼬츨]
#     쫓아[쪼차]
#     밭에[바테]
#     앞으로[아프로]
#     덮이다[더피다]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a406
_JONG_TO_CHO = {
    C_GIYEOK: O_GIYEOK, C_SSANGGIYEOK: O_SSANGGIYEOK, C_NIEUN: O_NIEUN,
    C_DIGEUT: O_DIGEUT, C_RIEUL: O_RIEUL, C_MIEUM: O_MIEUM,
    C_BIEUP: O_BIEUP, C_SIOT: O_SIOT, C_SSANGSIOT: O_SSANGSIOT,
    C_JIEUT: O_JIEUT, C_CHIEUT: O_CHIEUT, C_KIEUK: O_KIEUK,
    C_TIEUT: O_TIEUT, C_PIEUP: O_PIEUP
}
def norm13(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제13항. 홑받침이나 쌍받침이 모음으로 시작된 조사, 어미, 접미사와 결합되는 경우에는, 제 음가대로 뒤 음절 첫소리로 옮겨 발음합니다.

    토큰 내부(예: '덮이다')와 토큰 경계(예: '옷이', '깎아') 환경을 나누어 처리합니다.
    형태소 분석기가 어간+접미사를 한 토큰으로 묶는 경우(예: 덮이/VV) 연음 경계가 토큰 내부에
    숨기 때문에, 토큰 경계 순회만으로는 연음이 누락됩니다.

    ※ 주의: 본 엔진의 파이프라인 설계 상, 본 함수는 제15항(실질 형태소 앞 대표음 변환, `norm15`)이
    모두 완료된 *후*에 동작해야 합니다. 이는 zeroth 기여자 Lucas Jo의 코드에서 명시된 전제 조건
    ("15항의 실질형태소에 의한 대표음이 미리 적용되었다고 가정")을 따르는 구조입니다.

    Ref:
        g2pk.regular.link1()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/regular.py#L10-L32
        zeroth genPhoneSeq.py
        - https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L767-L781
        - https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L21-L24

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 홑/쌍받침이 뒤 모음의 초성으로 연음된 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 1. 토큰 내부(Intra-token) 처리
        jamo = curr_token.jamo_str
        if len(jamo) >= 6:
            new_jamo = ''
            for j in range(0, len(jamo), 3):
                cho, joong, jong = jamo[j:j+3]
                if j >= 3:
                    prev_jong = new_jamo[-1]
                    # 단일 토큰 내부는 기본적으로 어간+접미사 결합으로 간주 (예: 덮이/VV -> [더피])
                    if cho == O_IEUNG and prev_jong in _JONG_TO_CHO:
                        new_jamo = new_jamo[:-1] + C_NONE
                        cho = _JONG_TO_CHO[prev_jong]
                new_jamo += cho + joong + jong
            curr_token.jamo_str = new_jamo

        # 2. 토큰 경계(Inter-token) 처리
        if i < len(tokens) - 1:
            next_token = tokens[i+1]
            if next_token.pos.startswith('S'):
                continue

            curr_jamo = curr_token.jamo_str  # 갱신된 jamo_str 사용
            next_cho = next_token.jamo_str[0]

            is_functional = _is_functional(curr_token, next_token)

            if next_cho == O_IEUNG and is_functional:
                curr_jong = curr_jamo[-1]
                if curr_jong in _JONG_TO_CHO:
                    curr_token.jamo_str = curr_jamo[:-1] + C_NONE
                    next_token.jamo_str = _JONG_TO_CHO[curr_jong] + next_token.jamo_str[1:]

    return tokens


# [제14항 Norm 14]
#
# 겹받침이 모음으로 시작된 조사나 어미, 접미사와 결합되는 경우에는, 뒤엣것만을 뒤 음절 첫소리로 옮겨 발음한다.
# (이 경우, ‘ㅅ’은 된소리로 발음함.)
# When a double final consonant is combined with a postpositional particle, ending, or suffix starting with
# a vowel, only the second consonant is moved to the initial sound of the following syllable and pronounced.
# (In this case, ‘ㅅ’ is pronounced as a fortis/tensed sound.)
#
#     넋이[넉씨]
#     앉아[안자]
#     닭을[달글]
#     젊어[절머]
#     곬이[골씨]
#     핥아[할타]
#     읊어[을퍼]
#     값을[갑쓸]
#     없어[업:써]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a407
_GYUB_TO_SPLIT = {
    C_GIYEOK_SIOT: (C_GIYEOK, O_SSANGSIOT),  # ㄳ -> ㄱ, ㅆ
    C_NIEUN_JIEUT: (C_NIEUN, O_JIEUT),       # ㄵ -> ㄴ, ㅈ
    C_RIEUL_GIYEOK: (C_RIEUL, O_GIYEOK),     # ㄺ -> ㄹ, ㄱ
    C_RIEUL_MIEUM: (C_RIEUL, O_MIEUM),       # ㄻ -> ㄹ, ㅁ
    C_RIEUL_BIEUP: (C_RIEUL, O_BIEUP),       # ㄼ -> ㄹ, ㅂ
    C_RIEUL_SIOT: (C_RIEUL, O_SSANGSIOT),    # ㄽ -> ㄹ, ㅆ
    C_RIEUL_TIEUT: (C_RIEUL, O_TIEUT),       # ㄾ -> ㄹ, ㅌ
    C_RIEUL_PIEUP: (C_RIEUL, O_PIEUP),       # ㄿ -> ㄹ, ㅍ
    C_BIEUP_SIOT: (C_BIEUP, O_SSANGSIOT)     # ㅄ -> ㅂ, ㅆ
}
def norm14(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제14항. 겹받침이 모음으로 시작된 조사, 어미, 접미사와 결합되는 경우에는, 뒤엣것만을 뒤 음절 첫소리로 옮겨 발음합니다.

    'ㅅ'은 된소리 'ㅆ'으로 발음합니다.

    토큰 내부(예: '거침없이')와 토큰 경계(예: '앉아', '값을') 환경을 나누어 처리합니다.
    형태소 분석기가 파생어 전체를 한 토큰으로 묶는 경우(예: 거침없이/MAG) 겹받침 연음 경계가
    토큰 내부에 숨기 때문에, 토큰 경계 순회만으로는 연음이 누락됩니다.

    Ref:
        g2pk.regular.link2()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/regular.py#L35-L52
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L783-L818

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 겹받침의 뒤 자음이 모음의 초성으로 연음된 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 1. 토큰 내부(Intra-token) 처리
        jamo = curr_token.jamo_str
        if len(jamo) >= 6:
            new_jamo = ''
            for j in range(0, len(jamo), 3):
                cho, joong, jong = jamo[j:j+3]
                if j >= 3:
                    prev_jong = new_jamo[-1]
                    # 단일 토큰 내부는 기본적으로 어간+접미사 결합으로 간주 (예: 거침없이/MAG -> [거치멉씨])
                    if cho == O_IEUNG and prev_jong in _GYUB_TO_SPLIT:
                        remain_jong, move_cho = _GYUB_TO_SPLIT[prev_jong]
                        new_jamo = new_jamo[:-1] + remain_jong
                        cho = move_cho
                new_jamo += cho + joong + jong
            curr_token.jamo_str = new_jamo

        # 2. 토큰 경계(Inter-token) 처리
        if i < len(tokens) - 1:
            next_token = tokens[i+1]
            if next_token.pos.startswith('S'):
                continue

            curr_jamo = curr_token.jamo_str  # 갱신된 jamo_str 사용
            next_cho = next_token.jamo_str[0]

            is_functional = _is_functional(curr_token, next_token)

            if next_cho == O_IEUNG and is_functional:
                curr_jong = curr_jamo[-1]
                if curr_jong in _GYUB_TO_SPLIT:
                    remain_jong, move_cho = _GYUB_TO_SPLIT[curr_jong]
                    curr_token.jamo_str = curr_jamo[:-1] + remain_jong
                    next_token.jamo_str = move_cho + next_token.jamo_str[1:]

    return tokens


# [제15항 Norm 15]
#
# 받침 뒤에 모음 ‘ㅏ, ㅓ, ㅗ, ㅜ, ㅟ’ 들로 시작되는 실질 형태소가 연결되는 경우에는, 대표음으로 바꾸어서
# 뒤 음절 첫소리로 옮겨 발음한다.
# When a substantive morpheme starting with the vowels ‘ㅏ, ㅓ, ㅗ, ㅜ, ㅟ’ follows a final consonant,
# it is changed to its representative sound and moved to the initial sound of the following syllable.
#
#     밭 아래[바다래]
#     늪 앞[느밥]
#     젖어미[저더미]
#     맛없다[마덥따]
#     겉옷[거돋]
#     헛웃음[허두슴]
#     꽃 위[꼬뒤]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a408
_REP_ONSET_REAL_MORPH = {
    # ㄱ 계열 (ㄱ, ㄲ, ㅋ, ㄳ, ㄺ) -> ㄱ
    C_GIYEOK: O_GIYEOK, C_SSANGGIYEOK: O_GIYEOK, C_KIEUK: O_GIYEOK,
    C_GIYEOK_SIOT: O_GIYEOK, C_RIEUL_GIYEOK: O_GIYEOK,
    # ㄴ 계열 겹받침 (ㄵ, ㄶ) -> ㄴ
    C_NIEUN_JIEUT: O_NIEUN, C_NIEUN_HIEUT: O_NIEUN,
    # ㄷ 계열 (ㄷ, ㅅ, ㅆ, ㅈ, ㅊ, ㅌ, ㅎ) -> ㄷ
    C_DIGEUT: O_DIGEUT, C_SIOT: O_DIGEUT, C_SSANGSIOT: O_DIGEUT,
    C_JIEUT: O_DIGEUT, C_CHIEUT: O_DIGEUT, C_TIEUT: O_DIGEUT, C_HIEUT: O_DIGEUT,
    # ㄹ 계열 겹받침 (ㄼ, ㄽ, ㄾ, ㅀ) -> ㄹ
    C_RIEUL_BIEUP: O_RIEUL, C_RIEUL_SIOT: O_RIEUL,
    C_RIEUL_TIEUT: O_RIEUL, C_RIEUL_HIEUT: O_RIEUL,
    # ㅁ 계열 겹받침 (ㄻ) -> ㅁ
    C_RIEUL_MIEUM: O_MIEUM,
    # ※ 공명음 홑받침(ㄴ, ㄹ, ㅁ, ㅇ)은 테이블에서 제외한다. 해설에 따르면 제15항의 절음은
    #   받침이 대표음 [ㄱ, ㄷ, ㅂ] 중 하나로 바뀐 후 이동하는 현상이므로 공명음 홑받침은 대상이 아니다.
    #   포함 시 "달리던 아이", "그는 아무"가 [달리더 나이], [그느 나무]로 과발동한다.
    #   겹받침은 붙임("그중 하나만을 옮겨 발음", 예: 닭 앞에[다가페])에 따라 유지한다.
    # ㅂ 계열 (ㅂ, ㅍ, ㅄ, ㄿ) -> ㅂ
    C_BIEUP: O_BIEUP, C_PIEUP: O_BIEUP, C_BIEUP_SIOT: O_BIEUP, C_RIEUL_PIEUP: O_BIEUP,
    # ※ 받침 ㅇ(C_IEUNG)은 초성으로 이동할 수 없는 연구개 비음이므로 테이블에서 제외한다.
    #   포함 시 "식당 음식[식땅 음식]"의 ㅇ 종성이 삭제되는 오류가 발생한다 (예: [식따 음식]).
}
# 조항의 "ㅏ, ㅓ, ㅗ, ㅜ, ㅟ"는 대표 표기이며, 해설에 따르면 단모음 ㅣ와 반모음 ㅣ[j] 계열
# (ㅑ, ㅒ, ㅕ, ㅖ, ㅛ, ㅠ)을 제외한 나머지 모음(ㅐ, ㅔ, ㅚ 등)을 모두 포함하는 것으로 본다.
# ㅣ·j 계열이 제외된 이유는 그 환경에서는 제29항의 ㄴ첨가가 대신 발동하기 때문이다 (예: 앞일[암닐], 꽃잎[꼰닙]).
_TARGET_VOWELS_REAL_MORPH = (
    N_A, N_AE, N_EO, N_E, N_O, N_WA, N_WAE, N_OE,
    N_U, N_WEO, N_WE, N_WI, N_EU, N_UI,
)  # ㅏ, ㅐ, ㅓ, ㅔ, ㅗ, ㅘ, ㅙ, ㅚ, ㅜ, ㅝ, ㅞ, ㅟ, ㅡ, ㅢ
def norm15(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제15항. 받침 뒤에 모음 ‘ㅏ, ㅓ, ㅗ, ㅜ, ㅟ’ 들로 시작되는 실질 형태소가 연결되는 경우에는, 대표음으로 바꾸어서 뒤 음절 첫소리로 옮겨 발음합니다.

    본 엔진은 g2pK의 정규식 기반 한계를 극복하고, MorphToken 배열 순회를 통해 O(N)으로 재현했습니다.
    POS 태그를 활용해 실질 형태소와 형식 형태소를 구분하는 휴리스틱은 zeroth 기여자 Lucas Jo님의 코드에서
    확립된 인사이트를 계승합니다.

    ※ 주의: 본 엔진의 파이프라인 설계 상, 이 함수는 제13항(형식 형태소 연음, `norm13`)을 통과하기 *전*에
    실행되어야 합니다. 그렇지 않을 경우 "맛없다"가 [마덥따]가 아닌 [마섭따]로 오독됩니다.

    ※ 참고: 붙임의 "값어치[가버치]"는 '-어치'가 현행 사전상 접미사임에도 절음되는 예외입니다(해설: 역사적
    실질 형태소). 본 엔진은 pecab이 '어치'를 NNG(실질)로 태깅하는 데 의존하므로, 사전 패치 시 주의가 필요합니다.

    Ref:
        g2pk.regular.link3()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/regular.py#L55-L88
        zeroth genPhoneSeq.py
        - https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L702-L764
        - https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L21-L24

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 실질 형태소 앞에서 대표음으로 연음된 리스트.
    """
    for i in range(len(tokens) - 1):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 뒤에 이어지는 다음 실질 형태소를 찾기 위해 공백(SP) 토큰은 건너뜀
        next_idx = i + 1
        if tokens[next_idx].pos == "SP":
            next_idx += 1

        if next_idx >= len(tokens):
            continue

        next_token = tokens[next_idx]
        if next_token.pos.startswith('S'):
            continue

        curr_jamo = curr_token.jamo_str
        curr_jong = curr_jamo[-1]

        if curr_jong == C_NONE:
            continue

        next_jamo = next_token.jamo_str
        next_cho = next_jamo[0]
        next_joong = next_jamo[1] if len(next_jamo) >= 2 else ""

        # 모음(비 ㅣ·j 계열)으로 시작하는 실질 형태소인지 확인.
        # '있-'은 ㅣ로 시작하지만 ㄴ첨가 없이 절음되는 어휘적 예외 (예: 맛있다[마딛따] 원칙, 값있는[가빈는]).
        # 여기서 원칙 발음을 만든 뒤, 허용 발음(맛있다[마싣따])은 후속 norm15_p가 덮어쓴다.
        is_target_vowel = next_joong in _TARGET_VOWELS_REAL_MORPH or next_token.surface.startswith("있")
        if next_cho == O_IEUNG and is_target_vowel:
            is_functional = _is_functional(curr_token, next_token)

            if not is_functional:
                if curr_jong in _REP_ONSET_REAL_MORPH:
                    rep_cho = _REP_ONSET_REAL_MORPH[curr_jong]

                    # 밭(ㅂㅏㅌ) + 아래(ㅇㅏㄹㅐ) -> 바(ㅂㅏ) + 다래(ㄷㅏㄹㅐ)
                    # 맛(ㅁㅏᆺ) + 없다(ㅇㅓㅄㄷㅏ) -> 마(ㅁㅏ) + 덥다(ㄷㅓㅄㄷㅏ)
                    curr_token.jamo_str = curr_jamo[:-1] + C_NONE
                    next_token.jamo_str = rep_cho + next_jamo[1:]

    return tokens


# [제15항 다만 Proviso of Norm 15]
#
# ‘맛있다, 멋있다’는 [마싣따], [머싣따]로도 발음할 수 있다.
# ‘맛있다’ and ‘멋있다’ can also be pronounced as [마싣따] and [머싣따].
#
#     맛있다[마딛따/마싣따]
#     멋있다[머딛따/머싣따]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a408
def norm15_p(tokens: List[MorphToken]) -> List[MorphToken]:
    """"
    제15항 다만. "맛있다", "멋있다"는 [마싣따], [머싣따]로도 발음할 수 있다.

    현대 언중의 실제 발음 습관을 반영하여, '맛'/'멋' + '있'의 조합은 15항 원칙(중화 후 연음: [마덥따])을
    무시하고 조사 결합과 동일하게 [마싣따/머싣따]로 예외 연음 처리합니다.

    본 엔진에서는 이 허용 조항을 별도의 독립된 함수로 분리하여 파이프라인에서 취사선택할 수 있도록 구현했습니다.

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: "맛/멋있다"가 [마싣/머싣]으로 예외 연음된 리스트.
    """
    for i in range(len(tokens) - 1):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        next_idx = i + 1
        if tokens[next_idx].pos == "SP":
            next_idx += 1

        if next_idx >= len(tokens):
            continue

        next_token = tokens[next_idx]
        if next_token.pos.startswith('S'):
            continue

        # 맛/멋 + 있다 -> 'ㅅ'을 연음시킴
        if curr_token.surface in ("맛", "멋") and next_token.surface.startswith("있"):
            curr_jamo = curr_token.jamo_str
            next_jamo = next_token.jamo_str

            # 종성 ㅅ(C_SIOT)을 떼고 초성 ㅅ(O_SIOT)으로 넘김
            curr_token.jamo_str = curr_jamo[:-1] + C_NONE
            next_token.jamo_str = O_SIOT + next_jamo[1:]

    return tokens


# [제15항 붙임 Addendum of Norm 15]
#
# 겹받침의 경우에는, 그중 하나만을 옮겨 발음한다.
# In the case of double final consonants, only one of them is moved and pronounced.
#
#     넋 없다[너겁따]
#     닭 앞에[다가페]
#     값어치[가버치]
#     값있는[가빈는]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a408
def norm15_a(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제16항 Norm 16]
#
# 한글 자모의 이름은 그 받침소리를 연음하되, ‘ㄷ, ㅈ, ㅊ, ㅋ, ㅌ, ㅍ, ㅎ’의 경우에는 특별히 다음과 같이 발음한다.
# The names of Hangeul consonants are liaised with their final sounds, but in the case of
# ‘ㄷ, ㅈ, ㅊ, ㅋ, ㅌ, ㅍ, ㅎ’, they are specifically pronounced as follows.
#
#     디귿이[디그시]
#     디귿을[디그슬]
#     디귿에[디그세]
#     지읒이[지으시]
#     지읒을[지으슬]
#     지읒에[지으세]
#     치읓이[치으시]
#     치읓을[치으슬]
#     치읓에[치으세]
#     키읔이[키으기]
#     키읔을[키으글]
#     키읔에[키으게]
#     티읕이[티으시]
#     티읕을[티으슬]
#     티읕에[티으세]
#     피읖이[피으비]
#     피읖을[피으블]
#     피읖에[피으베]
#     히읗이[히으시]
#     히읗을[히으슬]
#     히읗에[히으세]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a409
_JAMO_NAME_EXCEPTIONS = {
    C_DIGEUT: C_SIOT, C_JIEUT: C_SIOT, C_CHIEUT: C_SIOT,
    C_TIEUT: C_SIOT, C_HIEUT: C_SIOT,
    C_KIEUK: C_GIYEOK, C_PIEUP: C_BIEUP
}
def norm16(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제16항. 한글 자모의 이름은 그 받침소리를 연음하되, "ㄷ, ㅈ, ㅊ, ㅋ, ㅌ, ㅍ, ㅎ"의 경우에는 특별히 발음한다.

    Ref:
        g2pk.special.jamo()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L66-L76
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L820

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 자모 이름의 예외 연음 발음(ㅅ, ㄱ, ㅂ 등)으로 종성이 치환된 리스트.
    """
    for i in range(len(tokens) - 1):
        curr_token = tokens[i]
        next_token = tokens[i+1]

        if curr_token.pos.startswith('S') or next_token.pos.startswith('S'):
            continue

        if curr_token.surface in ("디귿", "지읒", "치읓", "키읔", "티읕", "피읖", "히읗"):
            curr_jamo = curr_token.jamo_str
            next_cho = next_token.jamo_str[0]

            # 조사(J*)만이 아니라 서술격 조사(디귿이다[디그시다])와 '을/ETN' 오태깅까지 포괄하도록
            # 공용 형식 형태소 판별(_is_functional)을 사용한다.
            if next_cho == O_IEUNG and _is_functional(curr_token, next_token):
                curr_jong = curr_jamo[-1]
                if curr_jong in _JAMO_NAME_EXCEPTIONS:
                    curr_token.jamo_str = curr_jamo[:-1] + _JAMO_NAME_EXCEPTIONS[curr_jong]

    return tokens
