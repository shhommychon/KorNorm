# [KorNorm CMU 발음 사전 확보 모듈]
#
# 영어 단어 발음 변환에 쓰는 CMU 발음 사전(cmudict)을 최초 실행 시 1회 내려받아
# 패키지 리소스로 자가 설치합니다. `_patch_pecab`의 1회성 패치 방식과 동일한 구조로,
# 파일이 이미 있으면 즉시 통과하여 로딩 속도에 영향을 주지 않습니다.
#
# cmudict는 카네기 멜런 대학교가 공개한 영어 발음 사전(BSD 계열 라이선스)입니다.
#
# Ref:
#     cmusphinx/cmudict
#     — https://github.com/cmusphinx/cmudict

import os
import urllib.request
from pathlib import Path
from typing import Optional

CMUDICT_URL = "https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict"

_RESOURCE_DIR = os.path.join(os.path.dirname(__file__), "_resources")
CMUDICT_PATH = os.path.join(_RESOURCE_DIR, "cmudict.dict")


def fetch_cmudict_if_needed() -> Optional[str]:
    """
    CMU 발음 사전 파일을 확보하고 경로를 반환합니다.

    파일이 없으면 최초 1회 내려받아 패키지 `_resources/`에 저장합니다.
    네트워크 불가 등으로 확보에 실패하면 안내를 출력하고 None을 반환합니다
    (호출 측은 영어 단어 발음 변환을 건너뜁니다).

    Returns:
        Optional[str]: 사전 파일 경로. 확보 실패 시 None.
    """
    if os.path.exists(CMUDICT_PATH):
        return CMUDICT_PATH

    print("KorNorm: 최초 실행을 감지했습니다. CMU 발음 사전을 내려받습니다...")
    partial_path = CMUDICT_PATH + ".part"
    try:
        os.makedirs(_RESOURCE_DIR, exist_ok=True)
        urllib.request.urlretrieve(CMUDICT_URL, partial_path)
        # 부분 다운로드 파일이 사전으로 오인되지 않도록 완료 후에만 제자리로 옮긴다
        os.replace(partial_path, CMUDICT_PATH)
    except Exception as e:
        if os.path.exists(partial_path):
            os.remove(partial_path)
        print(f"KorNorm: CMU 발음 사전 다운로드 실패 — 영어 단어 발음 변환을 건너뜁니다. ({e})")
        return None

    # pip uninstall 시 함께 삭제되도록 kornorm의 RECORD 파일 수정
    # (저장소 체크아웃처럼 dist-info가 없는 환경에서는 자연히 건너뛴다)
    try:
        package_root = Path(__file__).parent.parent
        site_packages_dir = package_root.parent

        for dist_info in site_packages_dir.glob("kornorm-*.dist-info"):
            record_path = dist_info / "RECORD"
            if record_path.exists():
                relative_path = "kornorm/alphanumeric/_resources/cmudict.dict"
                with open(record_path, 'r', encoding="utf-8") as f:
                    already_recorded = relative_path in f.read()
                if not already_recorded:
                    with open(record_path, 'a', encoding="utf-8", newline='') as f:
                        f.write(f"{relative_path},,\n")
                break
    except Exception as e:
        print(f"KorNorm: kornorm RECORD 파일 업데이트 실패 (무시됨) - {e}")

    print("KorNorm: CMU 발음 사전 준비를 완료했습니다.")
    return CMUDICT_PATH
