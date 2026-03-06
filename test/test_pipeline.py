import unittest
from kornorm.pipeline import StreamPipeline, BatchPipeline


# BatchPipeline(multiprocessing)에서 직렬화가 가능하도록 최상단에 함수를 정의합니다.
def dummy_func_top(text: str) -> str:
    return text + "냥"

class TestPipeline(unittest.TestCase):
    def setUp(self):
        # 입력은 list, 예상 결과도 list로 통일하여 타입 불일치 방지
        self.samples = ["안녕", "반가워", "배고파"]
        self.expected = ["안녕냥", "반가워냥", "배고파냥"]

    def test_stream_pipeline(self):
        pipeline = StreamPipeline(dummy_func_top)
        results = list(pipeline(self.samples))
        self.assertEqual(results, self.expected)

    def test_batch_pipeline(self):
        pipeline = BatchPipeline(dummy_func_top)
        results = pipeline(self.samples, chunksize=1)
        self.assertEqual(results, self.expected)

    def test_pipeline_multiple_funcs(self):
        pipeline = StreamPipeline(dummy_func_top, dummy_func_top)
        results = list(pipeline(self.samples))
        expected_double = ["안녕냥냥", "반가워냥냥", "배고파냥냥"]
        self.assertEqual(results, expected_double)

if __name__ == "__main__":
    unittest.main()
