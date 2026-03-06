# [국립국어원 한국어 어문 규범 표준어규정 제2부 표준발음법 제1장 총칙]
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a387


# [제1항 Norm 1]
#
# 표준 발음법은 표준어의 실제 발음을 따르되, 국어의 전통성과 합리성을 고려하여 정함을 원칙으로 한다.
# Standard pronunciation rules shall follow the actual pronunciation of standard Korean,
# while being determined by considering the tradition and rationality of the Korean language.
#
# Ref:
#   https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0002&regltn_no=346#a394


# ======================================================================
# 유의 사항: `KorNorm/phonology` 모듈의 한계
# DISCLAIMER: Limitations of the `KorNorm/phonology` Module
# ======================================================================
#
# `KorNorm/phonology` 모듈은 국립국어원의 한국어 어문 규범을 바탕으로 표준 발음법에
# 따른 음운 변동을 프로그래밍적으로 구현한 것입니다.
# The `KorNorm/phonology` module is a programmatic implementation of
# phonological changes based on the Standard Pronunciation Rules of the
# National Institute of the Korean Language.
#
# 사용자는 본 모듈의 다음과 같은 기술적 한계 사항을 유의해야 합니다.
# Users should be aware of the technical limitations of this module.
#
# 1. 복수 표준 발음의 허용 Allowance of Multiple Standard Pronunciations:
#
#    표준 발음법은 하나의 단어에 대해 두 가지 이상의 발음을 허용하는 경우가 많습니다.
#    The Standard Pronunciation Rules often permit more than one
#    pronunciation for a single word.
#
#    본 패키지의 메소드들은 이러한 경우 특정 발음을 선택하여 구현한 사례가 많으므로,
#    사용자의 목적에 따라 취사선택하여 활용하시기 바랍니다.
#    Since the methods in this package often implement a specific choice
#    among these variations, users are encouraged to select and utilize
#    them according to their specific needs.
#
# 2. 방언 및 지역적 변이 Dialectal and Regional Variations:
#
#    본 패키지는 서울말을 기반으로 하는 표준어 발음에 국한됩니다.
#    This package is limited to standard pronunciation based on the Seoul
#    dialect.
#
#    지역별 방언, 사회적 변이, 또는 구어체에서 나타나는 자연스러운 운율 등은
#    고려 대상에서 제외되었습니다.
#    Regional dialects, social variations, and the natural prosody of
#    colloquial speech have been excluded from consideration.
#
# 3. 실제 언어 관습과 규범의 간극 Gap Between Actual Linguistic Habits and Norms:
#
#    언어는 빠르게 변화하며, 실제 언어 생활이 반드시 표준 발음법과 일치하지는 않습니다.
#    Language evolves rapidly, and actual linguistic usage does not always
#    align with the Standard Pronunciation Rules.
#
#    따라서 본 모듈이 처리한 결과물은 비표준인 현실 발음과 차이가 있을 수 있음에
#    유의해야 합니다 (예: 음성 인식 결과를 본 모듈로 처리하는 경우 등).
#    Therefore, users should note that the output processed by this module
#    may differ from non-standard realistic pronunciations (e.g., when
#    processing the results of speech recognition).
#
# 본 도구는 공식 언어 규범을 규칙 기반으로 구현한 파이썬 라이브러리이며, 별도의 기계학습
# 모델 없이 결정론적으로 텍스트를 처리하는 것을 지향합니다.
# This tool is a rule-based Python library that implements official
# linguistic norms and aims to process text deterministically without
# the use of machine learning models.
#
# 사용 시 이러한 모듈의 방향성을 충분히 감안해 주시기 바랍니다.
# Please take this direction into full account when using the library.
# ======================================================================
