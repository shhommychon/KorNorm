import unittest
from kornorm.utils.jamo import (
    split_syllable_char, decompose, join_jamos, to_compat_jamo, C_NONE
)

class TestJamo(unittest.TestCase):
    def test_split_syllable_char(self):
        """단일 음절의 초/중/종성 분리 테스트"""
        # 종성이 있는 경우
        cho, joong, jong = split_syllable_char('각')
        self.assertEqual(cho, '\u1100')  # O_GIYEOK
        self.assertEqual(joong, '\u1161') # N_A
        self.assertEqual(jong, '\u11a8')  # C_GIYEOK

        # 종성이 없는 경우 C_NONE이 반환되어야 함
        cho, joong, jong = split_syllable_char('가')
        self.assertEqual(jong, C_NONE)

        # 한글이 아닌 경우 그대로 반환
        cho, joong, jong = split_syllable_char('A')
        self.assertEqual(cho, 'A')
        self.assertEqual(joong, '')

    def test_decompose_and_join(self):
        """문자열 전체 분해 테스트"""
        original = "안녕하세요"
        decomposed = decompose(original)
        self.assertEqual('\u200b'.join(decompose(original)), "ᄋ​ᅡ​ᆫ​ᄂ​ᅧ​ᆼ​ᄒ​ᅡ​ㅤ​ᄉ​ᅦ​ㅤ​ᄋ​ᅭ​ㅤ")
    
    def test_join(self):
        """분해된 재조립 테스트"""
        self.assertEqual(join_jamos('\u1100', '\u1161', '\u11a8'), '각')
        self.assertEqual(join_jamos('\u1100', '\u1161', C_NONE), '가')
        self.assertEqual(join_jamos('\u1100', '\u1161', ''), '가')

    def test_to_compat_jamo(self):
        """위치 기반 자모가 호환 자모(ㄱ, ㄴ, ㅏ)로 잘 변환되는지 테스트"""
        # ᄆ​ᅥ​ᆨ (위치 기반) -> ㅁㅓㄱ (호환)
        positional_str = "\u1106\u1165\u11a8"
        compat_str = to_compat_jamo(positional_str)
        self.assertEqual(compat_str, "ㅁㅓㄱ")

if __name__ == "__main__":
    unittest.main()