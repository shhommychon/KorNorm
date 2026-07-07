import unittest
from kornorm.alphanumeric.english import read_english_words
from kornorm.alphanumeric.preset import dealers_choice

class TestEnglish(unittest.TestCase):
    def test_read_english_words(self):
        """CMU 사전 등재 영어 단어를 한글 표기로 변환하는지 테스트"""
        self.assertEqual(read_english_words("그 사람 좀 old school이야"), "그 사람 좀 올드 스쿨이야")
        self.assertEqual(read_english_words("오늘 game을 했다"), "오늘 게임을 했다")
        self.assertEqual(read_english_words("brand 가치"), "브랜드 가치")

    def test_read_english_words_glides(self):
        """반모음(Y·W)이 뒤 모음과 합쳐지는지 테스트 (g2pK의 [컴프유터] 오표기 교정)"""
        self.assertEqual(read_english_words("computer"), "컴퓨터")
        self.assertEqual(read_english_words("quick"), "퀵")
        self.assertEqual(read_english_words("beauty"), "뷰티")
        self.assertEqual(read_english_words("twist"), "트위스트")
        self.assertEqual(read_english_words("value"), "밸류")

    def test_read_english_words_untouched(self):
        """사전 미등재 단어와 한 글자 단어는 원문을 유지하는지 테스트"""
        self.assertEqual(read_english_words("qwerty 자판"), "qwerty 자판")
        self.assertEqual(read_english_words("a 등급"), "a 등급")

    def test_read_english_words_modern_entries(self):
        """cmusphinx 최신 배포본의 신조어 표제어가 조회되는지 테스트"""
        self.assertEqual(read_english_words("smartphone 시대"), "스마트폰 시대")

    def test_dealers_choice_english(self):
        """프리셋에서 영어 단어 변환과 낱자 읽기가 분업하는지 테스트"""
        self.assertEqual(dealers_choice("그 사람 좀 old school이야"), "그 사람 좀 올드 스쿨이야")
        # 미등재 단어(txt)는 낱자 읽기로 넘어간다
        self.assertEqual(dealers_choice("txt 파일"), "티엑스티 파일")

if __name__ == "__main__":
    unittest.main()
