import unittest
from functools import partial
from kornorm.heuristics.repetition import fix_text_degeneration
from kornorm.pipeline import StreamPipeline, BatchPipeline

# BatchPipeline(multiprocessing)에서 직렬화가 가능하도록 최상단에 함수를 정의합니다.
fix_text_degeneration_3 = partial(fix_text_degeneration, repeat_count=3, replace_char="...")

class TestRepetition(unittest.TestCase):
    def setUp(self):
        self.sample = "으아아아아아아아아악"  # '아'가 8번 반복
        self.sample_multi = "아니! 아니! 아니! 아니! 아니! 아니!" # "아니!"가 6번 반복 (띄어쓰기 포함)

    def test_basic_function(self):
        """순정 함수 테스트 (기본값: 5회 반복 후 〃 추가)"""
        result = fix_text_degeneration(self.sample)
        # '아' 5번 + '〃'
        self.assertEqual(result, "으아아아아아〃악")
        
        result_multi = fix_text_degeneration(self.sample_multi, repeat_count=3, replace_char='♤')
        # "아니! " 6번 + '♤'
        self.assertEqual(result_multi, "아니! 아니! 아니! ♤")

        result_multi = fix_text_degeneration('')
        self.assertEqual(result_multi, '')

        result_multi = fix_text_degeneration("abcde ")
        self.assertEqual(result_multi, "abcde ")

    def test_stream_pipeline_with_partial(self):
        """StreamPipeline에 partial로 파라미터를 수정한 함수를 넣어 테스트"""
        # repeat_count=3, replace_char="..." 적용
        pipeline = StreamPipeline(fix_text_degeneration_3)
        samples = [self.sample, self.sample_multi]
        
        results = list(pipeline(samples))
        
        self.assertEqual(results[0], "으아아아...악")
        self.assertEqual(results[1], "아니! 아니! 아니! ...")

    def test_batch_pipeline_with_partial(self):
        """BatchPipeline에 partial로 파라미터를 수정한 함수를 넣어 테스트"""
        # 멀티프로세싱을 위해 최상단에 정의된 fix_text_degeneration_3 사용
        pipeline = BatchPipeline(fix_text_degeneration_3)
        samples = [self.sample, self.sample_multi]
        
        # 소량 데이터이므로 chunksize=1
        results = pipeline(samples, chunksize=1)
        
        self.assertEqual(results[0], "으아아아...악")
        self.assertEqual(results[1], "아니! 아니! 아니! ...")

if __name__ == "__main__":
    unittest.main()
