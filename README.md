# 고놈 KorNorm

2022–2023년 한 AI 음성 합성 스타트업에서 보낸 1년 남짓한 시간 동안 유용하게 썼던 사내 한국어 정규화 도구가 그리워서 직접 만들기 시작한 저장소입니다.  
This repository is born out of nostalgia for a decent in-house Korean normalizer I used during my brief one-year stint at an AI speech startup.

인터넷 곳곳의 능력자들이 공개한 코드를 긁어 모은 뒤, AI 코딩 에이전트에게 맡겨서 재구성하는 방식으로 구현할 예정입니다.  
I'll build this by gathering code from various gigachads online and shoving them all into an AI coding agent to reorganize them.

---

###### 표절할 코드 목록 List to plagiarize

* 내가 퇴사하면서 회사에 유기해놓고 왔던 내 기억 속 텍스트 정규화 라이브러리
* [jamo](https://github.com/jdongian/python-jamo) : [조슈아 동](https://github.com/JDongian)님의 근본 자모 패키지
* 한국어 G2P 라이브러리
  - [Kyubyong/g2pK](https://github.com/Kyubyong/g2pK) : [TUNiB 박규병](https://github.com/Kyubyong)님 g2pK 원본 (2020년 마지막 커밋)
  - [harmlessman/g2pkk](https://github.com/harmlessman/g2pkk) : [무해한생물](https://drawing-thoughts.tistory.com/)님 g2pK 전체 OS 버젼 (2022년 마지막 커밋)
  - [tenebo/g2pk2](https://github.com/tenebo/g2pk2) : [이인표](https://github.com/tenebo)님 g2pK 최신본 (2023년 마지막 커밋)
  - [SMART-G2P](https://github.com/SMART-TTS/SMART-G2P) : SMART-G2P (2023년 마지막 커밋)
* [pecab](https://github.com/hyunwoongko/pecab) : [카카오 고현웅](https://github.com/hyunwoongko)님 순수 파이썬 Mecab
* `OKT` 시리즈
  - [twitter-korean](https://github.com/twitter/twitter-korean-text) : 트위터 코리안 구 버젼 (2019년 마지막 커밋)
  - [open-korean-text](https://github.com/open-korean-text/open-korean-text) : 트위터 코리안 오픈소스 버젼 (2024년 마지막 커밋)
* 유명한 한국어 TTS 클리너 함수들
  - [carpedm20/multi-speaker-tacotron-tensorflow](https://github.com/carpedm20/multi-speaker-tacotron-tensorflow/tree/master/text) : [前 OpenAI 김태훈](https://carpedm30.notion.site/me)님 한국어 tacotron 전처리 함수
  - [hash2430/pitchtron](https://github.com/hash2430/pitchtron/blob/hard/text/korean.py) : [정성희](https://jsh-tts.tistory.com/)님 한국어 pitchtron 전처리 함수
  - [sooftware/taKotron2](https://github.com/sooftware/taKotron2/blob/master/text/__init__.py) : [TUNiB 김수환](https://sooftware.io/)님 한국어 tacotron2 전처리 함수
  - [jyshin0926/KoreanTTS](https://github.com/jyshin0926/KoreanTTS/blob/master/Tacotron2_GriffinLim_TTS/text/__init__.py) : [서울대 신재영](https://github.com/jyshin0926)님 한국어 tacotron2 전처리 함수
  - [esoyeon/KoreanTTS](https://github.com/esoyeon/KoreanTTS/tree/main/Tacotron2-Wavenet-Korean-TTS/text) : [이소연](https://github.com/esoyeon)님 한국어 tacotron2 전처리 함수
  - [hccho2/Tacotron2-Wavenet-Korean-TTS](https://github.com/hccho2/Tacotron2-Wavenet-Korean-TTS/blob/master/text/korean.py) : [조희철](https://github.com/hccho2)님 한국어 Tacotron2+WaveNet 전처리 함수
  - [ssumin6/Korean-TTS-Server](https://github.com/ssumin6/Korean-TTS-Server/blob/master/text/korean.py) : [LINE+ 신수민](https://ssumin6.github.io/)님 한국어 fastspeech 전처리 함수
  - [jeromeryu/FastPitch_Korean](https://github.com/jeromeryu/FastPitch_Korean/blob/master/text/korean.py) : [류지엽](https://github.com/jeromeryu)님 한국어 FastPitch 전처리 함수
  - [HGU-DLLAB/Korean-FastSpeech2-Pytorch](https://github.com/HGU-DLLAB/Korean-FastSpeech2-Pytorch/blob/master/text/korean.py) : [한동대 DL랩](http://deeplearning.handong.edu/) 한국어 FastSpeech2 전처리 함수
  - [jhwanflow/Fastspeech2-Korean](https://github.com/jhwanflow/Fastspeech2-Korean/blob/master/text/korean.py) : [삼일회계 이정환](https://github.com/jhwanflow)님 한국어 FastSpeech2 전처리 함수
  - [keonlee9420/Expressive-FastSpeech2](https://github.com/keonlee9420/Expressive-FastSpeech2/blob/main/text/korean.py) : [크래프톤 이건](https://sites.google.com/view/keonlee9420)님 한국어 FastSpeech2 전처리 함수
  - [MEI-mk11/vits_korean](https://github.com/MEI-mk11/vits_korean/tree/main/text/korean) : [메이](https://github.com/MEI-mk11)님 한국어 FastSpeech2 전처리 함수
  - [ttop32/coqui_tts_korea](https://github.com/ttop32/coqui_tts_korea/blob/main/korean.py) : [다나와 다니엘](https://github.com/ttop32)님 한국어 전처리 함수
  - [jwj7140/Bert-VITS2-Korean](https://github.com/jwj7140/Bert-VITS2-Korean/blob/main/text/korean.py) : [경기대 정우준](https://github.com/jwj7140)님 한국어 Bert-VITS2 전처리 함수
  - [ORI-Muchim/MB-iSTFT-VITS-Korean](https://github.com/ORI-Muchim/MB-iSTFT-VITS-Korean/blob/main/text/korean.py) : [단국대 조민형](https://ori-muchim.github.io/)님 한국어 MB-iSTFT-VITS 전처리 함수
  - [coqui-ai/TTS](https://github.com/coqui-ai/TTS/tree/dev/TTS/tts/utils/text/korean) : Coqui TTS (2022) 한국어 전처리 함수
  - [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS/blob/main/GPT_SoVITS/text/korean.py) : GPT-SoVITS (2024) 한국어 전처리 함수
* [WFST @NeMo-text-processing](https://github.com/NVIDIA/NeMo-text-processing/blob/main/tutorials/WFST_Tutorial.ipynb) : `pynini` 및 `WFST(가중 유한 상태 트랜스듀서, Weighted Finite-State Transducer)`를 이용한 규칙 기반, 결정론적 텍스트 전처리기
