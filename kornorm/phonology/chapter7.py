# [국립국어원 한국어 어문 규범 표준어규정 제2부 표준발음법 제7장 음의 첨가]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a393

from typing import List
from kornorm.phonology.engine import MorphToken
from kornorm.phonology.common import FORTIS_MAPPING, DERIV_SUFFIX_TAGS, SUBSTANTIVE_TAGS

from kornorm.utils.jamo import (
    O_NIEUN, O_RIEUL, O_MIEUM, O_IEUNG,

    N_YA, N_YEO, N_YO, N_YU, N_I,

    C_NONE, C_NIEUN, C_DIGEUT, C_RIEUL, C_SIOT,
)

def _get_internal_boundaries(compound_structure: str) -> List[int]:
    """'솜-이불'과 같은 사전 구조에서 '-'가 위치한 음절 인덱스를 반환합니다."""
    if not compound_structure or '-' not in compound_structure:
        return []

    boundaries = []
    cur_len = 0
    # '-'로 쪼갠 뒤 글자 수를 누적하여 경계 지점(음절 인덱스)을 찾음
    for part in compound_structure.split('-')[:-1]:
        cur_len += len(part)
        boundaries.append(cur_len)
    return boundaries

# [제29항 Norm 29]
#
# 합성어 및 파생어에서, 앞 단어나 접두사의 끝이 자음이고 뒤 단어나 접미사의 첫음절이 ‘이, 야, 여, 요, 유’인
# 경우에는, ‘ㄴ’ 음을 첨가하여 [니, 냐, 녀, 뇨, 뉴]로 발음한다.
# In compound words and derivatives, when the final sound of the preceding word or prefix is a consonant
# and the first syllable of the following word or suffix starts with ‘이, 야, 여, 요, 유’, the sound ‘ㄴ’
# is added and pronounced as [니, 냐, 녀, 뇨, 뉴].
#
#     솜-이불[솜:니불]
#     홑-이불[혼니불]
#     막-일[망닐]
#     삯-일[상닐]
#     맨-입[맨닙]
#     꽃-잎[꼰닙]
#     내복-약[내:봉냑]
#     한-여름[한녀름]
#     남존-여비[남존녀비]
#     신-여성[신녀성]
#     색-연필[생년필]
#     직행-열차[지캥녈차]
#     늑막-염[능망념]
#     콩-엿[콩녇]
#     담-요[담:뇨]
#     눈-요기[눈뇨기]
#     영업-용[영엄뇽]
#     식용-유[시공뉴]
#     백분-율[백뿐뉼]
#     밤-윷[밤:뉼]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a422

# [제29항 다만 1st Proviso of Norm 29]
#
# 다만, 다음과 같은 말들은 ‘ㄴ’ 음을 첨가하여 발음하되, 표기대로 발음할 수 있다.
# However, the following words are pronounced by adding the sound ‘ㄴ’, but can also be pronounced
# according to their written forms.
#
#     이죽-이죽[이중니죽/이주기죽]
#     야금-야금[야금냐금/야그먀금]
#     검열[검:녈/거:멸]
#     욜랑-욜랑[욜랑놀랑/욜랑욜랑]
#     금융[금늉/그뮹]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a422

# [제29항 붙임 1 Addendum 1 of Norm 29]
#
# ‘ㄹ’ 받침 뒤에 첨가되는 ‘ㄴ’ 음은 [ㄹ]로 발음한다.
# The sound ‘ㄴ’ added after the final consonant ‘ㄹ’ is pronounced as [ㄹ].
#
#     들-일[들:릴]
#     솔-잎[솔립]
#     설-익다[설릭따]
#     물-약[물략]
#     불-여우[불려우]
#     서울-역[서울력]
#     물-엿[물렫]
#     휘발-유[휘발류]
#     유들-유들[유들류들]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a422

# [제29항 붙임 2 Addendum 2 of Norm 29]
#
# 두 단어를 이어서 한 마디로 발음하는 경우에도 이에 준한다.
# This also applies when two words are connected and pronounced as a single phrase.
#
#     한 일[한닐]
#     옷 입다[온닙따]
#     서른여섯[서른녀섣]
#     3 연대[삼년대]
#     먹은 엿[머근녇]
#     할 일[할릴]
#     잘 입다[잘립따]
#     스물여섯[스물려섣]
#     1 연대[일련대]
#     먹을 엿[머글렫]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a422
def norm29(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    제29항. 합성어 및 파생어에서, 앞 단어나 접두사의 끝이 자음이고 뒤 단어나 접미사의 첫 음절이 "이, 야, 여, 요, 유"인 경우에는, 'ㄴ'소리를 첨가하여 [니, 냐, 녀, 뇨, 뉴]로 발음합니다.

    본 메소드는 `붙임` 조항들을 같이 처리합니다.

    제29항 붙임 1. 'ㄹ' 받침 뒤에 첨가되는 'ㄴ'소리는 [ㄹ]로 발음합니다.
    제29항 붙임 2. 두 단어를 이어서 한 마디로 발음하는 경우에도 이에 준합니다.

    본 엔진에서는 인접한 두 MorphToken 사이(띄어쓰기 유무 포함)의 품사(POS) 조합을 분석하거나,
    표준국어대사전 기반의 합성어 구조(예: "솜-이불") 메타데이터를 활용하여
    합성/파생/연음 환경을 인지하고 'ㄴ'/'ㄹ'을 첨가합니다.

    Ref:
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L649-L681

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 조건에 맞는 경계에 'ㄴ' 또는 'ㄹ'이 첨가된 토큰 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 1. 단일 토큰 내부의 합성어 경계 처리 ("솜-이불"이 한 토큰으로 들어온 경우)
        internal_boundaries = _get_internal_boundaries(getattr(curr_token, "compound_structure", ''))
        if internal_boundaries:
            jamo_list = list(curr_token.jamo_str)
            for bnd in internal_boundaries:
                j = bnd * 3  # 초/중/종 3단위이므로 곱하기 3
                if j >= len(jamo_list) or j == 0: continue

                prev_jong = jamo_list[j - 1]
                next_cho = jamo_list[j]
                next_joong = jamo_list[j + 1] if j + 1 < len(jamo_list) else ""

                # 앞 단어의 끝이 자음(받침 있음)인지 확인
                if prev_jong != C_NONE:
                    # 뒤 단어의 첫 음절이 '이, 야, 여, 요, 유'인지 확인
                    if next_cho == O_IEUNG and next_joong in (N_I, N_YA, N_YEO, N_YO, N_YU):
                        # 'ㄴ' 첨가 (단, 앞 받침이 'ㄹ'이면 'ㄹ' 첨가)
                        inserted_cho = O_RIEUL if prev_jong == C_RIEUL else O_NIEUN
                        jamo_list[j] = inserted_cho

            curr_token.jamo_str = "".join(jamo_list)

        # 2. 토큰 간 경계 처리 (띄어쓰기 포함, 구 구성 및 신조어 파생어 방어)
        if i < len(tokens) - 1:
            next_idx = i + 1
            if tokens[next_idx].pos == 'SP':
                next_idx += 1
            if next_idx >= len(tokens):
                continue

            next_token = tokens[next_idx]
            if next_token.pos.startswith('S'):
                continue

            is_curr_valid = curr_token.pos.startswith(SUBSTANTIVE_TAGS) or curr_token.pos == "XPN"
            is_next_valid = next_token.pos.startswith(SUBSTANTIVE_TAGS) or next_token.pos in DERIV_SUFFIX_TAGS

            if is_curr_valid and is_next_valid:
                curr_jong = curr_token.jamo_str[-1]

                # 앞 단어의 끝이 자음(받침 있음)인지 확인
                if curr_jong != C_NONE:
                    next_cho = next_token.jamo_str[0]
                    next_joong = next_token.jamo_str[1] if len(next_token.jamo_str) >= 2 else ""

                    # 뒤 단어의 첫 음절이 '이, 야, 여, 요, 유'인지 확인
                    if next_cho == O_IEUNG and next_joong in (N_I, N_YA, N_YEO, N_YO, N_YU):
                        # 'ㄴ' 첨가 (단, 앞 받침이 'ㄹ'이면 'ㄹ' 첨가)
                        inserted_cho = O_RIEUL if curr_jong == C_RIEUL else O_NIEUN
                        next_token.jamo_str = inserted_cho + next_token.jamo_str[1:]

    return tokens


# [제29항 다만 2nd Proviso of Norm 29]
#
# 다만, 다음과 같은 단어에서는 ‘ㄴ(ㄹ)’ 음을 첨가하여 발음하지 않는다.
# However, the sound ‘ㄴ(ㄹ)’ is not added in the following words.
#
#     6·25[유기오]
#     3·1절[사밀쩔]
#     송별-연[송:별련]
#     등-용문[등용문]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a422


# [제30항 Norm 30]
#
# 사이시옷이 붙은 단어는 다음과 같이 발음한다.
# Words with ‘saisiot’ (intercalary ‘ㅅ’) are pronounced as follows.
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a423

# [제30항 1. Norm 30 Item 1]
#
# ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’으로 시작하는 단어 앞에 사이시옷이 올 때는 이들 자음만을 된소리로 발음하는 것을 원칙으로 하되, 사이시옷을 [ㄷ]으로 발음하는 것도 허용한다.
# When ‘saisiot’ comes before a word starting with ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’, the principle is to pronounce only these consonants as fortis sounds, but pronouncing ‘saisiot’ as [ㄷ] is also permitted.
#
#     냇가[내:까/낻:까]
#     샛길[새:낄/샏:낄]
#     빨랫돌[빨래똘/빨랟똘]
#     콧등[코뜽/콛뜽]
#     깃발[기빨/긷빨]
#     대팻밥[대패빱/대팯빱]
#     햇살[해쌀/핻쌀]
#     뱃속[배쏙/밷쏙]
#     뱃전[배쩐/밷쩐]
#     고갯짓[고개찓/고갣찓]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a423

# [제30항 2. Norm 30 Item 2]
#
# 사이시옷 뒤에 ‘ㄴ, ㅁ’이 결합되는 경우에는 [ㄴ]으로 발음한다.
# When ‘ㄴ, ㅁ’ are combined after ‘saisiot’, it is pronounced as [ㄴ].
#
#     콧날[콘날]
#     아랫니[아랜니]
#     뒷마루[뒨:마루]
#     뱃머리[밴머리]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a423

# [제30항 3. Norm 30 Item 3]
#
# 사이시옷 뒤에 ‘이’ 음이 결합되는 경우에는 [ㄴㄴ]으로 발음한다.
# When the sound ‘이’ is combined after ‘saisiot’, it is pronounced as [ㄴㄴ].
#
#     베갯잇[베갠닏]
#     깻잎[깬닙]
#     나뭇잎[나문닙]
#     도리깻열[도리깬녈]
#     뒷윷[뒨:뉼]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a423
def norm30(tokens: List[MorphToken], keep_saisiot: bool = False) -> List[MorphToken]:
    """
    제30항. 사이시옷이 붙는 단어의 발음을 처리합니다.

    1. 사이시옷 뒤에 "ㄱ, ㄷ, ㅂ, ㅅ, ㅈ"이 결합되는 경우에는 자음을 된소리로 발음합니다.
       (사이시옷을 [ㄷ]으로 발음하는 것도 허용)
    2. 사이시옷 뒤에 "ㄴ, ㅁ"이 결합되는 경우에는 [ㄴ]으로 발음합니다.
    3. 사이시옷 뒤에 '이' 소리가 결합되는 경우에는 [ㄴㄴ]으로 발음합니다.

    본 엔진은 표준국어대사전의 `compound_structure`(예: "나뭇-잎") 내부 경계와 형태소 분석기의 토큰 분리 결과를
    모두 활용하여 사이시옷 여부를 판단합니다.

    `keep_saisiot` 파라미터가 `False`일 경우 사이시옷의 발음(ㄷ)을 탈락시키고 뒤 자음의 변동만 취합니다.
    `True`일 경우 제30항 1호의 허용 조항에 따라 사이시옷을 'ㄷ'으로 유지합니다.

    Ref:
        zeroth genPhoneSeq.py
        — https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/buildLM/_scripts_/genPhoneSeq.py#L683-L699

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.
        keep_saisiot (bool): 사이시옷을 'ㄷ'으로 발음하여 남길지 여부. (기본값: False)

    Returns:
        List[MorphToken]: 사이시옷 규칙이 적용되어 자모가 치환되거나 탈락된 토큰 리스트.
    """
    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token.pos.startswith('S'):
            continue

        # 1. 단일 토큰 내부의 사이시옷 경계 처리 ("나뭇-잎"이 한 토큰일 경우)
        internal_boundaries = _get_internal_boundaries(getattr(curr_token, "compound_structure", ''))
        if internal_boundaries:
            jamo_list = list(curr_token.jamo_str)
            for bnd in internal_boundaries:
                j = bnd * 3
                if j >= len(jamo_list) or j == 0: continue

                prev_jong = jamo_list[j - 1]
                if prev_jong == C_SIOT:
                    next_cho = jamo_list[j]
                    next_joong = jamo_list[j + 1] if j + 1 < len(jamo_list) else ""

                    # 30.1 사이시옷 뒤에 'ㄱ, ㄷ, ㅂ, ㅅ, ㅈ' -> 된소리
                    if next_cho in FORTIS_MAPPING:
                        jamo_list[j] = FORTIS_MAPPING[next_cho]

                        # 사이시옷 처리 (탈락 vs ㄷ 유지)
                        jamo_list[j - 1] = C_DIGEUT if keep_saisiot else C_NONE

                    # 30.2 사이시옷 뒤에 'ㄴ, ㅁ' -> 사이시옷이 [ㄴ]으로 발음됨
                    elif next_cho in (O_NIEUN, O_MIEUM):
                        jamo_list[j - 1] = C_NIEUN

                    # 30.3 사이시옷 뒤에 '이' -> [ㄴㄴ]으로 발음됨
                    elif next_cho == O_IEUNG and next_joong == N_I:
                        jamo_list[j - 1] = C_NIEUN
                        jamo_list[j] = O_NIEUN

            curr_token.jamo_str = "".join(jamo_list)

        # 2. 토큰 간 경계 처리 (형태소 분석기가 '나뭇' + '잎' 등으로 쪼갠 경우)
        if i < len(tokens) - 1:
            curr_jong = curr_token.jamo_str[-1]
            if curr_jong == C_SIOT:
                next_token = tokens[i+1]
                if next_token.pos.startswith('S') or next_token.pos == 'SP':
                    continue

                # 복합어 환경이므로 보통 뒤 토큰은 명사(NNG 등)입니다.
                if next_token.pos.startswith(SUBSTANTIVE_TAGS):
                    next_cho = next_token.jamo_str[0]
                    next_joong = next_token.jamo_str[1] if len(next_token.jamo_str) >= 2 else ""

                    # 30.1 사이시옷 뒤에 'ㄱ, ㄷ, ㅂ, ㅅ, ㅈ' -> 된소리
                    if next_cho in FORTIS_MAPPING:
                        next_token.jamo_str = FORTIS_MAPPING[next_cho] + next_token.jamo_str[1:]

                        # 사이시옷 처리 (탈락 vs ㄷ 유지)
                        new_jong = C_DIGEUT if keep_saisiot else C_NONE
                        curr_token.jamo_str = curr_token.jamo_str[:-1] + new_jong

                    # 30.2 사이시옷 뒤에 'ㄴ, ㅁ' -> 사이시옷이 [ㄴ]으로 발음됨
                    elif next_cho in (O_NIEUN, O_MIEUM):
                        curr_token.jamo_str = curr_token.jamo_str[:-1] + C_NIEUN

                    # 30.3 사이시옷 뒤에 '이' -> [ㄴㄴ]으로 발음됨
                    elif next_cho == O_IEUNG and next_joong == N_I:
                        curr_token.jamo_str = curr_token.jamo_str[:-1] + C_NIEUN
                        next_token.jamo_str = O_NIEUN + next_token.jamo_str[1:]

    return tokens
