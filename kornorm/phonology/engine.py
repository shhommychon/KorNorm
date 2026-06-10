# [KorNorm 음운 변동 엔진 모듈]
#
# 정규식을 지양하고 O(1) 탐색 속도의 Arrow 사전과 2D LUT를 활용하는 하이브리드 음운 변동 엔진입니다.

import os
from typing import List, Literal

from kornorm.utils._patch_pecab import patch_pecab_dictionary_if_needed
from kornorm.utils.jamo import decompose, join_jamos, to_compat_jamo

from kornorm.phonology.common import MorphToken
from kornorm.phonology.apply_lut import apply_phonology_lut
from kornorm.phonology.chapter2 import (
    norm5_p1, norm5_p2, norm5_p3,
)
from kornorm.phonology.chapter4 import (
    norm10_p, norm11_p, norm12_1_c, norm12_1_a2, norm12_4, norm13, norm14, norm15, norm15_p, norm16,
)
from kornorm.phonology.chapter5 import (
    norm17, norm17_a, norm20_p,
)
from kornorm.phonology.chapter6 import (
    norm24, norm25, norm26, norm27, norm27_a,
)
from kornorm.phonology.chapter7 import (
    norm29, norm30,
)

global_phonology_engine = None

def worker_init():
    global global_phonology_engine
    if global_phonology_engine is None:
        global_phonology_engine = PhonologicProcessor()

def apply_phonology(text: str, output_format: str = "positional") -> str:
    global global_phonology_engine
    if global_phonology_engine is None:
        global_phonology_engine = PhonologicProcessor()
    return global_phonology_engine(text, output_format=output_format)


def apply_stdict_pronunciation(tokens: List[MorphToken]) -> List[MorphToken]:
    """
    표준국어대사전(stdict)의 발음 정보를 규칙 연산에 앞서 토큰에 선적용합니다.

    규칙만으로 도출할 수 없는 어휘적 발음(예: 대관령[대괄령] vs 동원령[동원녕], 공권력[공꿘녁],
    줄넘기[줄럼끼])을 사전 조회 한 번으로 확정합니다. g2pK의 idioms.txt식 하드코딩 목록을
    수만 어휘 규모의 DAT 사전 조회로 대체하는 본 엔진의 핵심 차별점입니다.

    단, 어말 종성은 표면형의 받침을 유지합니다. 사전 발음은 고립형(어말 중화 적용)이라 그대로
    치환하면 뒤 문맥과의 연음이 깨지기 때문입니다
    (예: 나뭇잎[나문닙] -> "나문닢"으로 복원해야 "나뭇잎이[나문니피]"가 성립).

    Args:
        tokens (List[MorphToken]): 형태소 분석 및 자모 분해가 완료된 토큰 리스트.

    Returns:
        List[MorphToken]: 사전 등재 발음이 자모에 반영된 토큰 리스트.
    """
    for token in tokens:
        if token.pos.startswith('S'):
            continue

        # 사전 표제어와 표면형이 온전히 일치하는 것은 사실상 체언·수식언·어근 계열이므로,
        # 어미·조사 등이 동형의 표제어와 우연히 충돌하는 것을 막는다 (예: 연결어미 '다가' vs 多價[다까]).
        if not token.pos.startswith(('N', 'M', "XR")):
            continue

        pron = token.pronunciation
        if not pron or pron == token.surface or len(pron) != len(token.surface):
            continue

        # 완성형 한글 이외의 문자가 섞인 발음 표기는 보수적으로 스킵
        if any(not ('가' <= ch <= '힣') for ch in pron):
            continue

        new_jamo = decompose(pron)
        token.jamo_str = new_jamo[:-1] + token.jamo_str[-1]
        # 사전 발음이 확정된 토큰임을 표시한다. 표기 기준 조항(제5항 다만 3 등)이
        # 발음 유래 자모를 재변형하지 않도록 하는 가드로 쓰인다 (예: 협의[혀븨] 유지).
        token.stdict_applied = True

    return tokens


class PhonologicProcessor:
    """
    KorNorm 메인 음운 변동 엔진

    본 프로세서는 한국어 음운 변동의 표준 모델을 지향하며, 국내 자연어 처리 분야의 준거 모델인
    g2pK 아키텍처 및 그 근간인 zeroth 프로젝트의 설계 철학을 계승하여 재구현되었습니다.

    만약 본 클래스의 정책을 변경하여 국립국어원의 다른 허용 조항이나 연음을 켜고 싶다면,
    본 클래스를 상속받아 `__call__` 파이프라인의 파라미터를 직접 오버라이딩하십시오.
    """

    def __init__(self):
        patch_pecab_dictionary_if_needed()

        import pecab
        self.tokenizer = pecab.PeCab()

        self.hanja_set = set()
        self.compound_set = set()

        self._load_stdict_arrow()
        self._load_2d_lut()

    def _load_stdict_arrow(self):
        """
        Arrow IPC를 로드하여 DoubleArrayTrie 구조로 복원합니다.

        PyArrow Native 구조를 유지하여 Zero-copy 로딩을 수행하며, 리스트 변환 과정을 생략하여 메모리 효율을 극대화합니다.
        """
        import pyarrow as pa
        from pecab._datrie import DoubleArrayTrie

        words_path = os.path.join(os.path.dirname(__file__), "_resources", "stdict_words.arrow")
        arrays_path = os.path.join(os.path.dirname(__file__), "_resources", "stdict_arrays.arrow")

        if os.path.exists(words_path) and os.path.exists(arrays_path):
            # 메모리 맵이 닫히지 않도록 인스턴스 변수로 유지하여 Zero-copy 참조를 보장
            self._source_w = pa.memory_map(words_path, 'r')
            self._source_a = pa.memory_map(arrays_path, 'r')
            
            words_table = pa.ipc.open_file(self._source_w).read_all()
            arrays_table = pa.ipc.open_file(self._source_a).read_all()

            # DoubleArrayTrie 객체 복원
            self.stdict_trie = DoubleArrayTrie({})

            # PyArrow Array 구조를 그대로 유지하여 메모리 복사를 방지
            # pecab 내부 로직의 .as_py() 호출과 호환됨
            self.stdict_trie._value = {
                col_name: words_table.column(col_name)
                for col_name in words_table.column_names
            }
            
            # pecab 내부 인터페이스에 맞게 value names 업데이트
            self.stdict_trie._value_names = tuple(words_table.column_names)

            # base/check 배열 또한 Native Array 상태로 유지
            self.stdict_trie._base = arrays_table.column("base")
            self.stdict_trie._check = arrays_table.column("check")

    def _load_2d_lut(self):
        """2D LUT를 메모리에 바인딩합니다."""
        from kornorm.phonology.apply_lut import PHONOLOGY_LUT
        self.lut = PHONOLOGY_LUT

    def _tokenize_and_tag(self, text: str) -> List[MorphToken]:
        """
        Pecab의 내부 API를 호출하여 토큰을 생성하고,
        표준국어대사전(stdict_trie)을 조회하여 한자어 여부 및 복합어 결합 구조를 주입합니다.
        """
        raw_output = self.tokenizer._tokenize(text)

        tokens = []
        for term, pos, offset in zip(
            raw_output["terms"],
            raw_output["pos_tags"],
            raw_output["offsets"]
        ):
            is_h = False
            comp_str = ''
            pron_str = ''

            # 사전 조회를 통한 메타데이터 확보
            if self.stdict_trie is not None:
                try:
                    dict_info = self.stdict_trie[term]
                    if isinstance(dict_info, dict):
                        is_h = (dict_info.get("is_hanja") == '1')
                        comp_str = dict_info.get("compound_structure", '')
                        pron_str = dict_info.get("pronunciation", '')
                except KeyError:
                    pass

            token = MorphToken(
                surface=term,
                pos=pos,
                start_offset=offset[0],
                end_offset=offset[1],
                jamo_str=decompose(term),
                is_hanja=is_h,
                compound_structure=comp_str,
                pronunciation=pron_str,
            )
            tokens.append(token)

        return tokens

    def __call__(
        self,
        text: str,
        output_format: Literal["positional", "compat", "hangul"] = "positional",
    ) -> str:
        """
        텍스트를 입력받아 표준발음법이 적용된 결과를 반환합니다.

        Args:
            text (str): 전처리가 완료된 원본 텍스트
            output_format (str):
                - "positional": (기본값) U+11xx 형태의 위치 기반 자모 분리 상태 (예: ᄆ​ᅥ​ᆨ)
                - "compat": U+313x 형태의 호환 자모 분리 상태 (예: ㅁ​ㅓ​ㄱ)
                - "hangul": 초중종성이 결합된 완성형 한글 (예: 먹)
        """
        tokens = self._tokenize_and_tag(text)

        # 0. 표준국어대사전 발음 선적용 (어휘적 발음 확정)
        tokens = apply_stdict_pronunciation(tokens)

        # 1. 한자어 처리
        tokens = norm20_p(tokens)
        tokens = norm26(tokens)

        # 2. 복합어/파생어 처리
        tokens = norm30(tokens, keep_saisiot=False) # 사이시옷의 발음(ㄷ)을 탈락시키고 뒤 자음의 변동만 취합
        tokens = norm29(tokens)

        # 3. 종성 규칙 선적용
        tokens = norm15(tokens)
        tokens = norm15_p(tokens)

        # 4. 표준 발음 규칙 적용
        tokens = norm5_p1(tokens)
        # 제5항 다만 2(ㅖ->ㅔ)도 허용 조항이나, 예사말에서 [ㅔ]가 압도적인 현실을 따라
        # 전사 관례로 채택한 의도적 예외이다 (계->[게], 단 '예·례'는 원칙대로 유지).
        tokens = norm5_p2(tokens)
        tokens = norm5_p3(tokens)
        # 제5항 다만 4(비어두 '의'->[이], 조사 '의'->[에])는 허용 조항이므로 기본 파이프라인에서는
        # 원칙형([의])을 유지한다. 허용형이 필요하면 본 클래스를 상속받아 chapter2의
        # norm5_p4_1/norm5_p4_2를 파이프라인에 추가하십시오.
        # 제22항 본항(어->여) 및 붙임(오->요)은 허용 조항이므로 기본 파이프라인에서는 원칙형을 유지한다.
        # 허용형이 필요하면 본 클래스를 상속받아 chapter5의 norm22/norm22_a를 파이프라인에 추가하십시오.

        tokens = norm10_p(tokens)
        tokens = norm11_p(tokens)
        tokens = norm16(tokens)

        tokens = norm24(tokens)
        tokens = norm25(tokens)
        tokens = norm27(tokens, ignore_space_as_pause=True) # 띄어쓰기에도 강건하게 변동 적용
        tokens = norm27_a(tokens)

        tokens = norm17(tokens)
        tokens = norm17_a(tokens)

        tokens = norm12_1_c(tokens)
        tokens = norm12_1_a2(tokens)

        # 5. 메인 O(1) 2D LUT 적용 (일반 자음 동화, 비음화, 유음화 등)
        # 공백(어절 경계)은 어말로 취급한다. 공백을 넘는 변동은 규칙별 전용 함수(norm15, norm12_1_a2, norm27 등)의 소관.
        tokens = apply_phonology_lut(tokens)

        # 6. 연음 및 탈락 적용
        tokens = norm13(tokens)
        tokens = norm14(tokens)
        tokens = norm12_4(tokens)

        # 출력 포맷팅
        result_chars = []
        for token in tokens:
            if token.pos == "SP":
                result_chars.append(token.surface)
            else:
                if output_format == "positional":
                    # C_NONE과 같은 플레이스홀더를 제거하여 순수 자모만 리턴
                    result_chars.append(token.jamo_str.replace('\u3164', ''))
                elif output_format == "compat":
                    result_chars.append(to_compat_jamo(token.jamo_str))
                elif output_format == "hangul":
                    jamo_len = len(token.jamo_str)
                    for i in range(0, jamo_len, 3):
                        cho = token.jamo_str[i]
                        joong = token.jamo_str[i+1]
                        jong = token.jamo_str[i+2]
                        result_chars.append(join_jamos(cho, joong, jong))
                else:
                    raise ValueError("output_format must be \"positional\", \"compat\", or \"hangul\"")

        return ''.join(result_chars)
