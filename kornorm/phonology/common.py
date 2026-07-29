from dataclasses import dataclass

from kornorm.utils.jamo import (
    O_GIYEOK, O_DIGEUT, O_BIEUP, O_SIOT, O_JIEUT, O_IEUNG,
    O_SSANGGIYEOK, O_SSANGDIGEUT, O_SSANGBIEUP, O_SSANGSIOT, O_SSANGJIEUT,

    N_A, N_EO, N_YEO, N_EU, N_I,
)

# 경음화(된소리) 매핑 (예사소리 -> 된소리)
FORTIS_MAPPING = {
    O_GIYEOK: O_SSANGGIYEOK,
    O_DIGEUT: O_SSANGDIGEUT,
    O_BIEUP: O_SSANGBIEUP,
    O_SIOT: O_SSANGSIOT,
    O_JIEUT: O_SSANGJIEUT
}

# 파생 접미사 판별용 튜플
DERIV_SUFFIX_TAGS = ("XSN", "XSV", "XSA")

# 실질 형태소 판별용 튜플
SUBSTANTIVE_TAGS = (
    "N",    # 체언 전체 (NNG, NNP, NNB, NNBC, NR, NP)

    "M",    # 수식언 전체 (MM, MAG, MAJ)

    "VV",   # 동사
    "VA",   # 형용사
    "VX",   # 보조 용언
    "VCN",  # 부정 지정사 (아니다)
            # 주의: 긍정 지정사 "VCP"(이다)는 서술격 조사로 연음 대상이므로 제외

    "XR",   # 어근

    "IC",   # 감탄사

    "SN",   # 숫자 (예: 3 연대[삼년대])
    "SL",   # 외국어/알파벳
    "SH",   # 한자
)

@dataclass
class MorphToken:
    """형태소 단위의 데이터와 메타정보를 담는 순수 메모리 객체"""
    surface: str
    pos: str
    start_offset: int
    end_offset: int
    jamo_str: str
    is_hanja: bool = False
    compound_structure: str = ''
    pronunciation: str = ''


# 연음(제12항 4, 제13항, 제14항)·절음(제15항)·자모 이름(제16항)·구개음화(제17항)는 모두
# "뒤 형태소가 형식 형태소인지"를 기준으로 갈라지므로, 판별 로직을 하나로 모아 규칙 간 불일치를 방지한다.
_FUNCTIONAL_ONSET_VOWELS = (N_A, N_EO, N_YEO, N_EU, N_I)  # 실제 어미가 취할 수 있는 어두 모음 (아/어/여/으/이 계열)
def _is_functional(curr_token: MorphToken, next_token: MorphToken) -> bool:
    """
    뒤 토큰이 형식 형태소(조사, 어미, 접미사, 서술격 조사)인지 판별합니다.

    pecab의 대표적인 태깅 이상 두 가지를 함께 보정합니다:
    - 모음으로 시작하는 어미(E*) 태그가 ㅏ, ㅓ, ㅕ, ㅡ, ㅣ 이외의 모음으로 시작하면 실질 형태소의
      오태깅으로 간주합니다 (예: "겉옷" -> 겉/VA + 옷/EC. 실제 어미는 그런 모음으로 시작하지 않음).
    - 용언 어간 바로 뒤의 단음절 '음'/'이'가 명사(NNG)·부사(MAG)·감탄사(IC) 등으로 오분석되면
      전성어미(-음)나 파생 접미사(-이)로 간주합니다
      (예: "헛웃음을" -> 웃/VV+EP + 음/NNG, "벼훑이" -> 훑/VV + 이/IC).

    Args:
        curr_token (MorphToken): 판별 문맥이 되는 앞 토큰.
        next_token (MorphToken): 형식 형태소 여부를 판별할 뒤 토큰.

    Returns:
        bool: 형식 형태소로 판단되면 True.
    """
    next_jamo = next_token.jamo_str
    if next_token.pos.startswith('E') and len(next_jamo) >= 2:
        if next_jamo[0] == O_IEUNG and next_jamo[1] not in _FUNCTIONAL_ONSET_VOWELS:
            return False

    if next_token.pos.startswith(('J', 'E', "VCP")) or next_token.pos in DERIV_SUFFIX_TAGS:
        return True

    if next_token.surface in ('음', '이') and curr_token.pos.startswith('V'):
        return True

    return False


# [어절 결속도 Eojeol Cohesion]
#
# 제18항 붙임과 제29항 붙임 2는 "두 단어를 이어서 한 마디로 발음하는 경우" 공백을 넘어
# 음운 변동을 적용한다. 결속 여부는 공백(SP) 양쪽 토큰의 품사 쌍으로 판정하며,
# 조사·어미로 끝난 어절 뒤는 휴지가 성립하는 느슨한 경계로 보아 배제한다
# (예: "책을 읽거나", "아이는 엿을"은 배제 / "옷 입다", "할 일"은 결속).
def _is_cohesive_boundary(prev_token: MorphToken, next_token: MorphToken) -> bool:
    """
    공백을 사이에 둔 두 어절이 한 마디로 발음될 만큼 결속됐는지 판정합니다 (제29항 붙임 2 기준).

    허용 품사 쌍: 맨체언+용언(옷 입다), 관형사·수사+체언(한 일), 관형사형 어미+체언(먹은 엿, 할 일),
    부사+용언(잘 입다). 부사+체언은 배제합니다 (예: "그냥 일하기가"는 첨가 대상이 아님).

    Args:
        prev_token (MorphToken): 공백 직전 토큰 (앞 어절의 마지막 형태소).
        next_token (MorphToken): 공백 직후 토큰 (뒤 어절의 첫 형태소).

    Returns:
        bool: 결속된 경계로 판단되면 True.
    """
    prev_pos = prev_token.pos.split('+')[-1]
    next_pos = next_token.pos

    if prev_pos.startswith('N') and next_pos.startswith(("VV", "VA", "VX")):
        return True
    if prev_pos in ("MM", "NR") and next_pos.startswith('N'):
        return True
    if prev_pos == "ETM" and next_pos.startswith('N'):
        return True
    if prev_pos == "MAG" and next_pos.startswith(("VV", "VA", "VX")):
        return True
    return False


def _is_tight_cohesive_boundary(prev_token: MorphToken, next_token: MorphToken) -> bool:
    """
    제18항 붙임용의 더 좁은 결속도 판정: 맨명사+용언 쌍(책 넣는다, 밥 먹는다)만 허용합니다.

    수사+단위명사(여덟 명)처럼 비음화 없이 발음되는 것이 자연스러운 경계를 배제하기 위해
    제29항 붙임 2(`_is_cohesive_boundary`)보다 좁게 잡습니다.

    Args:
        prev_token (MorphToken): 공백 직전 토큰.
        next_token (MorphToken): 공백 직후 토큰.

    Returns:
        bool: 결속된 경계로 판단되면 True.
    """
    prev_pos = prev_token.pos.split('+')[-1]
    return prev_pos.startswith("NN") and next_token.pos.startswith(("VV", "VA", "VX"))


def _ends_with_functional(token: MorphToken) -> bool:
    """
    어절의 마지막 토큰이 조사·어미(형식 형태소)로 끝나는지 판별합니다.

    조사·어미로 끝난 어절 뒤는 "두 단어를 이어서 한 마디로 발음하는 경우"로 보지 않는다는
    어절 결속도 공통 원칙의 판별 헬퍼입니다 (복합 태그는 마지막 태그 기준.
    예: 할수록/VV+EC -> EC -> True, 밭/NNG -> False).

    Args:
        token (MorphToken): 공백 직전 토큰 (앞 어절의 마지막 형태소).

    Returns:
        bool: 조사(J*)·어미(E*)로 끝나면 True.
    """
    return token.pos.split('+')[-1].startswith(('J', 'E'))

