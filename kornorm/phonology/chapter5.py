# [국립국어원 한국어 어문 규범 표준어규정 제2부 표준발음법 제5장 음의 동화]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a391

from typing import List
from kornorm.phonology.common import MorphToken
from kornorm.phonology.common import DERIV_SUFFIX_TAGS, _is_functional

from kornorm.utils.jamo import (
    O_NIEUN, O_RIEUL, O_IEUNG, O_JIEUT, O_CHIEUT, O_HIEUT,

    N_EO, N_YEO, N_O, N_YO, N_OE, N_I,

    C_NONE, C_NIEUN, C_DIGEUT, C_RIEUL, C_RIEUL_TIEUT, C_TIEUT,
)

# [제17항 Norm 17]
#
# 받침 ‘ㄷ, ㅌ(ㄾ)’이 조사나 접미사의 모음 ‘ㅣ’와 결합되는 경우에는, [ㅈ, ㅊ]으로 바꾸어서 뒤 음절 첫소리로 옮겨
# 발음한다.
# When the final consonants ‘ㄷ, ㅌ(ㄾ)’ are combined with the vowel ‘ㅣ’ of a postpositional particle or suffix,
# they are changed to [ㅈ, ㅊ] and moved to the initial sound of the following syllable.
#
#     곧이듣다[고지듣따]
#     굳이[구지]
#     미닫이[미:다지]
#     땀받이[땀바지]
#     밭이[바치]
#     벼훑이[벼훌치]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a410
def norm17(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제17항. 받침 ‘ㄷ, ㅌ(ㄾ)’이 조사나 접미사의 모음 ‘ㅣ’와 결합되는 경우에는, [ㅈ, ㅊ]으로 바꾸어서 뒤 음절 첫소리로 옮겨 발음합니다.

    구개음화 관련 메소드 입니다.

    토큰 내부(예: '굳이', '미닫이')와 토큰 경계(예: '밭이') 환경을 나누어 처리합니다.
    형태소 분석기가 어간+접미사를 한 토큰으로 묶는 경우(예: 굳이/MAG) 구개음화 경계가 토큰 내부에
    숨기 때문에, 토큰 경계 순회만으로는 후속 연음(제13항)이 ㄷ을 제 음가로 옮겨 [구디]가 됩니다.

    g2pK의 로직을 반영하여 'ㅣ'뿐만 아니라 'ㅕ'(ㅣ+ㅓ)가 결합할 때도 적용합니다.

    Ref:
        g2pk.special.palatalize()
        — https://github.com/Kyubyong/g2pK/blob/master/g2pk/special.py#L141-L152
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L439-L459

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: "ㄷ, ㅌ(ㄾ)" 받침이 'ㅣ'나 'ㅕ'와 결합하여 [ㅈ, ㅊ]으로 구개음화된 토큰 리스트.
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
                    # 단일 토큰 내부는 기본적으로 어간+접미사 결합으로 간주 (예: 굳이/MAG -> [구지], 같이/MAG -> [가치])
                    if cho == O_IEUNG and joong in (N_I, N_YEO):
                        if prev_jong == C_DIGEUT:
                            new_jamo = new_jamo[:-1] + C_NONE
                            cho = O_JIEUT
                        elif prev_jong == C_TIEUT:
                            new_jamo = new_jamo[:-1] + C_NONE
                            cho = O_CHIEUT
                        elif prev_jong == C_RIEUL_TIEUT:
                            new_jamo = new_jamo[:-1] + C_RIEUL
                            cho = O_CHIEUT
                new_jamo += cho + joong + jong
            curr_token.jamo_str = new_jamo

        # 2. 토큰 경계(Inter-token) 처리
        if i < len(tokens) - 1:
            next_idx = i + 1
            if tokens[next_idx].pos == "SP":
                continue # 구개음화는 단어 내부(조사/접미사 결합)에서 일어나므로 공백을 넘지 않음

            next_token = tokens[next_idx]
            if next_token.pos.startswith('S'):
                continue

            if not _is_functional(curr_token, next_token):
                continue

            curr_jamo = curr_token.jamo_str  # 갱신된 jamo_str 사용
            curr_jong = curr_jamo[-1]

            next_jamo = next_token.jamo_str
            next_cho = next_jamo[0]
            next_joong = next_jamo[1] if len(next_jamo) >= 2 else ""

            # 'ㅇ' + 'ㅣ' 또는 'ㅕ'
            if next_cho == O_IEUNG and next_joong in (N_I, N_YEO):
                if curr_jong == C_DIGEUT:
                    # ㄷ -> ㅈ
                    curr_token.jamo_str = curr_jamo[:-1] + C_NONE
                    next_token.jamo_str = O_JIEUT + next_jamo[1:]
                elif curr_jong == C_TIEUT:
                    # ㅌ -> ㅊ
                    curr_token.jamo_str = curr_jamo[:-1] + C_NONE
                    next_token.jamo_str = O_CHIEUT + next_jamo[1:]
                elif curr_jong == C_RIEUL_TIEUT:
                    # ㄾ -> ㄹ, ㅊ
                    curr_token.jamo_str = curr_jamo[:-1] + C_RIEUL
                    next_token.jamo_str = O_CHIEUT + next_jamo[1:]

    return tokens


# [제17항 붙임 Addendum of Norm 17]
#
# ‘ㄷ’ 뒤에 접미사 ‘히’가 결합되어 ‘티’를 이루는 것은 [치]로 발음한다.
# When the suffix ‘히’ is combined after ‘ㄷ’ to form ‘티’, it is pronounced as [치].
#
#     굳히다[구치다]
#     닫히다[다치다]
#     묻히다[무치다]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a410
def norm17_a(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제17항 붙임. ‘ㄷ’ 뒤에 접미사 ‘히’가 결합되어 ‘티’를 이루는 것은 [치]로 발음합니다.

    토큰 내부(예: '굳히다' -> 굳히/VV)와 토큰 경계(예: '닫히다' -> 닫/VV + 히다/EC) 환경을 나누어
    처리합니다. 본 함수는 2D LUT의 일반 격음화(ㄷ+ㅎ -> ㅌ, 예: 맏형[마텽])보다 먼저 실행되어
    접미사 '히' 환경을 선점해야 합니다.

    Ref:
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L461-L468

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.[cite: 5]

    Returns:
        List[MorphToken]: 'ㄷ' 뒤에 접미사 '히'가 결합하여 [치]로 구개음화된 토큰 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 1. 토큰 내부(Intra-token) 처리
        # 피동·사동 접미사 '-히-'는 용언 활용에서만 나타나므로 용언(V*) 토큰에 한정한다.
        # 명사 내부의 ㄷ+ㅎ은 실질 형태소 경계로, 제12항 붙임 1의 일반 격음화 대상이다 (예: 맏형[마텽]).
        jamo = curr_token.jamo_str
        if len(jamo) >= 6 and curr_token.pos.startswith('V'):
            new_jamo = ''
            for j in range(0, len(jamo), 3):
                cho, joong, jong = jamo[j:j+3]
                if j >= 3:
                    prev_jong = new_jamo[-1]
                    # 단일 용언 토큰 내부는 어간+접미사 결합으로 간주 (예: 굳히/VV -> [구치])
                    if cho == O_HIEUT and joong in (N_I, N_YEO):
                        if prev_jong == C_DIGEUT:
                            new_jamo = new_jamo[:-1] + C_NONE
                            cho = O_CHIEUT
                new_jamo += cho + joong + jong
            curr_token.jamo_str = new_jamo

        # 2. 토큰 경계(Inter-token) 처리
        if i < len(tokens) - 1:
            next_idx = i + 1
            if tokens[next_idx].pos == "SP":
                continue

            next_token = tokens[next_idx]
            if next_token.pos.startswith('S'):
                continue

            if not _is_functional(curr_token, next_token):
                continue

            curr_jamo = curr_token.jamo_str  # 갱신된 jamo_str 사용
            curr_jong = curr_jamo[-1]

            next_jamo = next_token.jamo_str
            next_cho = next_jamo[0]
            next_joong = next_jamo[1] if len(next_jamo) >= 2 else ""

            # 'ㅎ' + 'ㅣ' 또는 'ㅕ'
            if next_cho == O_HIEUT and next_joong in (N_I, N_YEO):
                if curr_jong == C_DIGEUT:
                    # ㄷ + ㅎ -> ㅊ
                    curr_token.jamo_str = curr_jamo[:-1] + C_NONE
                    next_token.jamo_str = O_CHIEUT + next_jamo[1:]

    return tokens


# [제18항 Norm 18]
#
# 받침 ‘ㄱ(ㄲ, ㅋ, ㄳ, ㄺ), ㄷ(ㅅ, ㅆ, ㅈ, ㅊ, ㅌ, ㅎ), ㅂ(ㅍ, ㄼ, ㄿ, ㅄ)’은 ‘ㄴ, ㅁ’ 앞에서 [ㅇ, ㄴ, ㅁ]으로 발음한다.
# Final consonants ‘ㄱ(ㄲ, ㅋ, ㄳ, ㄺ)’, ‘ㄷ(ㅅ, ㅆ, ㅈ, ㅊ, ㅌ, ㅎ)’, and ‘ㅂ(ㅍ, ㄼ, ㄿ, ㅄ)’ are pronounced as [ㅇ, ㄴ, ㅁ], respectively, before ‘ㄴ, ㅁ’.
#
#     먹는[멍는]
#     국물[궁물]
#     깎는[깡는]
#     키읔만[키응만]
#     몫몫이[몽목씨]
#     긁는[긍는]
#     흙만[흥만]
#     닫는[단는]
#     짓는[진:는]
#     옷맵시[온맵씨]
#     있는[인는]
#     맞는[만는]
#     젖멍울[전멍울]
#     쫓는[쫀는]
#     꽃망울[꼰망울]
#     붙는[분는]
#     놓는[논는]
#     잡는[잠는]
#     밥물[밤물]
#     앞마당[암마당]
#     밟는[밤:는]
#     읊는[음는]
#     없는[엄:는]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a411
def norm18(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제18항 붙임 Addendum of Norm 18]
#
# 두 단어를 이어서 한 마디로 발음하는 경우에도 이와 같다.
# This also applies when two words are connected and pronounced as a single phrase.
#
#     책 넣는다[챙넌는다]
#     흙 말리다[흥말리다]
#     옷 맞추다[온맏추다]
#     밥 먹는다[밤멍는다]
#     값 매기다[감매기다]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a411
def norm18_a(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError(
        "cross-word nasalization (e.g., 밥 먹는다[밤멍는다]) is deferred until an eojeol-cohesion "
        "based boundary policy is implemented (see `apply_phonology_lut` docstring)"
    )


# [제19항 Norm 19]
#
# 받침 ‘ㅁ, ㅇ’ 뒤에 연결되는 ‘ㄹ’은 [ㄴ]으로 발음한다.
# The ‘ㄹ’ following the final consonants ‘ㅁ, ㅇ’ is pronounced as [ㄴ].
#
#     담력[담:녁]
#     침략[침:냑]
#     강릉[강능]
#     항로[항:노]
#     대통령[대:통녕]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a412
def norm19(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제19항 붙임 Addendum of Norm 19]
#
# 받침 ‘ㄱ, ㅂ’ 뒤에 연결되는 ‘ㄹ’도 [ㄴ]으로 발음한다.
# The ‘ㄹ’ following the final consonants ‘ㄱ, ㅂ’ is also pronounced as [ㄴ].
#
#     막론[막논 -> 망논]
#     석류[석뉴 -> 성뉴]
#     협력[협녁 -> 혐녁]
#     법리[법니 -> 범니]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a412
def norm19_a(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제20항 Norm 20]
#
# ‘ㄴ’은 ‘ㄹ’의 앞이나 뒤에서 [ㄹ]로 발음한다.
# ‘ㄴ’ is pronounced as [ㄹ] before or after ‘ㄹ’.
#
# (1) ‘ㄴ’이 ‘ㄹ’ 뒤에 오는 경우:
#     난로[날:로]
#     신라[실라]
#     천리[철리]
#     광한루[광:할루]
#     대관령[대:괄령]
#
# (2) ‘ㄴ’이 ‘ㄹ’ 앞에 오는 경우:
#     칼날[칼랄]
#     물난리[물랄리]
#     줄넘기[줄럼끼]
#     핥는지[할른지]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a413
def norm20(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제20항 붙임 Addendum of Norm 20]
#
# 첫소리 ‘ㄴ’이 ‘ㄶ, ㅀ’ 뒤에 연결되는 경우에도 이에 준한다.
# This also applies when the initial sound ‘ㄴ’ follows ‘ㄶ, ㅀ’.
#
#     앓는[알른]
#     뚫는[뚤른]
#     핥네[할레]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a413
def norm20_a(tokens: List[MorphToken]) -> List[MorphToken]:
    raise NotImplementedError("use `from kornorm.phonology.apply_lut import apply_phonology_lut`")


# [제20항 다만 Proviso of Norm 20]
#
# 다음과 같은 단어들은 ‘ㄹ’을 [ㄴ]으로 발음한다.
# In the following words, ‘ㄹ’ is pronounced as [ㄴ].
#
#     의견란[의:견난]
#     임진란[임:진난]
#     생산량[생산냥]
#     결단력[결딴녁]
#     공권력[공꿘녁]
#     동원령[동:원녕]
#     상견례[상견네]
#     횡단로[횡단노]
#     이원론[이:원논]
#     입원료[이뷘뇨]
#     구근류[구근뉴]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a413
def norm20_p(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제20항 다만. 한자어에서 'ㄴ' 뒤에 'ㄹ'이 결합할 때, 'ㄹ'을 [ㄴ]으로 발음합니다.

    한국어 어문 규범 해설에 따르면 "2음절 한자어 뒤에 ‘ㄹ’로 시작하는 한자가 결합할 때에는 ‘ㄹ’이 ‘ㄴ’으로
    바뀌는 경향이 강하다"고 명시되어 있습니다. 본 엔진은 이를 휴리스틱으로 구현하여 MorphToken의 `is_hanja`
    속성과 음절 길이를 통해 O(N)으로 재현합니다.

    ※ 주의: 본 엔진의 파이프라인 설계 상, 이 함수는 2D LUT(`apply_phonology_lut`)를 통과하기 *전*에
    실행되어야 합니다. 먼저 'ㄹ'을 'ㄴ'으로 선점 변환해 두어야, 이후 LUT에서 제20항 본항
    (유음화: ㄴ+ㄹ->ㄹㄹ)의 일괄 적용을 회피할 수 있습니다.

    Ref:
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L498-L518

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 조건에 맞는 한자어 내부/경계에서 'ㄹ'이 'ㄴ'으로 예외 변환된 토큰 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]

        if curr_token.pos.startswith('S'):
            continue

        # 1. 단일 토큰 내부에서 발생하는 경우 (예: "의견란"이 하나의 명사로 묶여 들어온 경우)
        # 조건: 한자어이면서 전체 길이가 3음절 이상일 때
        if getattr(curr_token, "is_hanja", False) and len(curr_token.surface) >= 3:
            jamo = curr_token.jamo_str
            new_jamo = ""
            # 3단위(초,중,종) 순회
            for j in range(0, len(jamo), 3):
                cho, joong, jong = jamo[j:j+3]

                # 현재 글자의 초성이 'ㄹ'이고, 앞 글자의 종성이 'ㄴ'이며,
                # 앞에 최소 2음절(6자모) 이상이 존재할 때 (j >= 6)
                if j >= 6 and cho == O_RIEUL and new_jamo[-1] == C_NIEUN:
                    cho = O_NIEUN

                new_jamo += cho + joong + jong
            curr_token.jamo_str = new_jamo

        # 2. 두 토큰 사이에서 발생하는 경우 (예: "의견" + "란"으로 분리된 경우)
        if i < len(tokens) - 1:
            next_token = tokens[i+1]
            if next_token.pos.startswith('S') or next_token.pos == "SP":
                continue

            # 조건: 앞 토큰과 뒤 토큰 모두 한자어일 때
            if getattr(curr_token, "is_hanja", False) and getattr(next_token, "is_hanja", False):
                # 2음절 이상의 한자어 + 1음절의 한자어(접미사 형태)
                if len(curr_token.surface) >= 2 and len(next_token.surface) == 1:
                    curr_jong = curr_token.jamo_str[-1]
                    next_cho = next_token.jamo_str[0]

                    if curr_jong == C_NIEUN and next_cho == O_RIEUL:
                        # ㄹ -> ㄴ으로 선점 변환
                        next_token.jamo_str = O_NIEUN + next_token.jamo_str[1:]

    return tokens


# [제21항 Norm 21]
#
# 위에서 지적한 이외의 자음 동화는 인정하지 않는다.
# Consonant assimilations other than those specified above are not recognized.
#
#     감기[감:기](×[강:기])
#     옷감[옫깜](×[옥깜])
#     있고[읻꼬](×[익꼬])
#     꽃길[꼳낄](×[꼭낄])
#     젖먹이[전머기](×[점머기])
#     문법[문뻡](×[뭄뻡])
#     꽃밭[꼳빙](×[꼽빙])
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a414


# [제22항 Norm 22]
#
# 다음과 같은 용언의 어미는 [어]로 발음함을 원칙으로 하되, [여]로 발음함도 허용한다.
# The following endings of predicates are ideally pronounced as [어], but pronouncing them as [여] is also permitted.
#
#     되어[되어/되여]
#     피어[피어/피여]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a415
def norm22(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제22항. 용언의 어미는 [어]로 발음함을 원칙으로 하되, [여]로 발음함도 허용합니다.

    본 엔진에서는 이를 허용 조항으로 분류하여 파이프라인에서 선택적으로 적용할 수 있도록 제공합니다.

    Ref:
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L524-L535

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 용언 어간 뒤의 어미 "-어"가 "-여"로 치환된 토큰 리스트.
    """
    for i in range(len(tokens) - 1):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        next_idx = i + 1
        if tokens[next_idx].pos == "SP":
            continue

        next_token = tokens[next_idx]
        if next_token.pos.startswith('S'):
            continue

        curr_jamo = curr_token.jamo_str
        curr_jong = curr_jamo[-1]
        curr_joong = curr_jamo[1] if len(curr_jamo) >= 2 else ""

        # 앞 토큰이 용언 어간(V)이고, 받침이 없으며 모음이 'ㅣ' 또는 'ㅚ'일 때
        if curr_token.pos.startswith('V') and curr_jong == C_NONE and curr_joong in (N_I, N_OE):
            next_jamo = next_token.jamo_str
            next_cho = next_jamo[0]
            next_joong = next_jamo[1] if len(next_jamo) >= 2 else ""

            # 뒤 토큰이 어미(E)이고 "-어"일 때 "-여"로 치환
            if next_token.pos.startswith('E') and next_cho == O_IEUNG and next_joong == N_EO:
                next_token.jamo_str = next_cho + N_YEO + next_jamo[2:]

    return tokens


# [제22항 붙임 Addendum of Norm 22]
#
# ‘이오, 아니오’도 이에 준하여 [이오, 이요], [아니오, 아니요]로 발음함을 허용한다.
# Similarly, ‘이오, 아니오’ are permitted to be pronounced as [이오, 이요] and [아니오, 아니요].
#
#     이오[이오/이요]
#     아니오[아니오/아니요]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a415
def norm22_a(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제22항 붙임. ‘이오, 아니오’도 이에 준하여 [이오, 이요], [아니오, 아니요]로 발음함을 허용합니다.

    본 엔진에서는 이를 허용 조항으로 분류하여 파이프라인에서 선택적으로 적용할 수 있도록 제공합니다.

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: "이오", "아니오"의 어미 "-오"가 "-요"로 치환된 토큰 리스트.
    """
    for i in range(len(tokens) - 1):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        next_idx = i + 1
        if tokens[next_idx].pos == "SP":
            continue

        next_token = tokens[next_idx]
        if next_token.pos.startswith('S'):
            continue

        curr_surface = curr_token.surface

        # '이'(긍정지정사 VCP) 또는 "아니"(부정지정사 VCN)일 때
        if (curr_surface == "이" and curr_token.pos == "VCP") or \
           (curr_surface == "아니" and curr_token.pos == "VCN"):

            next_jamo = next_token.jamo_str
            next_cho = next_jamo[0]
            next_joong = next_jamo[1] if len(next_jamo) >= 2 else ""

            # 뒤 토큰이 어미(E)이고 "-오"일 때 "-요"로 치환
            if next_token.pos.startswith('E') and next_cho == O_IEUNG and next_joong == N_O:
                next_token.jamo_str = next_cho + N_YO + next_jamo[2:]

    return tokens
