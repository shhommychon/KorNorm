import unittest
from kornorm.alphanumeric.preset import dealers_choice

class TestAlnumPreset(unittest.TestCase):
    def test_dealers_choice_case1(self):
        # 케이스 1: 연속된 하이픈 기호와 의존 명사의 결합
        text1 = "임시 비밀번호는 1-2-3-4번 입니다."
        expected1 = "임시 비밀번호는 일대쉬이대쉬삼대쉬네번 입니다."
        self.assertEqual(dealers_choice(text1), expected1)

    def test_dealers_choice_case2(self):
        # 케이스 2: 영숫자 혼합 단위 및 물리 단위 처리
        text2 = "제원은 3.5GHz, 16GB, 220V 규격입니다."
        expected2 = "제원은 삼 쩜 오기가헤르츠, 십육기가바이트, 이백이십븨 규격입니다."
        self.assertEqual(dealers_choice(text2), expected2)

    def test_dealers_choice_case3(self):
        # 케이스 3: 그리스 문자, 수학 기호 및 퍼센트 기호의 연속
        text3 = "수익률이 α+β=100% 이상을 기록했습니다."
        expected3 = "수익률이 알파플러스베타는백퍼센트 이상을 기록했습니다."
        self.assertEqual(dealers_choice(text3), expected3)

    def test_dealers_choice_case4(self):
        # 케이스 4: 복잡한 통화 기호, 천 단위 쉼표, 소수점이 얽힌 텍스트
        text4 = "예상 비용은 €1,234,567.89에다가 ₩999,000의 합산 입니다."
        expected4 = "예상 비용은 백이십삼만사천오백육십칠 쩜 팔구유로에다가 구십구만구천원의 합산 입니다."
        self.assertEqual(dealers_choice(text4), expected4)

    def test_dealers_choice_case5(self):
        # 케이스 5: B2B 같은 영숫자 조합과 큰 숫자의 단위 명사 결합
        text5 = "B2B 계약으로 사과 100개, 장갑 3켤레를 납품했다."
        expected5 = "비투비 계약으로 사과 백개, 장갑 세켤레를 납품했다."
        self.assertEqual(dealers_choice(text5), expected5)

    def test_dealers_choice_case6(self):
        # 케이스 6: 의존 명사가 붙지 않은 단독 0의 독법
        text6 = "오늘 기온은 0도, 강수 확률은 0%입니다."
        expected6 = "오늘 기온은 영도, 강수 확률은 영퍼센트입니다."
        self.assertEqual(dealers_choice(text6), expected6)

if __name__ == "__main__":
    unittest.main()
