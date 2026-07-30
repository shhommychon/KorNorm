import unittest
from kornorm.phonology import pos

class TestPosExposure(unittest.TestCase):
    def test_surface_tag_pairs(self):
        """(표면형, 품사 태그) 튜플 목록을 돌려주는지 테스트"""
        self.assertEqual(pos("맑게 갠 하늘"), [('맑', "VA"), ('게', "EC"), ('갠', "VV+ETM"), ("하늘", "NNG")])

    def test_drop_space(self):
        """기본값은 공백(SP) 제외, drop_space=False면 포함하는지 테스트"""
        self.assertEqual(pos("낮 한때"), [('낮', "NNG"), ('한', "XSA+ETM"), ('때', "NNG")])
        self.assertEqual(pos("낮 한때", drop_space=False),
                         [('낮', "NNG"), (' ', "SP"), ('한', "XSA+ETM"), ('때', "NNG")])

    def test_engine_view(self):
        """순정 pecab과 다른 엔진의 시점(재태깅·수사 병합)이 반영되는지 테스트"""
        # 한자 원문·호환 자모 낱자는 S 계열로 재태깅됨
        self.assertEqual(pos("漢字 공부"), [("漢字", "SH"), ("공부", "NNG")])
        # 수사 낱자 나열은 사전 표제어 단위로 병합됨 (육/NR+이/NR+오/NR -> 육이오)
        self.assertEqual(pos("육이오 전쟁"), [("육이오", "NNG"), ("전쟁", "NNG")])

if __name__ == "__main__":
    unittest.main()
