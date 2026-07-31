import unittest

import kornorm.asia.japanese as japanese
from kornorm.asia import read_japanese

try:
    import janome  # noqa: F401
    HAS_JANOME = True
except ImportError:
    HAS_JANOME = False


class TestJapanese(unittest.TestCase):
    def test_read_japanese_norm_examples(self):
        """외래어 표기법 일본어 표기 세칙의 공식 예시를 재현하는지 테스트"""
        self.assertEqual(read_japanese("サッポロ"), "삿포로")
        self.assertEqual(read_japanese("トットリ"), "돗토리")
        self.assertEqual(read_japanese("ヨッカイチ"), "욧카이치")
        self.assertEqual(read_japanese("とうきょう"), "도쿄")
        self.assertEqual(read_japanese("きょうと"), "교토")
        self.assertEqual(read_japanese("おおさか"), "오사카")
        self.assertEqual(read_japanese("きゅうしゅう"), "규슈")
        self.assertEqual(read_japanese("ヨコハマ"), "요코하마")
        self.assertEqual(read_japanese("ニイガタ"), "니가타")

    def test_read_japanese_long_vowels(self):
        """장모음 무표기(세칙 제2항)와 에이 유지 관용을 테스트"""
        self.assertEqual(read_japanese("ラーメン"), "라멘")
        self.assertEqual(read_japanese("ありがとう"), "아리가토")
        self.assertEqual(read_japanese("げいしゃ"), "게이샤")

    def test_read_japanese_loan_kana(self):
        """표4 외 외래 음 가나 조합(관용 확장)을 테스트"""
        self.assertEqual(read_japanese("ファイト"), "파이토")
        self.assertEqual(read_japanese("ウィキペディア"), "위키페디아")
        self.assertEqual(read_japanese("シェフとチェス"), "셰후토체스")

    def test_read_japanese_sokuon_edge(self):
        """촉음이 직전 음절 받침으로 붙고, 고아 촉음은 통과하는지 테스트"""
        self.assertEqual(read_japanese("あっ"), "앗")
        self.assertEqual(read_japanese("ッアン"), "ッ안")

    @unittest.skipUnless(HAS_JANOME, "janome 미설치 (pip install kornorm[ja])")
    def test_read_japanese_sentences(self):
        """janome 형태소 분석으로 한자 독음·조사 발음이 해결되는지 테스트"""
        self.assertEqual(read_japanese("私は東京へ行きます"), "와타시와토쿄에이키마스")
        self.assertEqual(read_japanese("時々ラーメンを食べる"), "도키도키라멘오타베루")
        self.assertEqual(read_japanese("日本語を勉強します"), "니혼고오벤쿄시마스")
        self.assertEqual(read_japanese("こんにちは"), "곤니치와")
        self.assertEqual(read_japanese("いすゞ自動車"), "이스즈지도샤")

    def test_read_japanese_mixed_korean(self):
        """한국어 문장 속 일본어 구간만 변환하는지 테스트"""
        self.assertEqual(read_japanese("오늘 ラーメン 먹었다"), "오늘 라멘 먹었다")

    @unittest.skipUnless(HAS_JANOME, "janome 미설치 (pip install kornorm[ja])")
    def test_read_japanese_lone_kanji(self):
        """한자만의 구간은 기본 통과, convert_lone_kanji로만 읽는지 테스트"""
        self.assertEqual(read_japanese("中國"), "中國")
        self.assertEqual(read_japanese("東京"), "東京")
        self.assertEqual(read_japanese("東京", convert_lone_kanji=True), "도쿄")

    def test_read_japanese_untouched(self):
        """일본어가 없는 텍스트는 원문을 유지하는지 테스트"""
        self.assertEqual(read_japanese("평범한 한국어 문장"), "평범한 한국어 문장")
        self.assertEqual(read_japanese("hello world 123"), "hello world 123")
        self.assertEqual(read_japanese(''), '')
        self.assertEqual(read_japanese("ー"), "ー")

    def test_read_japanese_fallback(self):
        """janome 미설치 폴백 — 가나만 변환하고 한자·조사 표기는 남는지 테스트"""
        original = japanese._load_janome
        japanese._load_janome = lambda: None
        try:
            self.assertEqual(read_japanese("サッポロ"), "삿포로")
            self.assertEqual(read_japanese("とうきょう"), "도쿄")
            # 반복 기호: 가나(ゝ·ゞ)는 직전 가나 (탁음) 복사로 전개
            self.assertEqual(read_japanese("こゝろ"), "고코로")
            self.assertEqual(read_japanese("いすゞ"), "이스즈")
            # 한자 반복 기호(々)는 폴백에서만 직전 한자 복사로 전개
            self.assertEqual(read_japanese("時々ラーメン"), "時時라멘")
            # 한자는 통과, 조사 발음(は->와)은 미반영 — 문서화된 폴백 한계
            self.assertEqual(read_japanese("私は東京へ行きます"), "私하東京헤行기마스")
        finally:
            japanese._load_janome = original


if __name__ == "__main__":
    unittest.main()
