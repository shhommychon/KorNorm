# [KorNorm 표준국어대사전 Arrow 빌더]
#
# 국립국어원 표준국어대사전 수출본(1538127_*.xls, 어휘 전수 437k행)을 읽어
# kornorm/phonology/_resources/의 stdict_words.arrow / stdict_arrays.arrow 를 생성합니다.
#
# ※ 최초 빌드는 pecab의 _convert_to_arrow.py를 즉석에서 변형해 썼던 것으로 보여 전용
#   스크립트가 남아 있지 않았고, 구 arrow(288,615 표제어)와의 전수 등가성 검증
#   (--legacy 빌드 == 구 arrow, diff 0)을 거쳐 다음 규칙을 복원해 재작성했습니다:
#   - 구성 단위가 '단어'인 행만 사용 (구·관용구·속담 제외)
#   - 어휘 표기의 동형어 번호 "(NN)" 제거, 결합 경계 '-'와 가운뎃점 '·'은
#     compound_structure에 '-'로 보존, 표면형에서는 제거
#   - 표면형에 현대 한글 음절(가-힣)·호환 자모(ㄱ-ㅣ) 이외 문자가 남으면 드롭 (PUA 등 5건)
#   - compound_structure의 선행 '-'(어미·접사 표기)는 제거하되 후행 '-'는 보존 ("-으오-" -> "으오-")
#   - 발음은 대괄호 제거, 복수 표기(/)는 첫 형태(원칙형) 채택, 장음 기호(ː·:) 제거
#   - is_hanja는 고유어 여부가 "한자어"이거나, 원어·어종 필드에 어종이 "한자"로 라벨된
#     부분이 있으면 "1" (된醬+잠자리 "1", appeal+하다 "0", 쓰시마섬 Tsushima[對馬]는 어종 "안 밝힘"이라 "0")
#
# 사용법:
#   venv/bin/python .dev_phonology/build_stdict_arrow.py --out <dir>
#   venv/bin/python .dev_phonology/build_stdict_arrow.py --out <dir> --legacy   # 구 arrow 재현(등가성 검증용)

import argparse
import glob
import os
import re
from typing import Dict

import xlrd
import pyarrow as pa
from pecab._datrie import DoubleArrayTrie

DUMP_GLOB = os.path.join(os.path.dirname(__file__), "1538127_*.xls")
VALUE_COLUMNS = ("is_hanja", "pronunciation", "compound_structure")

# 수출본에 누락된 표준국어대사전 실존 표제어의 보충 목록.
# 사전에 실려 있는 규범 어휘만 담을 수 있으며, 근거(사전 표기·발음)를 반드시 병기한다.
#   - 입원-료(入院料) [이붠뇨]: 표준 발음법 제20항 다만의 규범 예시. 수출본에는 부재.
SUPPLEMENTS = {
    "입원료": {
        "is_hanja": '1',
        "pronunciation": "이붠뇨",
        "compound_structure": "입원-료",
    },
}

# 동형어 우선순위 수동 지정 목록: {표면형: 채택할 발음}.
# 기본 정책은 수출본 수록 순서의 첫 표제어 채택이며, 그 결과가 주된 독법과 다르다고
# 검증된 표면형만 여기에 담는다. 근거를 반드시 병기한다.
#
# ※ "발음이 표기와 다른 동형어 우선" 같은 일반 정책은 기각되었다. 전수 시뮬레이션 결과
#   589개 표면형이 뒤집히는데, 개선(관점[관쩜], 개수[개쑤])과 함께 최빈 독법의 역전
#   (경기(競技)[경기]->[경끼], 강조(強調)[강조]->[강쪼], 경과(經過)[경과]->[경꽈])이
#   다수 섞여 있어 무차별 적용이 불가능하다.
#   - 물질: 고유어 물-질(01)[물질](해녀의 무자맥질)보다 物質(02)[물찔]이 압도적 주 독법.
HOMOGRAPH_PREFERENCES = {
    "물질": "물찔",
}


def _clean_pronunciation(raw: str) -> str:
    """
    수출본 발음 표기를 arrow 저장 형식으로 정돈합니다.

    Args:
        raw (str): 수출본 '발음' 셀 원문 (예: "[물찔계/물찔게]").

    Returns:
        str: 대괄호·장음 기호를 제거하고 첫 형태(원칙형)만 남긴 발음 문자열.
    """
    pron = str(raw).strip().strip("[]")
    pron = pron.split('/')[0]
    return pron.replace('ː', '').replace(':', '')


def _has_hanja_part(origin_kinds: str) -> bool:
    """
    수출본 '원어·어종' 필드에 어종이 "한자"인 부분이 있는지 검사합니다.

    Args:
        origin_kinds (str): 수출본 '원어·어종' 셀 원문 (줄 단위 "{어종} {원어}" 나열.
            예: 된장잠자리의 "고유어 된 / 한자 醬 / 고유어 잠자리").

    Returns:
        bool: "한자"로 라벨된 부분이 하나라도 있으면 True.
    """
    return any(
        line.startswith("한자 ") for line in str(origin_kinds).splitlines()
    )


def _is_valid_surface(surface: str) -> bool:
    """
    표면형이 현대 한글 음절·호환 자모만으로 이루어졌는지 검사합니다.

    Args:
        surface (str): 정규화가 끝난 표면형.

    Returns:
        bool: 등재 가능하면 True. (빈 문자열·PUA 등 이외 문자 포함 시 False.)
    """
    if not surface:
        return False
    return all(('가' <= ch <= '힣') or ('ㄱ' <= ch <= 'ㅣ') for ch in surface)


def read_dump_entries() -> Dict[str, list]:
    """
    수출본 전체를 사전 순으로 읽어 표면형별 표제어 후보 리스트를 만듭니다.

    Returns:
        Dict[str, list]: {표면형: [값 딕셔너리, ...]} — 리스트는 사전 수록 순서를 유지합니다.
    """
    files = sorted(
        glob.glob(DUMP_GLOB),
        key=lambda f: int(re.search(r"_(\d+)\.xls$", f).group(1)),
    )
    if not files:
        raise FileNotFoundError(f"수출본을 찾을 수 없습니다: {DUMP_GLOB}")

    entries: Dict[str, list] = {}
    for f in files:
        book = xlrd.open_workbook(f)
        sheet = book.sheet_by_index(0)
        for r in range(1, sheet.nrows):
            if sheet.cell_value(r, 1) != "단어":
                continue

            raw_word = str(sheet.cell_value(r, 0))
            no_number = re.sub(r"\(\d+\)", '', raw_word)
            compound = no_number.replace('·', '-').replace('^', '-').lstrip('-')
            surface = compound.replace('-', '')
            if not _is_valid_surface(surface):
                continue

            # '천억'처럼 원어·어종이 공란인 데이터 갭은 고유어 여부 분류('한자어')로 보완한다.
            is_hanja = (
                sheet.cell_value(r, 2) == "한자어"
                or _has_hanja_part(sheet.cell_value(r, 4))
            )
            value = {
                "is_hanja": '1' if is_hanja else '0',
                "pronunciation": _clean_pronunciation(sheet.cell_value(r, 8)),
                "compound_structure": compound,
            }
            entries.setdefault(surface, []).append(value)
    return entries


def select_homograph(surface: str, candidates: list, use_preferences: bool) -> dict:
    """
    같은 표면형의 동형어 후보 중 arrow에 실을 하나를 고릅니다.

    Args:
        surface (str): 표면형.
        candidates (list): 사전 수록 순서의 값 딕셔너리 리스트.
        use_preferences (bool): True면 HOMOGRAPH_PREFERENCES에 지정된 발음의 후보를
            우선 채택하고, 그 외에는 첫 표제어(수록 순서)를 따른다.

    Returns:
        dict: 채택된 값 딕셔너리.
    """
    if use_preferences and surface in HOMOGRAPH_PREFERENCES:
        preferred = HOMOGRAPH_PREFERENCES[surface]
        for cand in candidates:
            if cand["pronunciation"] == preferred:
                return cand
    return candidates[0]


def build(out_dir: str, legacy: bool):
    """
    Arrow 파일 두 개(words/arrays)를 생성합니다.

    DAT 빌드와 Arrow IPC 직렬화 구조는 pecab이 자체 사전을 빌드하는 방식을 그대로 따릅니다.

    Ref:
        pecab _resources/_convert_to_arrow.py (DoubleArrayTrie 빌드·words/arrays 직렬화 패턴)
        — https://github.com/hyunwoongko/pecab/blob/main/pecab/_resources/_convert_to_arrow.py

    Args:
        out_dir (str): 산출물 디렉토리.
        legacy (bool): True면 우선순위·보충 없이 구 arrow를 그대로 재현한다 (등가성 검증용).
    """
    entries = read_dump_entries()
    data = {
        surface: select_homograph(surface, cands, use_preferences=not legacy)
        for surface, cands in entries.items()
    }

    if not legacy:
        for surface, value in SUPPLEMENTS.items():
            if surface not in data:
                data[surface] = dict(value)

    print(f"표제어 {len(data)}개로 DAT를 빌드합니다 (legacy={legacy}) ...")
    trie = DoubleArrayTrie(data)

    words_table = pa.Table.from_pydict({
        col: [row[col] for row in trie._value] for col in VALUE_COLUMNS
    })
    arrays_table = pa.Table.from_pydict({"base": trie._base, "check": trie._check})

    os.makedirs(out_dir, exist_ok=True)
    for fname, table in (("stdict_words.arrow", words_table), ("stdict_arrays.arrow", arrays_table)):
        path = os.path.join(out_dir, fname)
        with pa.OSFile(path, "wb") as sink:
            with pa.RecordBatchFileWriter(sink, table.schema) as writer:
                writer.write_table(table)
        print("생성:", path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="표준국어대사전 Arrow 빌더")
    parser.add_argument("--out", required=True, help="산출물 디렉토리")
    parser.add_argument("--legacy", action="store_true", help="우선순위·보충 없이 구 arrow 재현 (등가성 검증용)")
    args = parser.parse_args()
    build(args.out, legacy=args.legacy)
