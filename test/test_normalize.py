import unittest
from kornorm import normalize

class TestNormalize(unittest.TestCase):
    def test_numeral_n_insertion(self):
        """정규화된 수사가 표준 발음법 제29항(ㄴ·ㄹ첨가)에 참여하는지 테스트"""
        self.assertEqual(normalize("3 연대"), "삼 년대")
        self.assertEqual(normalize("1 연대"), "일 련대")
        self.assertEqual(normalize("3연대"), "삼년대")
        self.assertEqual(normalize("1연대"), "일련대")

    def test_interpunct_idioms(self):
        """가운뎃점 숫자 관용 독법이 사전 발음으로 이어지는지 테스트"""
        self.assertEqual(normalize("6·25 전쟁"), "유기오 전쟁")
        self.assertEqual(normalize("3·1절 기념식"), "사밀쩔 기념식")
        self.assertEqual(normalize("8·15 광복"), "파리로 광복")

    def test_english_liaison(self):
        """영어 단어 변환 결과가 조사와 연음되는지 테스트"""
        self.assertEqual(normalize("그 사람 좀 old school이야"), "그 사람 좀 올드 스쿠리야")

    def test_unit_pipeline(self):
        """단위·소수점 정규화가 음운 변동(경음화·연음)으로 이어지는지 테스트"""
        self.assertEqual(normalize("몸무게가 70.5kg 나갔다"), "몸무게가 칠씹 쩜 오킬로그램 나갇따")

    def test_punctuation_passthrough(self):
        """문장부호가 남은 문장도 완성형 출력을 끝까지 마치는지 테스트"""
        self.assertEqual(normalize("같이 갈래?"), "가치 갈래?")
        self.assertEqual(normalize("안녕, 세상! 잘 지냈어?"), "안녕, 세상! 잘 지내써?")

    def test_standalone_zero(self):
        """단독 0이 사라지지 않고 발음까지 이어지는지 테스트"""
        self.assertEqual(normalize("통장 잔액은 0원입니다"), "통장 자내근 영워님니다")
        self.assertEqual(normalize("재고가 0개 남았다"), "재고가 영개 나맏따")

if __name__ == "__main__":
    unittest.main()
