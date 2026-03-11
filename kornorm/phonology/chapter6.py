# [국립국어원 한국어 어문 규범 표준어규정 제2부 표준발음법 제6장 경음화]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a392

from typing import List
from kornorm.phonology.common import MorphToken
from kornorm.phonology.common import FORTIS_MAPPING

from kornorm.utils.jamo import (
    O_DIGEUT, O_SIOT, O_JIEUT,

    C_NIEUN, C_NIEUN_JIEUT, C_RIEUL, C_RIEUL_MIEUM, C_RIEUL_BIEUP,
    C_RIEUL_TIEUT, C_MIEUM,
)

# [제23항 Norm 23]
#
# 받침 ‘ㄱ(ㄲ, ㅋ, ㄳ, ㄺ), ㄷ(ㅅ, ㅆ, ㅈ, ㅊ, ㅌ), ㅂ(ㅍ, ㄼ, ㄿ, ㅄ)’ 뒤에 연결되는 ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’은
# 된소리로 발음한다.
# The consonants ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’ following the final consonants ‘ㄱ(ㄲ, ㅋ, ㄳ, ㄺ)’,
# ‘ㄷ(ㅅ, ㅆ, ㅈ, ㅊ, ㅌ)’, or ‘ㅂ(ㅍ, ㄼ, ㄿ, ㅄ)’ are pronounced as fortis (tensed) sounds.
#
#     국밥[국빱]
#     깎다[깍따]
#     넋받이[넉빠지]
#     삯돈[삭똔]
#     닭장[닥짱]
#     칡범[칙뻠]
#     뻗대다[뻗때다]
#     옷고름[옫꼬름]
#     있던[읻떤]
#     꽂고[꼳꼬]
#     꽃다발[꼳따발]
#     낯설다[낟썰다]
#     밭갈이[받까리]
#     솥전[솓쩐]
#     곱돌[곱똘]
#     덮개[덥깨]
#     옆집[엽찝]
#     넓죽하다[넙쭈카다]
#     읊조리다[읍쪼리다]
#     값지다[갑찌다]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a416
def norm23(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제24항 Norm 24]
#
# 어간 받침 ‘ㄴ(ㄵ), ㅁ(ㄻ)’ 뒤에 결합되는 어미의 첫소리 ‘ㄱ, ㄷ, ㅅ, ㅈ’은 된소리로 발음한다.
# The initial sounds ‘ㄱ, ㄷ, ㅅ, ㅈ’ of endings following the verb stem final consonants ‘ㄴ(ㄵ)’ or ‘ㅁ(ㄻ)’
# are pronounced as fortis (tensed) sounds.
#
#     신고[신:꼬]
#     껴안다[껴안따]
#     앉고[안꼬]
#     얹다[언따]
#     삼고[삼:꼬]
#     더듬지[더듬찌]
#     닮고[담:꼬]
#     젊지[점:찌]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a417

# [제24항 다만 Proviso of Norm 24]
#
# 다만, 피동, 사동의 접미사 ‘-기-’는 된소리로 발음하지 않는다.
# However, the passive or causative suffix ‘-기-’ is not pronounced as a fortis (tensed) sound.
#
#     안기다
#     감기다
#     굶기다
#     옮기다
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a417
def norm24(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제24항. 어간 받침 ‘ㄴ(ㄵ), ㅁ(ㄻ)’ 뒤에 결합되는 어미의 첫소리 ‘ㄱ, ㄷ, ㅅ, ㅈ’은 된소리로 발음합니다.

    본 메소드는 `제24항 다만` 조항을 같이 처리합니다.

    제24항 다만. 피동, 사동의 접미사 ‘-기-’는 된소리로 발음하지 않습니다.
    형태소 태그를 검사하여 "어미(E)"인 경우에만 적용하므로, 접미사인 "-기-"는 자연스럽게 예외 처리됩니다.

    Ref:
        g2pk.special.verb_nieun()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L103-L126
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L559-L585

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 조건에 맞는 어미의 첫소리가 된소리로 치환된 토큰 리스트.
    """
    for i in range(len(tokens) - 1):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 1. 어간(V: 동사/형용사)인지 확인
        if not curr_token.pos.startswith('V'):
            continue

        curr_jong = curr_token.jamo_str[-1]

        # 2. 어간 받침이 "ㄴ, ㄵ, ㅁ, ㄻ"인지 확인
        if curr_jong in (C_NIEUN, C_NIEUN_JIEUT, C_MIEUM, C_RIEUL_MIEUM):
            next_idx = i + 1
            if tokens[next_idx].pos == "SP":
                next_idx += 1
            if next_idx >= len(tokens):
                continue

            next_token = tokens[next_idx]

            # 3. 뒤따르는 형태소가 어미(E)인지 확인
            #   - 형태소 분석기는 "-기-"를 어미(E)가 아니라 접미사(XSV, XSA)로 태깅합니다.
            if next_token.pos.startswith('E'):
                next_cho = next_token.jamo_str[0]
                if next_cho in FORTIS_MAPPING:
                    next_token.jamo_str = FORTIS_MAPPING[next_cho] + next_token.jamo_str[1:]

    return tokens


# [제25항 Norm 25]
#
# 어간 받침 ‘ㄼ, ㄾ’ 뒤에 결합되는 어미의 첫소리 ‘ㄱ, ㄷ, ㅅ, ㅈ’은 된소리로 발음한다.
# The initial sounds ‘ㄱ, ㄷ, ㅅ, ㅈ’ of endings following the verb stem final consonants ‘ㄼ’ or ‘ㄾ’
# are pronounced as fortis (tensed) sounds.
#
#     넓게[널께]
#     핥다[할따]
#     훑소[훌쏘]
#     떫지[떨:찌]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a418
def norm25(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제25항. 어간 받침 ‘ㄼ, ㄾ’ 뒤에 결합되는 어미의 첫소리 ‘ㄱ, ㄷ, ㅅ, ㅈ’은 된소리로 발음합니다.

    Ref:
        g2pk.special.rieulbieub()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L90-L100
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L587-L614

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 조건에 맞는 어미의 첫소리가 된소리로 치환된 토큰 리스트.
    """
    for i in range(len(tokens) - 1):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        if not curr_token.pos.startswith('V'):
            continue

        curr_jong = curr_token.jamo_str[-1]

        if curr_jong in (C_RIEUL_BIEUP, C_RIEUL_TIEUT):
            next_idx = i + 1
            if tokens[next_idx].pos == "SP":
                next_idx += 1
            if next_idx >= len(tokens):
                continue

            next_token = tokens[next_idx]

            if next_token.pos.startswith('E'):
                next_cho = next_token.jamo_str[0]
                if next_cho in FORTIS_MAPPING:
                    next_token.jamo_str = FORTIS_MAPPING[next_cho] + next_token.jamo_str[1:]

    return tokens


# [제26항 Norm 26]
#
# 한자어에서, ‘ㄹ’ 받침 뒤에 연결되는 ‘ㄷ, ㅅ, ㅈ’은 된소리로 발음한다.
# In Sino-Korean words, ‘ㄷ, ㅅ, ㅈ’ following the final consonant ‘ㄹ’ are pronounced as fortis (tensed) sounds.
#
#     갈등[갈뜽]
#     발동[발똥]
#     절도[절또]
#     말살[말쌀]
#     불소[불쏘](弗素)
#     일시[일씨]
#     갈증[갈쯩]
#     물질[물찔]
#     발전[발쩐]
#     몰상식[몰쌍식]
#     불세출[불쎄출]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a419

# [제26항 다만 Proviso of Norm 26]
#
# 다만, 같은 한자가 겹쳐진 단어의 경우에는 된소리로 발음하지 않는다.
# However, in words where the same Chinese character is repeated, they are not pronounced as fortis (tensed) sounds.
#
#     허허실실[허허실실](虛虛實實)
#     절절-하다[절절하다](切切-)
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a419

# [제26항 Norm 26]
def norm26(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제26항 본항. 한자어에서, ‘ㄹ’ 받침 뒤에 연결되는 ‘ㄷ, ㅅ, ㅈ’은 된소리로 발음합니다.

    본 엔진은 표준국어대사전 리소스를 통해 획득한 MorphToken의 `is_hanja` 속성을 활용하여 한자어 여부를 판단합니다.

    제26항 다만. 같은 한자가 겹쳐진 단어의 경우에는 된소리로 발음하지 않습니다.
    본 엔진은 예외 조항(다만)의 "같은 한자가 겹쳐진 경우"를 탐지하기 위해, 1D 자모 배열의 3단위(초·중·종) 인덱스
    슬라이싱 동등 비교 알고리즘을 구현하여 적용합니다.

    Ref:
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L616

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 메타데이터(is_hanja)가 주입된 자모 분해 토큰 리스트.

    Returns:
        List[MorphToken]: 한자어 내부 및 경계에서 'ㄹ' 뒤의 "ㄷ, ㅅ, ㅈ"이 된소리로 치환된 토큰 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 1. 단일 토큰 내부의 한자어 경음화 및 "다만" 조항(동일 한자 반복) 처리
        if getattr(curr_token, "is_hanja", False):
            jamo = curr_token.jamo_str
            new_jamo = ""
            for j in range(0, len(jamo), 3):
                cho, joong, jong = jamo[j:j+3]

                # 두 번째 음절부터 이전 음절(3자모)과 비교 가능
                if j >= 3:
                    prev_syl = jamo[j-3:j]  # 이전 음절 전체 (초, 중, 종)
                    prev_jong = prev_syl[-1]

                    if prev_jong == C_RIEUL and cho in (O_DIGEUT, O_SIOT, O_JIEUT):
                        curr_syl = cho + joong + jong

                        # 다만 조항: 이전 음절과 현재 음절이 자모 단위로 완전히 똑같은지 확인
                        #            (예: 절[ㅈㅓㄹ] == 절[ㅈㅓㄹ])
                        if prev_syl == curr_syl:
                            pass  # 예외 발동: 된소리로 바꾸지 않고 그냥 넘어감
                        else:
                            cho = FORTIS_MAPPING[cho]

                new_jamo += cho + joong + jong
            curr_token.jamo_str = new_jamo

        # 2. 토큰 경계(인접한 두 형태소) 사이의 한자어 경음화 및 "다만" 조항 처리
        next_idx = i + 1
        if next_idx < len(tokens):
            next_token = tokens[next_idx]

            # 한자어의 형태소 결합은 띄어쓰기가 없는 복합어("물" + "질") 환경에서만 적용
            if next_token.pos.startswith('S') or next_token.pos == "SP":
                continue

            # 앞 토큰과 뒤 토큰이 모두 한자어일 때
            if getattr(curr_token, "is_hanja", False) and getattr(next_token, "is_hanja", False):
                curr_jamo = curr_token.jamo_str
                next_jamo = next_token.jamo_str

                curr_jong = curr_jamo[-1]
                next_cho = next_jamo[0]

                if curr_jong == C_RIEUL and next_cho in (O_DIGEUT, O_SIOT, O_JIEUT):
                    # 앞 단어의 마지막 음절(3자모)과 뒤 단어의 첫 음절(3자모) 슬라이싱 비교
                    curr_last_syl = curr_jamo[-3:]
                    next_first_syl = next_jamo[:3]

                    if curr_last_syl == next_first_syl:
                        continue  # 다만 조항: 예외 발동
                    else:
                        next_token.jamo_str = FORTIS_MAPPING[next_cho] + next_jamo[1:]

    return tokens


# [제27항 Norm 27]
#
# 관형사형 ‘-(으)ㄹ’ 뒤에 연결되는 ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’은 된소리로 발음한다.
# The sounds ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’ following the adnominal form ‘-(으)ㄹ’ are pronounced as fortis (tensed) sounds.
#
#     할 것을[할꺼슬]
#     갈 데가[갈떼가]
#     할 바를[할빠를]
#     할 수는[할쑤는]
#     할 적에[할쩌게]
#     갈 곳[갈꼳]
#     할 도리[할또리]
#     만날 사람[만날싸람]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a420

# [제27항 다만 Proviso of Norm 27]
#
# 다만, 끊어서 말할 적에는 예사소리로 발음한다.
# However, when speaking with a pause, they are pronounced as plain sounds.
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a420
def norm27(
    tokens: List[MorphToken],
    ignore_space_as_pause: bool = True,
) -> List[MorphToken]:
    """
    제27항 본항. 관형사형 ‘-(으)ㄹ’ 뒤에 연결되는 ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’은 된소리로 발음합니다.

    `ignore_space_as_pause` 파라미터가 `True`일 때는 텍스트 상의 띄어쓰기(SP)를 단순 공백으로 취급하여
    강건하게 경음화를 적용하며, `False`일 때는 띄어쓰기를 명시적인 휴지(pause)로 해석하여 제27항 다만 조항
    ("끊어서 말할 적에는 예사소리로 발음한다")을 엄격하게 적용합니다.

    형태론적으로 관형사형 어미 뒤에는 띄어쓰기가 수반되는 것이 원칙("할 것을")이나, 실제 텍스트 데이터나
    형태소 분석기의 토큰화 과정에서는 공백이 누락되는 오류("할것을")가 매우 잦습니다.

    본 엔진은 띄어쓰기 유무에 관계없이 형태소 결합 맥락만을 신뢰하여 강건하게 처리하는 것을 지향하여
    `ignore_space_as_pause` 파라미터 기본값을 `True`로 설정합니다.

    Ref:
        g2pk.special.modifying_rieul()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L159-L163
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L618-L644

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.
        ignore_space_as_pause (bool): 띄어쓰기를 휴지(Pause)로 간주하지 않고 경음화를 적용할지 여부. (기본값: True)

    Returns:
        List[MorphToken]: 관형사형 'ㄹ' 뒤의 자음이 조건에 따라 된소리로 치환된 토큰 리스트.
    """
    for i in range(len(tokens) - 1):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 관형사형 전성어미(ETM)로 한정한다. 'E' 전체로 검사하면 ㄹ로 끝나는 연결어미('-거늘' 등)나
        # 명사형 어미 오태깅('을/ETN' 등)까지 경음화가 오발동한다 (예: "헛웃음을 지으며" -> [찌으며]).
        # 형태소 분석기는 축약형("할" = 하/VV + ㄹ/ETM)을 "VV+ETM" 복합 태그 단일 토큰으로 병합하므로,
        # 태그의 마지막 성분이 ETM인지 검사한다.
        if curr_token.pos.split('+')[-1] == "ETM" and curr_token.jamo_str[-1] == C_RIEUL:
            # 오태깅 가드: 체언 토큰에 공백 없이 바로 붙은 VV/VA 계열 관형사형은 합성명사가
            # 조각난 것(예: "칼날" -> 칼/NNG + 날/VV+ETM)이므로 경음화하지 않는다. 정상 표기에서
            # 용언 관형사형은 공백 뒤(만날 사람)나 체언+하다 파생(도착한/XSV+ETM)으로만 나타난다.
            if (
                curr_token.pos.startswith(("VV", "VA"))
                and i >= 1
                and tokens[i - 1].pos.startswith('N')
            ):
                continue

            next_idx = i + 1
            has_space = False

            # 공백 토큰 존재 여부 확인
            if next_idx < len(tokens) and tokens[next_idx].pos == "SP":
                has_space = True
                next_idx += 1

            if next_idx >= len(tokens):
                continue

            # 공백이 존재하고, 이를 휴지로 취급하기로(ignore_space_as_pause=False) 설정했다면 경음화 차단
            if has_space and not ignore_space_as_pause:
                continue

            next_token = tokens[next_idx]
            if next_token.pos.startswith('S'):
                continue

            next_cho = next_token.jamo_str[0]
            if next_cho in FORTIS_MAPPING:
                next_token.jamo_str = FORTIS_MAPPING[next_cho] + next_token.jamo_str[1:]

    return tokens


# [제27항 붙임 Addendum of Norm 27]
#
# ‘-(으)ㄹ’로 시작되는 어미의 경우에도 이에 준한다.
# This also applies to endings starting with ‘-(으)ㄹ’.
#
#     할걸[할껄]
#     할밖에[할빠께]
#     할세라[할쎄라]
#     할수록[할쑤록]
#     할지라도[할찌라도]
#     할지언정[할찌언정]
#     할진대[할찐대]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a420

# 'ㄹ' 종성 바로 뒤에 이어지는, 규범 붙임에 열거된 '-(으)ㄹ' 계열 어미의 잔여 표기.
# '-ㄹ지'와 '-ㄹ게'는 ㄹ 말음 어간 + 평어미 조합(만들지[만들지], 달게[달게])과 표면형이 충돌하여
# 형태소 태그만으로는 구분할 수 없으므로 보수적으로 제외한다.
_RIEUL_ENDING_REMAINDERS = ('걸', "밖에", "세라", "수록", "지라도", "지언정", "진대")
def norm27_a(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제27항 붙임. ‘-(으)ㄹ’로 시작되는 어미(-ㄹ걸, -ㄹ수록 등)의 내부에서 발생하는 경음화를 처리합니다.

    형태소 분석기는 이 계열의 어미를 어간과 병합한 복합 태그 단일 토큰("할수록" = VV+EC)으로 내놓으므로,
    용언+어미 복합 토큰 내부를 스캔하여 'ㄹ' 종성 뒤 잔여 표기가 열거된 어미와 일치할 때만 경음화합니다.
    잔여 표기 전체 일치를 요구하므로 ㄹ 말음 어간의 평어미 활용(만들지)은 건드리지 않으면서도,
    ㄹ 말음 어간 병합(만들수록[만들쑤록])과 '-을' 계열(먹을지라도[머글찌라도])은 자연스럽게 처리됩니다.

    Ref:
        g2pk.special.modifying_rieul()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L165-L171
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L618-L644

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 'ㄹ'로 시작되는 어미 내부의 자음이 된소리로 치환된 토큰 리스트.
    """
    for curr_token in tokens:
        if curr_token.pos.startswith('S'):
            continue

        # 1. 순수 어미(E) 토큰: 어미 표기 내부의 'ㄹ' 뒤 자음을 그대로 경음화
        if curr_token.pos.startswith('E'):
            jamo = curr_token.jamo_str
            new_jamo = ""
            for j in range(0, len(jamo), 3):
                cho, joong, jong = jamo[j:j+3]
                # 이전 글자의 종성이 'ㄹ'이고, 현재 글자의 초성이 경음화 대상인 경우
                if j >= 3 and new_jamo[-1] == C_RIEUL and cho in FORTIS_MAPPING:
                    cho = FORTIS_MAPPING[cho]
                new_jamo += cho + joong + jong
            curr_token.jamo_str = new_jamo
            continue

        # 2. 용언 어간과 어미가 병합된 복합 토큰(VV+EC, VV+EF 등): 'ㄹ' 종성 뒤 잔여 표기가
        #    열거된 '-(으)ㄹ' 계열 어미와 온전히 일치할 때만 경음화
        if '+E' in curr_token.pos and curr_token.pos.split('+')[0].startswith(('V', "XS")):
            surface = curr_token.surface
            jamo = curr_token.jamo_str
            if len(jamo) != 3 * len(surface):
                continue

            for k in range(len(surface) - 1):
                if jamo[3 * k + 2] != C_RIEUL:
                    continue
                if surface[k + 1:] not in _RIEUL_ENDING_REMAINDERS:
                    continue
                next_cho = jamo[3 * (k + 1)]
                if next_cho in FORTIS_MAPPING:
                    curr_token.jamo_str = (
                        jamo[:3 * (k + 1)] + FORTIS_MAPPING[next_cho] + jamo[3 * (k + 1) + 1:]
                    )
                break

    return tokens


# [제28항 Norm 28]
#
# 표기상으로는 사이시옷이 없더라도, 관형격 기능을 지니는 사이시옷이 있어야 할(휴지가 성립되는) 합성어의 경우에는,
# 뒤 단어의 첫소리 ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’을 된소리로 발음한다.
# In compound words where a genitive ‘saisiot’ (intercalary ‘ㅅ’) is functionally required even if not written,
# the initial sounds ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’ of the following word are pronounced as fortis (tensed) sounds.
#
#     문-고리[문꼬리]
#     눈-동자[눈똥자]
#     신-바람[신빠람]
#     산-새[산쌔]
#     손-재주[손째주]
#     길-가[길까]
#     물-동이[물똥이]
#     발-바닥[발빠닥]
#     굴-속[굴쏙]
#     술-잔[술짠]
#     바람-결[바람껼]
#     그믐-달[그믐딸]
#     아침-밥[아침빱]
#     잠-자리[잠짜리]
#     강-가[강까]
#     초승-달[초승딸]
#     등-불[등뿔]
#     창-살[창쌀]
#     강-줄기[강쭐기]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a421
def norm28(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제28항. 사이시옷이 없는 관형격 합성어의 된소리 발음을 처리합니다.

    본 조항의 "관형격 기능을 지니는 환경"은 언어학적 맥락에 따라 결정되므로 규칙 기반의 일괄 처리가
    매우 까다롭습니다. (예: "손등"[손뜽] vs "손발"[손발])

    zeroth 기여자 Lucas Jo님 역시 본 조항에 대해 "기본적으로 된소리로 됨... 어색한 경우 수정이 필요할 수 있음"
    이라며 규칙화의 한계를 명시한 바 있습니다.

    Ref:
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L646-L647

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Raises:
        NotImplementedError: 2D LUT를 통한 일반화가 불가능한 조항입니다.
    """
    # TODO: 휴리스틱 기반의 된소리 자동 적용 로직을 검토.
    #       일반적인 2D LUT 매트릭스에 포함하지 않고, Arrow 사전 리소스(`stdict_words.arrow`)의
    #       합성어 발음 데이터를 통해 개별적으로 처리하는 것 고려.
    raise NotImplementedError()
