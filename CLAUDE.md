# CLAUDE.md — KorNorm (고놈) 개발 가이드

Claude Code가 이 저장소에서 작업할 때 읽는 프로젝트 컨텍스트 문서입니다.

## 1. 프로젝트 개요

- **KorNorm(고놈)**: 한국어 TTS 전처리 라이브러리 — 텍스트 정규화(숫자·단위·기호·영문) + 표준발음법 기반 G2P(음운 변동) 엔진.
- 사용자가 2022~2023년 AI 음성합성 스타트업에서 만들었던 사내 도구(`myxi-text-preprocess`/`myxi-text-g2pX`)의 **클린룸 재설계**. 공개 코드(g2pK 계열 4종, TTS 클리너 16종+, pecab, python-jamo 등)를 참고하되 구조적으로 독립된 구현을 만든다. 참고용 서브모듈들은 조사 완료 후 전부 삭제됨(출처 목록은 README Credits 참조).
- 외부 의존성은 순수 파이썬 `pecab`+`pyarrow`뿐 (C-MeCab 배제). 어휘 지식은 표준국어대사전(stdict)을 Arrow/DAT로 컴파일해 O(1) 조회. 영단어 발음용 cmudict는 첫 실행 시 자가 다운로드(nltk 불사용).
- g2pK 대비 차별점: ① idioms.txt식 하드코딩 예외 목록 대신 **stdict 발음 선적용 패스**, ② 전역 스위치 대신 **규칙별 공백(어절 경계) 정책** + **어절 결속도**(POS 쌍 기반, 18항 붙임·29항 붙임2), ③ 형태소 태그 기반 형식/실질 형태소 구분(낮 한때[나탄때] 등 g2pK 레거시 버그 해결).

## 2. 자주 쓰는 명령

```bash
# 음운 엔진 전체 테스트 (전 배터리 154 tests 중 111개, 전부 green — §6 참조)
venv/bin/python -m unittest discover -s test -p "test_phone*.py"

# 단일 규칙 스위트
venv/bin/python -m unittest test.test_phone_norm18

# 정규화(alphanumeric/heuristics) 테스트
venv/bin/python -m unittest discover -s test -p "test_alnum*.py"

# 통합 엔트리포인트(dealers_choice→음운) 테스트
venv/bin/python -m unittest test.test_normalize
```

- 테스트 폴더명은 `test` (`tests` 아님 — 의도적 결정).
- 엔진 초기화(pecab+Arrow 로드)에 수 초가 걸리므로 스위트 단위 실행을 선호.

## 3. 저장소 구조

- `kornorm/phonology/` — 표준발음법 엔진 (핵심).
  - `engine.py`: `PhonologicProcessor` — 파이프라인 조립. `apply_stdict_pronunciation`(step 0, 사전 발음 선적용)도 여기.
  - `chapter1.py`~`chapter7.py`: 표준발음법 장별 규칙 함수 (`normN`, 다만=`_p`(proviso), 붙임=`_a`(addendum), 해설=`_c`(commentary)).
  - `apply_lut.py`: 종성×초성 2D LUT (`PHONOLOGY_LUT`, 셀 = `(새 종성, 새 초성, rule_id)`). 공백 앞 종성은 어말(EOW) 대표음화만 — 공백을 넘는 변동은 규칙별 전용 함수 소관.
  - `common.py`: `MorphToken`, `FORTIS_MAPPING`, `_is_functional`(형식 형태소 판별 + pecab 오태깅 보정), `_ends_with_functional`, `_is_cohesive_boundary`/`_is_tight_cohesive_boundary`(어절 결속도).
  - `homographs.py`: 문맥 의존 동형어 판별 (`CONTEXT_HOMOGRAPHS` 단서 다수결 — 잠자리류).
  - `_resources/`: stdict Arrow 바이너리 (`is_hanja`/`pronunciation`/`compound_structure`).
- `kornorm/alphanumeric/` — 숫자·단위·통화·영문 정규화. `preset.dealers_choice` 14단계 프리셋. `english.py`(CMU dict → 외래어 표기법 변환), `_fetch_cmudict.py`(첫 실행 자가 다운로드).
- `kornorm/heuristics/` — 반복 열화 축약(`repetition.py`), 기호 제거(`eraser.py`).
- `kornorm/pipeline.py` — Stream/Batch 파이프라인 (순수 함수 조립). `kornorm/preset.py` — `normalize`(dealers_choice→apply_phonology 통합 엔트리포인트).
- `kornorm/utils/jamo.py` — U+11xx 위치 기반 자모 상수(`O_*`/`N_*`/`C_*`)·분해·조합. `_patch_pecab.py` — pecab 사전 lazy 패처(`PATCH_REVISION` 마커, 제외·추가·코스트 보정).
- `test/` — 규칙별 테스트. `test_phone_normN.py`는 직전 파일과 완전 동일 형식(헬퍼 5종 verbatim, 본항/다만/붙임별 words+sentences).
- `pyproject.toml`·`PYPI.md` — 0.0.0a1 패키징(버전 단일 소스는 `kornorm.__version__`, PyPI readme는 PYPI.md, 저장소 README는 이미지 포함 영문판).
- `.dev_phonology/` — stdict Arrow 빌더(`build_stdict_arrow.py`, -f로 추적)·LUT 빌더·pecab 사전 분석 노트북 (디렉토리 자체는 gitignore).

## 4. 엔진 아키텍처 요지

파이프라인 순서 (`PhonologicProcessor.__call__`): 토큰화(수사 낱자 병합 `_merge_numeral_headwords` 포함) → **stdict 발음 선적용**(+문맥 동형어 훅) → 한자어(20_p·26·26_c) → 첨가·사이시옷(30·29) → 절음(15·15_p) → 모음(5_p1~p3) → 대표음(10_p·11_p·16) → 경음화(24·25·27·27_a) → 구개음화(17·17_a) → ㅎ 격음화(12_1_c·12_1_a2) → **결속 경계 비음화(18_a)** → **LUT** → 연음(13·14·12_4).

- **허용 조항 정책**: 기본 파이프라인은 원칙형만. 허용형은 서브클래싱으로 활성화 — 22항(어→여), 5항 다만4('의'→이/에)가 이 정책으로 제외됨. 의도적 예외: 5항 다만2(ㅖ→ㅔ)는 전사 관례로 채택.
- **stdict 선적용 패스**: POS N·M·XR·V* 한정(어미 '다가' vs 多價 충돌 방지), 어말 종성은 표면형 복원(연음 보존), 발음==표기는 치환 스킵하되 norm29가 "표기대로"의 적극 정보로 활용(등용문). 치환 시 `stdict_applied` 마커 — 표기 기준 조항(5_p3)이 발음 유래 자모(협의[혀븨])를 재변형하지 못하게 가드. 용언은 어간+'다' 표제어 폴백 조회(발음 말음절 절단; `_NORM15_PROVISO_LEMMAS` 맛있다/멋있다는 15항 다만에 양보, 명사 동형어 오염 차단 위해 직접 히트 발음은 폐기).
- **어절 결속도**: "두 단어를 한 마디로 발음하는 경우"를 POS 쌍으로 판정. 29항 붙임2 = 맨체언+용언/관형사·수사+체언/관형사형 어미+체언/부사+용언(한 일[한 닐], 옷 입다[온 닙따]), 18항 붙임 = 맨명사+용언만(밥 먹는다[밤 멍는다]; 수사+단위명사 "여덟 명" 보호). 순서 필수: norm29(ㄴ첨가) → norm18_a. 조사·어미로 끝난 어절 뒤는 미발동(norm15도 `_ends_with_functional` 게이트로 "할수록 어려울" 절음 과발동 차단). norm29 공백 ㄴ첨가는 삽입 지점에서 LUT "18항" 셀로 비음화 연쇄를 즉시 완결(못 이겨[몬 니겨]).
- pecab 태깅 이상은 개별 하드코딩이 아니라 **공용 가드**(`_is_functional`, 27항 합성명사 조각 가드)나 **pecab 사전 패치 채널**로 대응. 어휘 예외 튜플 하드코딩 금지 — 단, 규범이 직접 열거한 폐쇄 문법 목록(예: 27항 붙임 `_RIEUL_ENDING_REMAINDERS`)은 허용.

## 5. 작업 이력 (완료 순서 — 날짜는 git log 참조)

1. 프로젝트 셋업: 참고 서브모듈 일괄 추가, 기본 라이브러리 구조.
2. 참고 코드 전수조사: TTS 클리너 16종·g2pK 계열·과거 사내 도구의 특수문자/숫자/단위 처리 로직 수집 (산출물은 `temp/` 계열에 격리).
3. 실행 계층: `StreamPipeline`/`BatchPipeline`(멀티프로세싱 pickle 제약 때문에 전처리 함수는 톱레벨 순수 함수), heuristics(`fix_text_degeneration` 반복 열화 축약, `eraser` 기호 제거).
4. `alphanumeric` 패키지: "모든 단계 일괄 통과" 초안을 해체하고 전부 개별 함수로 재설계 + `dealers_choice` 12단계 프리셋. datrie 미사용(순수 Python+정규식) 결정.
5. 음운 엔진 기반 공사: pecab 사전 자동 패칭(`_patch_pecab.py` — 고정밀 G2P 평가로 발음 오류 타겟 944개 검출), U+11xx 위치 기반 자모 유틸(초/종성 혼동 방지), 표준국어대사전 Arrow 컴파일.
6. 음운 엔진 구현: `chapter1~7` + 2D LUT + `PhonologicProcessor` 조립. 이후 대형 버그픽스(MorphToken을 common.py로 이동해 순환 임포트 해소, LUT 토큰 내부 음절 경계 순회 지원 등).
7. 규칙별 정밀 리뷰 1차: 5항('의' 처리), LUT를 훈민정음 자음 순서로 재배열 + g2pK 원본 `table.csv`의 정규식 버그·오타·누락 문서화, 9·10·11항(넓/밟 intra-token 스캔, g2pK 정규식 오타 저격 문장).
8. 12항(받침 ㅎ): 형식/실질 형태소 경계 문제(꽂히다[꼬치다] vs 낮 한때[나탄때]) 규명 — LUT 해체 대신 **LUT 직전 핀셋 예외 함수 선적용** 구조 확립(`norm12_1_a1/a2/c`), `norm12_4`에 ㅎ 탈락+연음 내장.
9. 13·14·15항: intra-token 연음, '있' 절음 특례, 절음 대상 모음 목록 확장, **`cross_word_boundary` 전역 스위치 폐기**(공백=어말 원칙 + 공백 통과는 규칙별 전용 함수 소관).
10. stdict 발음 선적용 패스 도입(20항 라운드): idioms식 하드코딩 대체. 이후 21항(문법[문뻡])·26항·28항(사잇소리)·29항(ㄴ첨가 어휘)·30항(사이시옷)의 실질 해결책이 됨.
11. 16~30항 리뷰 완주: 16(자모 이름), 17(구개음화), 18·19(비음화), 20(유음화+다만), 21(과동화 금지), 22(허용 조항 제외 정책 확립), 23~27(경음화; 27항 ETM 복합 태그 대응), 28(사잇소리), 29(ㄴ첨가, 무공백 원칙), 30(사이시옷). 규범 예시 전수 커버 대조까지 완료.
12. 마무리 라운드: expected 전사 오기 전수 정정, '의' 원칙형 정책 확립(`stdict_applied` 가드 포함), **어절 결속도 구현**으로 18항 붙임·29항 붙임2 해소.
13. develop 병합: 정규화 계열(`feature/cleaner`)과 음운 엔진 계열(`feature/better-g2pK`) 통합.
14. 0.0.0a1 준비 라운드(Phase 1~9): 기지 실패 9건 전소탕 — pecab 패치 채널 확장(`PATCH_REVISION`·코스트 보정·엔트리 추가), 용언 '-다' 폴백, stdict Arrow 빌더 재작성+재컴파일(물질 동형어·입원료), dealers_choice 재정렬(단위→소수점). 신규 기능 — 영단어 발음(`english.py`+cmudict 자가 다운로드), 통합 `normalize`(+가운뎃점 낱자·수사 병합), 문맥 동형어(잠자리)·"-증" 경음화(norm26_c), norm15 절음 게이트·norm29 공백 첨가 연쇄 완결.
15. 참고 서브모듈 전체 삭제 + 패키징: pyproject.toml·PYPI.md 신설, 공개 API export(`__version__`·`dealers_choice`·`apply_phonology`·`PhonologicProcessor`·heuristics), README 영문 개편(캐릭터 이미지 활용).

## 6. 현재 상태 (develop 기준)

- **전 배터리 154 tests green, 기지 실패 0** (음운 111 + alnum 27 + 유틸·통합 16). 신설 스위트: `test_normalize`(통합)·`test_phone_homograph`·`test_alnum_english`.
- 패키징 파일 완비(pyproject.toml·PYPI.md), PyPI 업로드는 미실행.

## 7. 남은 작업 (우선순위 순)

1. **PyPI 업로드**: TestPyPI 선행 권장. 계정·토큰은 사용자 소관.
2. **read-only 환경 대응**: 첫 실행 pecab 패치·cmudict 다운로드가 site-packages 쓰기 필요(Docker PermissionError). OS 캐시 리다이렉션안은 기각됨 — 현재는 문서로 한계 명시.
3. **미착수 기능(초기 기획분)**: 이메일·URL 한국어화, 띄어쓰기 보정, 어미 통일("밥먹어요"→"밥먹으세요").
4. **관찰된 미세 결함 후보**: "3400mAh"→"삼천사백마"(mAh 단위 미등재), "1연대는"→[일연대는](조사 결합형에서 ㄴ첨가 미발동 — 단독형 "1연대"는 [일련대]로 정상).
5. **엔진 개선 후보**: 연속 음운변동 시 규칙 롤백/규칙 간 충돌 방지 일반화(현재는 norm29→LUT 셀 연쇄 완결 등 국소 해법).
6. **확인 대기**: chapter5.py 주석 의심 2곳 — 20항 (2) "핥는지"(규범 원문 할는지?), 다만 "이뷘뇨"([이붠뇨]?). 다만 "상견네" 주석도 미수정(테스트는 [상견녜] 반영됨).

## 8. 컨벤션과 작업 관례

**코드 컨벤션**:
- **String Quote 규칙 (강박적으로 준수)**: 빈 문자열·단일 문자는 `'` (`''`, `'ㄱ'`), 2자 이상은 `"` ("KorNorm").
- 파일 최상단 `[KorNorm {요약} 모듈]` 주석. 독스트링은 한국어, `Args:`/`Returns:` 형식(타입 괄호, 마침표로 끝). Type hint 필수.
- 파일 이름 변경은 `mv` (rm 후 재작성 금지). 리서치 산출물은 `temp/` 등에 격리, 커밋 금지.

**작업 관례**:
- **테스트 형식**: 새 `test_phone_normN.py`는 직전 파일 형식을 그대로 복사. diff 부호는 `-`=엔진 실제 출력, `+`=기대값. `[DIFF_LOG]` 블록은 g2pK와의 참고 비교(log_only)라 실패가 아님.
- **전사 관례**: 장음 무표기, 공백 보존(밭 아래→"바 다래"), ㅖ→ㅔ 채택(계→게, 녜는 유지), 관형격 '의'는 원칙형 유지(그의). 결속 경계는 공백 너머 변동을 전사에 반영(한 일→"한 닐").
- **테스트 문장 작문 시 회피**: 받침+조사 '의'(연음 ㄹ+ㅢ 전사 불확정), 받침+공백+ㅏㅓㅗㅜㅟ류 시작 실질 형태소(norm15 절음), 2음절 한자어 경음화(norm26 미커버), "결국"류 부사성 맨명사+용언(결속도 게이트 충돌). 평파열음+ㅅ 전사 주의(접시[접씨]).
