# 로봇 동작 품질 저하를 가리키는 용어: 동료 심사 논문 기준 재조사

작성 기준일: 2026-09-25. 이전 판은 arXiv preprint 위주 39편을 셌다. 이번 판은 **게재를 직접 확인한 동료 심사 논문만** 센다. 확인 수단은 학회 proceedings 페이지, PMLR, roboticsproceedings.org, 학회 virtual site의 포스터 페이지(accepted paper 목록), DOI(IEEE, SAGE, AAAI)이다. 확인하지 못한 논문은 집계에서 뺐고, 필요한 경우 §9에 "preprint, not peer-reviewed"로 따로 적었다.

---

## 1. 결론

- **집계 대상**: 게재를 확인한 동료 심사 논문 40편. 그룹 A(양자화·압축) 14편, 그룹 B(action smoothness·chunking·tokenization·시간 일관성) 26편이다. 여기에 그룹 C(smoothness 지표의 정의 원전) 4편을 정의 근거로만 따로 썼다.
- **그룹 A는 사실상 비어 있다.** 14편 중 로봇 policy를 **정수·저비트로 양자화**한 논문은 4편(OpenVLA의 int8/int4 평가, SQIL, QVLA, QuantVLA)이고, 관측 공간을 양자화한 Just Round가 1편이다. 나머지 9편은 pruning, token caching, early exit, 증류 같은 압축이다. **양자화가 일으킨 동작 결함을 문장으로 적은 동료 심사 논문은 QVLA(ICLR 2026) 1편뿐이다.** 이것도 시뮬레이션 rollout을 보고 적은 정성 서술이다. **양자화 조건에서 smoothness나 jerk를 수치로 잰 동료 심사 논문은 0편이다.**
- **용어 순위(논문 수, 40편 중)**: smooth/smoothness 28편 > compounding error 14편 > discontinuity/abrupt 13편 > jerk/jerky 11편 > oscillation 9편 > jitter 8편 > drift(동작 의미) 6편 > overshoot 3편 = tremor/vibration/shaking 3편 = mode switching/jumping 3편 > chatter 1편.
- **현상 용어**: 결함을 직접 가리키는 말 중에서는 *jerky / jerkiness*(11편)가 가장 많다. 그러나 문헌에서 "jerky"는 jerk(3차 도함수)를 잰 뒤에 붙이는 말이 아니다. chunk 경계의 위치·속도 불연속까지 두루 부르는 **비정식 표현**이다(ACT, RTC). 주기적으로 되풀이되는 흔들림은 *oscillation*(9편)으로 따로 부르고, 강화학습 문헌은 주파수 스펙트럼 지표로 이를 잰다(CAPS, ASAP).
- **지표 용어**: 정의가 가장 탄탄한 것은 운동재활 분야의 **SPARC**와 **LDLJ**(Balasubramanian et al. 2012, 2015; Hogan & Sternad 2009)이다. 로봇 학습 쪽에서 이 둘을 그대로 쓴 동료 심사 논문으로는 RSS 2026의 Legato(NSPARC, NLDLJ)가 있다. 차원이 있는 jerk 지표(RMS jerk, integrated squared jerk)는 Hogan & Sternad(2009)가 보였듯 동작 시간과 진폭에 따라 직관과 반대로 변한다. 그래서 비교 조건 사이에 동작 시간이 달라지면 해석하기 어렵다.
- **jitter는 주 용어로 쓰지 않는 것이 좋다.** 동작 의미로 8편이 쓰지만, 같은 동료 심사 코퍼스 안에서 scheduling jitter(MAC, ICLR 2026)와 color jitter(π0.5, CoRL 2025)라는 다른 뜻과 겹친다.
- **이전(preprint 기반) 분석에서 더는 성립하지 않는 주장**은 §8에 정리했다. 가장 큰 변화는 두 가지이다. 첫째, "양자화 결함은 jerky라고 가장 많이 부른다(4편)"는 주장은 동료 심사 기준으로 1편(QVLA)만 남는다. 둘째, "average jerk L2 norm이 양자화에 적용된 유일한 지표"라는 근거는 preprint(arXiv 2603.19131)에만 있다.

---

## 2. 범위와 방법

**검증 기준.** 다음 중 하나에서 제목을 직접 확인한 논문만 넣었다.
- 학회 virtual site의 accepted paper 목록(`iclr.cc`, `neurips.cc`, `icml.cc`, `cvpr.thecvf.com`, `iccv.thecvf.com`의 `/virtual/<year>/papers.html`)과 개별 포스터 페이지
- `roboticsproceedings.org`(RSS 2023–2026), `proceedings.mlr.press`(CoRL, ICML), `proceedings.neurips.cc`
- DOI(IEEE ICRA, SAGE IJRR, AAAI OJS)

OpenReview API와 dblp는 이번 조사 환경에서 봇 차단 때문에 열리지 않았다. 그래서 OpenReview 대신 학회 virtual site로 확인했다. arXiv의 "Accepted to …" 주석만 있고 출판사 페이지를 찾지 못한 논문(Grad-CAPS, IROS 2024 주장)은 집계에서 뺐다.

**전문 수집.** 40편 모두 전문을 받았다. 39편은 arXiv HTML 최신판(게재본 반영판으로 가정)이고, LipsNet은 PMLR PDF이다. 참고문헌 절(`ltx_bibliography`), script와 style, MathML 수식은 지운 뒤 셌다. 본문, 그림·표 캡션, 부록은 포함했다.

**정규식**(대소문자 무시, 굴절형 포함):
- jitter: `jitter\w*`
- jerk: `jerk\w*`
- oscillation: `oscillat\w*`
- chatter: `chatter\w*`
- tremor/vibration/shaking: `tremor\w*|vibrat\w*|shak(e|es|ing|y|iness)`
- smooth: `(non-?|un)?smooth\w*`
- discontinuity/abrupt: `discontinu\w*|abrupt\w*`
- overshoot: `overshoot\w*`
- drift: `drift\w*`
- compounding error: `compound… error(s)`, `error(s) … compound…`
- mode: `mode[- ]?(switch|jump|hopp|averag|collaps|mix)…`, `… between (different) modes`

**비동작 의미 제외.** 자동 필터를 거친 뒤 smooth 외의 모든 적중 문맥을 사람이 다시 읽었다. 제외한 뜻은 다음과 같다.
- jitter: latency, scheduling, color jitter
- smooth: SmoothQuant식 activation·weight smoothing, label smoothing, target policy smoothing, EMA "smooth calculation", 이론 가정의 smooth policy(TVC)
- drift: QuantVLA의 "input drift"와 "cross-module drift"(activation 통계), SDE의 drift coefficient, Foster–Lyapunov drift condition, 배터리 SOC drift, 토큰 슬롯 drift
- oscillation: 성공률·학습 곡선의 진동
- discontinuity: 포장지 이음매, 이미지 경계
- mode: mode collapse(생성 모형 의미)
- vibration/shake: 과제 동작("shake to separate"), 참고문헌에 남은 문자열

smooth 적중은 소형 논문은 모두 읽었고, 대형 논문(CAPS, IAC, Legato, ASAP, LipsNet, NIAF)은 표본만 읽었다. 그래서 smooth 횟수는 근사치이다.

**용례 라벨**
- **(i) 정식 지표**: 수식이나 표의 측정값으로 정의해 씀
- **(ii) 관찰된 결함**: 평가한 정책의 동작에서 본 현상을 서술함
- **(iii) 일반 서술**: 동기, 가정, 관련 연구 서술
- **Q**: 양자화가 원인인 결함

---

## 3. 검증된 논문별 표

열 약어는 다음과 같다. 숫자는 모두 동작 의미 횟수이다.
- Jit = jitter, Jrk = jerk, Osc = oscillation, Cht = chatter
- Vib = tremor/vibration/shaking, Smo = smooth, Dis = discontinuity/abrupt
- OS = overshoot, Dft = drift, CE = compounding error, Mode = mode switching/jumping

### 3.1 그룹 A: 양자화 / 저비트 / 압축 (14편)

| # | 논문 | 게재 | 검증 링크 | 종류 | Jit | Jrk | Osc | Cht | Vib | Smo | Dis | OS | Dft | CE | Mode | 용례 |
|--:|---|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| A1 | OpenVLA: An Open-Source Vision-Language-Action Model | CoRL 2024 | [PMLR v270](https://proceedings.mlr.press/v270/kim25c.html) | bf16/int8/int4 평가 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | smooth (ii): Diffusion Policy와 비교. 양자화 결함 서술 없음 |
| A2 | Saliency-Aware Quantized Imitation Learning (SQIL) | ICCV 2025 | [ICCV poster](https://iccv.thecvf.com/virtual/2025/poster/958) | INT4 QAT | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 결함 용어 없음. "large deviations in actions"(Q) |
| A3 | QVLA: Not All Channels Are Equal in VLA Model's Quantization | ICLR 2026 | [ICLR poster](https://iclr.cc/virtual/2026/poster/10009282) | 채널별 비트 할당 PTQ | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 2 | 0 | **jerkiness·oscillation·overshoot (ii·Q)**, CE (iii) |
| A4 | QuantVLA: Scale-Calibrated PTQ for VLA Models | CVPR 2026 | [CVPR poster](https://cvpr.thecvf.com/virtual/2026/poster/39915) | W4A8 PTQ | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | smooth (iii). drift 15회는 모두 비동작(activation 통계) |
| A5 | DeeR-VLA: Dynamic Inference of MLLMs for Efficient Robot Execution | NeurIPS 2024 | [proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/67b0e7c7c2a5780aeefe3b79caac106e-Abstract-Conference.html) | early exit | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 없음 |
| A6 | EfficientVLA: Training-Free Acceleration and Compression for VLA Models | NeurIPS 2025 | [NeurIPS poster](https://neurips.cc/virtual/2025/poster/117949) | layer·token pruning | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 없음 |
| A7 | VLA-Cache: Efficient VLA Manipulation via Adaptive Token Caching | NeurIPS 2025 | [NeurIPS poster](https://neurips.cc/virtual/2025/poster/118121) | token caching | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 없음 |
| A8 | On-Device Diffusion Transformer Policy for Efficient Robot Manipulation (LightDP) | ICCV 2025 | [ICCV poster](https://iccv.thecvf.com/virtual/2025/poster/1292) | pruning + consistency distillation | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 없음 |
| A9 | SP-VLA: Joint Model Scheduling and Token Pruning for VLA Acceleration | ICLR 2026 | [ICLR poster](https://iclr.cc/virtual/2026/poster/10009455) | token pruning | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | smooth (iii) |
| A10 | Action-aware Dynamic Pruning for Efficient VLA Manipulation | ICLR 2026 | [ICLR poster](https://iclr.cc/virtual/2026/poster/10008304) | dynamic pruning | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | abrupt (iii, 동작 국면 전환) |
| A11 | SpecPrune-VLA: Action-Aware Self-Speculative Pruning | ICML 2026 | [ICML poster](https://icml.cc/virtual/2026/poster/64525) | token pruning | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 없음 |
| A12 | Sparse ActionGen: Accelerating Diffusion Policy with Real-time Pruning | ICML 2026 | [ICML poster](https://icml.cc/virtual/2026/poster/65503) | pruning | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | smooth (iii) |
| A13 | Consistency Policy: Accelerated Visuomotor Policies via Consistency Distillation | RSS 2024 | [RSS p071](https://www.roboticsproceedings.org/rss20/p071.html) | step distillation | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 없음 |
| A14 | Just Round: Quantized Observation Spaces Enable Memory Efficient Learning of Dynamic Locomotion | ICRA 2023 | [IEEE Xplore](https://ieeexplore.ieee.org/document/10160293/) | 관측 양자화 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 없음 |

### 3.2 그룹 B: action smoothness / chunking / tokenization / 시간 일관성 (26편)

| # | 논문 | 게재 | 검증 링크 | Jit | Jrk | Osc | Cht | Vib | Smo | Dis | OS | Dft | CE | Mode | 용례 |
|--:|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| B1 | Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT) | RSS 2023 | [RSS p016](https://www.roboticsproceedings.org/rss19/p016.html) | 0 | 1 | 0 | 0 | 1 | 6 | 1 | 0 | 1 | 10 | 0 | jerky (ii, naive chunking), CE·drift (iii, 메커니즘) |
| B2 | Diffusion Policy: Visuomotor Policy Learning via Action Diffusion | RSS 2023 / IJRR 2025 | [RSS p026](https://www.roboticsproceedings.org/rss19/p026.html), [IJRR DOI](https://doi.org/10.1177/02783649241273668) | 3 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 2 | 0 | jittery·abrupt (ii) |
| B3 | FAST: Efficient Action Tokenization for VLA Models | RSS 2025 | [RSS p012](https://www.roboticsproceedings.org/rss21/p012.html) | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 결함 용어 없음 |
| B4 | π0: A VLA Flow Model for General Robot Control | RSS 2025 | [RSS p010](https://www.roboticsproceedings.org/rss21/p010.html) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 없음 |
| B5 | π0.5: a VLA Model with Open-World Generalization | CoRL 2025 | [PMLR v305](https://proceedings.mlr.press/v305/black25a.html) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 없음. jitter 2회는 color jitter |
| B6 | Regularizing Action Policies for Smooth Control with RL (CAPS) | ICRA 2021 | [DOI](https://doi.org/10.1109/ICRA48506.2021.9561138) | 0 | 0 | 12 | 0 | 0 | 86 | 0 | 1 | 0 | 0 | 0 | oscillation (ii), smoothness **(i)** Sm |
| B7 | Bidirectional Decoding: Improving Action Chunking via Guided Test-Time Sampling (BID) | ICLR 2025 | [ICLR poster](https://iclr.cc/virtual/2025/poster/28245) | 2 | 0 | 2 | 0 | 0 | 4 | 0 | 0 | 0 | 2 | 0 | jittery·"oscillations between strategies" (ii) |
| B8 | Real-Time Execution of Action Chunking Flow Policies (RTC) | NeurIPS 2025 | [proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/300ccb2187dedd4edcc07f7e76d8e553-Abstract-Conference.html) | 0 | 5 | 2 | 0 | 0 | 3 | 4 | 0 | 0 | 0 | 2 | jerky·discontinuity·oscillation (ii), mode-jumping (iii), max acceleration (i, proxy) |
| B9 | VQ-VLA: Scaling Vector-Quantized Action Tokenizers | ICCV 2025 | [ICCV poster](https://iccv.thecvf.com/virtual/2025/poster/1332) | 1 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | jittery (ii, 데이터), smooth (iii, 주장) |
| B10 | BEAST: B-Spline Encoded Action Sequence Tokenizer | NeurIPS 2025 | [NeurIPS poster](https://neurips.cc/virtual/2025/poster/115779) | 0 | 4 | 0 | 0 | 0 | 19 | 2 | 0 | 0 | 1 | 0 | jerky (iii, 평가 기준 문구 포함) |
| B11 | Quantization-Free Autoregressive Action Transformer (Q-FAT) | NeurIPS 2025 | [NeurIPS poster](https://neurips.cc/virtual/2025/poster/120026) | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | jitter (iii) |
| B12 | Neural Implicit Action Fields (NIAF) | ICML 2026 | [ICML poster](https://icml.cc/virtual/2026/poster/64538) | 9 | 10 | 2 | 0 | 0 | 29 | 4 | 0 | 0 | 5 | 0 | jitter·oscillation (ii, baseline 속도 곡선), jerk 정규화 손실 |
| B13 | Implicit Action Chunking for Smooth Continuous Control | ICML 2026 | [ICML poster](https://icml.cc/virtual/2026/poster/62846) | 11 | 37 | 18 | 0 | 0 | ≈141 | 5 | 0 | 1 | 0 | 0 | **Jerk RMS·AFR (i)**, oscillation·jitter (ii) |
| B14 | Mixture of Horizons in Action Chunking | ICML 2026 | [ICML poster](https://icml.cc/virtual/2026/poster/66600) | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 2 | 0 | 0 | "cumulative drift effect" (ii) |
| B15 | FocalPolicy: Frequency-Optimized Chunking … Coherent Visuomotor Policy | ICML 2026 | [ICML poster](https://icml.cc/virtual/2026/poster/66520) | 0 | 0 | 0 | 0 | 0 | 10 | 17 | 0 | 6 | 14 | 0 | **ATV·TS (i)**, inter-chunk discontinuity (ii), CE (i, Euclidean 거리) |
| B16 | Understanding Behavior Cloning with Action Quantization | ICML 2026 | [ICML poster](https://icml.cc/virtual/2026/poster/65817) | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 0 | CE (iii, 이론). smooth 23회는 정책의 TVC 평활성 가정이라 제외 |
| B17 | Real-Time Robot Execution with Masked Action Chunking | ICLR 2026 | [ICLR poster](https://iclr.cc/virtual/2026/poster/10007187) | 0 | 3 | 0 | 0 | 0 | 7 | 15 | 0 | 0 | 1 | 0 | jerky·inter-chunk discontinuity (ii). jitter 1회는 scheduling jitter |
| B18 | Adaptive Action Chunking at Inference-time for VLA Models | CVPR 2026 | [CVPR poster](https://cvpr.thecvf.com/virtual/2026/poster/39692) | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | RTC 문장을 거의 그대로 인용 (iii) |
| B19 | Learning Native Continuation for Action Chunking Flow Policies (Legato) | RSS 2026 | [RSS p058](https://www.roboticsproceedings.org/rss22/p058.html) | 1 | 11 | 9 | 0 | 0 | ≈83 | 9 | 0 | 1 | 0 | 1 | **NLDLJ·NSPARC·overlap RMSE (i)**, oscillation (ii) |
| B20 | OAT: Ordered Action Tokenization | RSS 2026 | [RSS p075](https://www.roboticsproceedings.org/rss22/p075.html) | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 1 | 0 | smoother motions (ii) |
| B21 | Streaming Flow Policy | CoRL 2025 | [PMLR v305](https://proceedings.mlr.press/v305/jiang25a.html) | 0 | 1 | 0 | 0 | 0 | 4 | 0 | 0 | 1 | 0 | 0 | smoother motion (ii), jerky (iii) |
| B22 | Smooth Exploration for Robotic Reinforcement Learning (gSDE) | CoRL 2021 | [PMLR v164](https://proceedings.mlr.press/v164/raffin22a.html) | 3 | 3 | 2 | 0 | 3 | 21 | 0 | 0 | 0 | 0 | 0 | **continuity cost (i)**, jittery·shaky·jerky (ii/iii) |
| B23 | Is Bang-Bang Control All You Need? | NeurIPS 2021 | [proceedings](https://proceedings.neurips.cc/paper/2021/hash/e46be61f0050f9cc3a98d5d2192cb0eb-Abstract.html) | 0 | 0 | 0 | 2 | 0 | 4 | 1 | 1 | 0 | 0 | 0 | chattering (iii, 최적제어의 정식 의미) |
| B24 | Behavior Generation with Latent Actions (VQ-BeT) | ICML 2024 | [ICML poster](https://icml.cc/virtual/2024/poster/33379) | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 1 | 0 | smooth trajectories (ii) |
| B25 | LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant | ICML 2023 | [PMLR v202](https://proceedings.mlr.press/v202/song23b.html) | 0 | 0 | 0 | 0 | 1 | ≈45 | 0 | 0 | 0 | 0 | 0 | **action fluctuation ratio (i)** |
| B26 | Enhancing Control Policy Smoothness by Aligning Actions with Predictions from Preceding States (ASAP) | AAAI 2026 | [DOI](https://doi.org/10.1609/aaai.v40i27.39432) | 0 | 0 | 23 | 0 | 0 | 42 | 1 | 0 | 0 | 0 | 0 | oscillation (ii), **Sm (i)** |

### 3.3 그룹 C: smoothness 지표의 정의 원전 (집계 제외, 정의 근거로만 사용)

| 논문 | 게재 | 검증 링크 | 쓰임 |
|---|---|---|---|
| Flash & Hogan, The coordination of arm movements: an experimentally confirmed mathematical model | J. Neuroscience 5(7):1688–1703, 1985 | [DOI 10.1523/JNEUROSCI.05-07-01688.1985](https://doi.org/10.1523/JNEUROSCI.05-07-01688.1985) | minimum-jerk 모형(적분 제곱 jerk 최소화) |
| Hogan & Sternad, Sensitivity of smoothness measures to movement duration, amplitude, and arrests | J. Motor Behavior 41(6):529–534, 2009 | [DOI 10.3200/35-09-004-RC](https://doi.org/10.3200/35-09-004-RC), [PMC3470860](https://pmc.ncbi.nlm.nih.gov/articles/PMC3470860/) | jerk 지표의 단위와 정규화, dimensionless squared jerk |
| Balasubramanian, Melendez-Calderon & Burdet, A robust and sensitive metric for quantifying movement smoothness | IEEE T-BME 59(8):2126–2136, 2012 | [DOI 10.1109/TBME.2011.2179545](https://doi.org/10.1109/TBME.2011.2179545) | spectral arc length(SAL) 도입 |
| Balasubramanian, Melendez-Calderon, Roby-Brami & Burdet, On the analysis of movement smoothness | J. NeuroEng. Rehabil. 12:112, 2015 | [DOI 10.1186/s12984-015-0090-9](https://doi.org/10.1186/s12984-015-0090-9), [PMC4674971](https://pmc.ncbi.nlm.nih.gov/articles/PMC4674971/) | DLJ, LDLJ, SPARC의 정의와 비교 |

---

## 4. 용어 순위 (동료 심사 40편만)

"논문 수"는 해당 용어를 동작 의미로 1회 이상 쓴 논문 수이다. 괄호 안은 그룹 A / 그룹 B 내역이다.

| 순위 | 용어군 | 논문 수 (A/B) | 동작 의미 횟수 | (i) 지표로 쓴 논문 | (ii) 관찰 결함으로 쓴 논문 | 성격 |
|--:|---|--:|--:|---|---|---|
| 1 | smooth / smoothness / non-smooth | **28** (4/24) | ≈537 | CAPS, gSDE, LipsNet, ASAP, IAC, Legato, FocalPolicy (7편) | OpenVLA, VQ-BeT, OAT, SFP 등 | 상위 개념. 대부분 긍정형("smoother") |
| 2 | compounding error | 14 (2/12) | 45 | FocalPolicy(Euclidean 거리로 측정) | – | **메커니즘** 용어 |
| 3 | discontinuity / abrupt | 13 (1/12) | 62 | FocalPolicy(ATV), Legato(overlap RMSE) | DP, RTC, MAC, Legato, FocalPolicy | chunk 경계 현상 |
| 4 | jerk / jerky / jerkiness | 11 (1/10) | 77 | IAC(Jerk RMS), Legato(LDLJ), RTC(가속도 proxy) | **QVLA(Q)**, ACT, RTC, MAC | 현상어(jerky)와 물리량(jerk)이 섞여 쓰임 |
| 5 | oscillation / oscillatory | 9 (1/8) | 71 | ASAP·CAPS(Sm으로 측정) | **QVLA(Q)**, CAPS, BID, RTC, NIAF, IAC, Legato, ASAP | 주기적 왕복 |
| 6 | jitter / jittery | 8 (0/8) | 32 | gSDE(continuity cost), IAC | DP, BID, NIAF, IAC, gSDE | 비동작 의미와 겹침 |
| 7 | drift (동작 의미) | 6 (0/6) | 12 | FocalPolicy(DC offset 모형) | MoH | 궤적이 서서히 벗어남 |
| 8 | overshoot | 3 (1/2) | 3 | – | **QVLA(Q)**, CAPS | 정성 서술뿐 |
| 8 | tremor / vibration / shaking | 3 (0/3) | 5 | – | gSDE("shaky") | 드묾. tremor는 0편 |
| 8 | mode switching / jumping | 3 (0/3) | 4 | – | Legato | 메커니즘. RTC가 "mode-jumping"을 씀 |
| 11 | chatter / chattering | 1 (0/1) | 2 | – | – | 최적제어의 정식 개념(Zeno) |

읽을 때 주의할 점:
- 그룹 A 14편 중 smooth 외의 결함 용어를 쓴 논문은 QVLA 한 편이다. 그 한 편이 jerkiness, oscillation, overshoot를 한 번씩 쓴다. 그래서 양자화 문헌에서 "어느 결함 용어가 우세하다"고 말할 표본이 없다.
- 횟수는 몇 편에 쏠려 있다. smooth는 IAC(≈141), CAPS(86), Legato(≈83)가 과반이다. jerk 77회 중 37회는 IAC, oscillation 71회 중 23회는 ASAP이다. 논문 수를 1차 기준으로 삼았다.
- IAC의 jerk 37회에는 표 머리글("Jerk_RMS", "Jerk_P95")이 많이 들어 있다.
- "mode averaging"이라는 표현은 동료 심사 코퍼스에서 한 번도 나오지 않았다. 비슷한 개념은 다른 말로 나온다. DP는 "consecutive actions could be drawn from different modes", BID는 "oscillations between different strategies", Legato는 "spurious multimodal switching"이라고 썼다.

---

## 5. 인용 예시 (원문)

### 5.1 양자화가 원인인 결함 (동료 심사 기준 유일한 예)

| 논문 | 용어 | 원문 | 라벨 |
|---|---|---|---|
| QVLA (ICLR 2026), App. H | oscillation, jerkiness | "certain quantized models, especially when attempting to recover a distant object may exhibit localized oscillation or jerkiness without initiating a clear effective re-engagement trajectory, as shown in Fig. 6 (a)." | (ii)·Q. ALOHA 시뮬레이션 rollout을 보고 적은 정성 서술 |
| QVLA (ICLR 2026), App. H | overshoot | "when attempting to grasp an object, the quantized gripper may significantly overshoot the target (as shown in Fig. 5)." | (ii)·Q. LIBERO rollout |
| SQIL (ICCV 2025) | (결함 용어 없음) | "Certain critical states, however, experience large deviations in actions due to quantization errors …, ultimately causing mission failures" | (ii)·Q. 편차는 FP 대비 action L2로 잼 |
| OpenVLA (CoRL 2024) | (동작 품질 언급 없음) | int8 성공률 하락을 지연 탓으로 설명한다: "we can only run the model at 1.2Hz, which significantly changes the system dynamics compared to the training dataset for the 5Hz non-blocking controller" | 교란 변수(주기 변화) |

### 5.2 chunking·smoothness 문헌의 현상 서술

| 논문 | 용어 | 원문 | 라벨 |
|---|---|---|---|
| ACT (RSS 2023) | jerky | "a new environment observation is incorporated abruptly every k steps and can result in jerky robot motion." | (ii) |
| Diffusion Policy (RSS 2023) | jittery | "consecutive actions could be drawn from different modes, resulting in jittery actions that alternate between the two valid trajectories." | (ii), mode switching 메커니즘 |
| RTC (NeurIPS 2025) | jerky, mode-jumping, discontinuity | "a short one increases the likelihood of mode-jumping, jerky behavior resulting from discontinuities between chunks." | (ii)+(iii) |
| RTC (NeurIPS 2025) | jerkiness (proxy) | "maximum acceleration (second discrete difference) … Higher … leads to more jerkiness, a proxy for out-of-distribution actions." | (i) proxy |
| BID (ICLR 2025) | oscillation | "this simple closed-loop approach destroys the consistency preserved within each chunk, potentially leading to oscillations between different strategies." | (iii)→(ii) |
| CAPS (ICRA 2021) | oscillation | "the trained agent presented with significant high-frequency control signal oscillations, which would cause the drone's motors to overheat" | (ii) |
| gSDE (CoRL 2021) | jitter, jerky, shaky | "We quantify this jitter as the mean absolute difference between two timesteps, denoted as continuity cost" | (i). 수식은 §6.2 참고 (제곱으로 정의되어 문장과 어긋남) |
| IAC (ICML 2026) | jitter, jerk | "We verify whether the Execution Window can naturally suppress control jitter (Jerk) and enforce temporally coherent trajectories." | (i) |
| Legato (RSS 2026) | oscillation | "overlap RMSE may fail to fully capture smoothness degradation when oscillations are dominated by low-frequency, large-amplitude motion." | (ii), 지표의 한계 |
| NIAF (ICML 2026) | jitter, oscillation | "The velocity profiles exhibit high-frequency oscillations hovering around zero, indicating disjointed stop-and-go motion" | (ii) |
| Bang-Bang (NeurIPS 2021) | chattering | "This behavior is referred to as chattering or Zeno's phenomenon." | (iii), 정식 개념 |

### 5.3 같은 단어가 다른 뜻으로 쓰인 예 (동료 심사 논문 안에서)

| 논문 | 단어 | 원문 | 뜻 |
|---|---|---|---|
| Masked Action Chunking (ICLR 2026) | jitter | "VLA inference time, network transmission, file I/O, memory contention, and system-level scheduling jitter" | 타이밍 흔들림 |
| π0.5 (CoRL 2025) | jitter | color jitter 증강 | 이미지 증강 |
| QuantVLA (CVPR 2026) | drift | "the perturbation propagates downstream as input drift", "cross-module drift" | activation 통계의 이동 |
| QVLA, QuantVLA | smooth | OmniQuant·SmoothQuant식 "smooths weight and activation outliers" | 양자화 기법 |
| Understanding BC with Action Quantization (ICML 2026) | smooth | "the policy satisfies a probabilistic smoothness condition" | 정책 분포의 연속성(TVC) 가정 |

---

## 6. 엄밀한 용어 정의

세 층위로 나눈다.
- **현상 용어(phenomenon)**: 무엇이 보였는가
- **지표 용어(metric)**: 무엇을 어떻게 쟀는가
- **메커니즘 용어(mechanism)**: 왜 생겼는가

한 문장 안에서 이 셋을 섞지 않는 것이 좋다. 예를 들어 "jerky"(현상)를 썼다면, 어떤 지표로 쟀는지와 어떤 메커니즘을 가정하는지를 따로 밝힌다.

### 6.1 현상 용어

| 용어 | 정의 (출처) | 문헌에서의 엄밀성 | 권고 |
|---|---|---|---|
| **jerky motion / jerkiness** | 물리량 jerk는 가속도의 시간 미분, 곧 위치의 3차 도함수이다 (Flash & Hogan 1985; Hogan & Sternad 2009: "jerk, the time-derivative of acceleration"). "jerky"는 가속도가 급변하는 매끄럽지 않은 동작을 가리키는 서술어이다. | **비정식.** ACT와 RTC는 chunk 경계에서 명령이 튀는 현상(위치·속도의 불연속)을 jerky라고 불렀다. 그런 현상을 jerk 수치로 잰 것은 아니다. 동료 심사 코퍼스에서 jerky를 jerk 지표와 함께 쓴 논문은 IAC와 Legato 정도이다. | 정성 서술에 쓰되, 같은 문단에 측정 지표(§6.2)를 붙인다. |
| **oscillation (high-frequency / low-frequency)** | 동작이나 명령이 평균 주위를 반복해서 왕복하는 현상이다. RL 문헌은 제어 신호의 고주파 성분으로 규정하고 스펙트럼 지표로 잰다 (CAPS: "control signal oscillation"; ASAP: "To quantify action oscillations, we adopted a smoothness measurement method based on the FFT frequency spectrum"). | 비교적 정식이다. 주파수 대역이 문헌마다 다르다. Legato는 "low-frequency, large-amplitude oscillations"를 따로 구분했고, BID는 전략 사이의 왕복도 oscillation이라 불렀다. | 주파수 대역(high/low)과 대상(명령 action인지 관절 궤적인지)을 명시한다. |
| **inter-chunk discontinuity** | 연속한 action chunk의 경계에서 명령값이 튀는 현상이다 (RTC; MAC: "If [two chunks] coincide up to timestep … but diverge thereafter, inter-chunk discontinuity arises at the boundary"). | 정식에 가깝다. FocalPolicy는 ATV로, Legato는 overlap RMSE로 쟀다. | chunked policy(ACT, SmolVLA 등)를 쓰면 jerky와 따로 보고한다. |
| **overshoot** | 목표를 지나쳐 가는 현상이다 (QVLA: "the quantized gripper may significantly overshoot the target"; CAPS). | 코퍼스 안에서는 **정성 서술뿐**이다. 정식 정의(예: percent overshoot)를 준 동료 심사 논문은 이번 조사에서 찾지 못했다. | 쓰려면 "목표 위치 대비 최대 초과 거리"처럼 조작적 정의를 직접 적고, 자기 정의임을 밝힌다. |
| **jitter** | 동작 의미로는 작고 빠른 불규칙 흔들림을 뜻한다 (DP: "jittery actions"; NIAF: "high-frequency jitter"; gSDE는 continuity cost로 수치화). | **모호하다.** 같은 코퍼스에서 scheduling jitter(MAC), color jitter(π0.5)와 겹친다. | 주 용어로 쓰지 않는다. 쓰려면 "action jitter (high-frequency action fluctuation)"로 한정한다. 지연 흔들림은 "latency variability"나 "timing jitter"로 이름을 따로 붙인다. |
| **drift (trajectory drift)** | 궤적이나 상태가 기준에서 서서히 벗어나는 현상이다 (ACT: "errors … accumulate and cause the robot to drift off of its training distribution"; FocalPolicy: "macroscopic drift error modeled as a constant DC offset"; MoH: "cumulative drift effect"). | **모호하다.** 양자화 논문(QuantVLA)에서는 activation 통계의 이동을 가리킨다. | "trajectory deviation from the FP reference"처럼 기준과 거리를 밝혀 쓴다. |
| **chattering** | 최적제어에서 유한 시간 안에 제어가 무한히 자주 전환되는 현상이다 (Bang-Bang: "chattering or Zeno's phenomenon"). | 정식이지만 **다른 분야의 뜻**이다. | 그리퍼 개폐가 반복되는 현상을 이 말로 부르지 않는다. "gripper toggling"처럼 부르고 횟수 정의를 직접 적는다. |
| **tremor / shaking / vibration** | tremor는 코퍼스 0편이다. gSDE가 "shaky behavior"를 썼다. | 드물다. tremor는 임상 용어이다. | 쓰지 않는다. |

### 6.2 지표 용어 (수식, 단위, 민감도)

표기는 다음과 같다. 위치는 $x(t)$, 속력은 $v(t)=\|\dot x(t)\|$, jerk는 $j(t)=\dddot x(t)$로 쓴다. 동작 구간은 $[t_1,t_2]$, 길이는 $D=t_2-t_1$, 진폭은 $A$, 최대 속력은 $v_{\text{peak}}=\max_t v(t)$이다.

**(a) jerk와 차원이 있는 jerk 지표** (Hogan & Sternad 2009, Table 1)
- jerk: $j(t)=\dfrac{d^3x}{dt^3}$. 단위는 $L\,T^{-3}$ (예: m/s³, rad/s³). Flash & Hogan(1985)은 손 jerk 크기의 제곱을 동작 전체에 걸쳐 적분한 값을 목적함수로 삼았다: $C\propto\int_0^{D}\big(\dddot x^2+\dddot y^2\big)\,dt$ (평면 손 좌표 $x,y$; 상수 배는 원문 식을 따른다). 원문 초록의 표현은 "the square of the magnitude of jerk … integrated over the entire movement"이다.
- integrated squared jerk: $\int_{t_1}^{t_2}\|j(t)\|^2dt$. 단위는 $L^2T^{-5}$.
- RMS jerk: $\sqrt{\tfrac{1}{D}\int_{t_1}^{t_2}\|j(t)\|^2dt}$. 단위는 $L\,T^{-3}$.
- 민감도: Hogan & Sternad는 단위가 있는 jerk 지표가 "vary counter-intuitively with movement smoothness"라고 보였다. 동작 시간이 길어지면 이 지표들은 급격히 작아진다. 정지 구간(arrest)이 있으면 적분 지표와 평균 지표가 서로 다르게 움직인다. Balasubramanian et al.(2015, Table 1)도 RMS jerk를 타당한(valid) smoothness 지표가 아니라고 분류했다.
- 로봇 학습에서의 사용: IAC(ICML 2026)는 로그 속도의 유한 차분으로 가속도와 jerk를 추정해 "Jerk RMS"를 보고했다. 조건 사이에 동작 시간이 비슷할 때만 비교가 공정하다.

**(b) dimensionless jerk (DLJ)와 log dimensionless jerk (LDLJ)**
- Hogan & Sternad(2009)의 dimensionless squared jerk: $\Big(\int_{t_1}^{t_2}\|\dddot x\|^2dt\Big)\dfrac{D^5}{A^2}$. 무차원이고 동작 시간과 진폭에 독립적이다.
- Balasubramanian et al.(2015)의 정의:
  $$\mathrm{DLJ}\triangleq-\frac{(t_2-t_1)^5}{v_{\text{peak}}^2}\int_{t_1}^{t_2}\left|\frac{d^2v(t)}{dt^2}\right|^2dt,\qquad \mathrm{LDLJ}\triangleq-\ln\left|\mathrm{DLJ}\right|$$
  무차원이다. 값이 클수록(0에 가까운 음수 쪽일수록) 매끄럽다.
- 민감도: 원문은 "the LDLJ is highly sensitive to noise, and even lowpass filtering does not fully address this problem"이라고 적고, "we recommend the use of SPARC over LDLJ"라고 결론지었다. 3차 미분이 측정 잡음을 크게 증폭하기 때문이다.
- 로봇 학습에서의 사용: Legato(RSS 2026)는 $\mathrm{LDLJ}=-\log\big(\tfrac{T^5}{v_{\text{peak}}^2}\int_0^T\|j(t)\|^2dt\big)$를 쓰고, 부호를 뒤집은 NLDLJ를 보고했다. 병진과 회전을 따로 계산하고 chunk 연결 지점의 jerk 표본은 뺐다.

**(c) spectral arc length: SAL과 SPARC** (Balasubramanian et al. 2012, 2015)
- 속력 $v(t)$의 Fourier magnitude spectrum을 $V(\omega)$라 하고 DC 성분으로 정규화한다: $\hat V(\omega)=V(\omega)/V(0)$.
- SAL: $\mathrm{SAL}\triangleq-\int_0^{\omega_c}\sqrt{\left(\tfrac{1}{\omega_c}\right)^2+\left(\tfrac{d\hat V(\omega)}{d\omega}\right)^2}\,d\omega$. 원 정의에서 $\omega_c=40\pi$(20 Hz)로 고정한다.
- SPARC: 차단 주파수를 적응적으로 정한다. $\omega_c\triangleq\min\big\{\omega_c^{\max},\ \min\{\omega:\hat V(r)<\bar V\ \forall r>\omega\}\big\}$. 2015년 논문의 예시 설정은 $\bar V=0.05$, $\omega_c^{\max}=20\pi$(10 Hz)이다.
- 성질: 무차원이고 음수이며, 0에 가까울수록 매끄럽다. 원문은 SPARC가 "independent of temporal movement scaling"이고 잡음에 강건하다고 적었다. 스펙트럼의 모양, 즉 저주파에 에너지가 모인 정도를 보므로 고주파 흔들림과 여러 번 끊기는 동작(submovement)에 민감하다.
- 로봇 학습에서의 사용: Legato(RSS 2026)가 NSPARC를 보고했다. 원문은 "NSPARC primarily captures the distribution of motion energy across frequencies"라고 적었다.
- 주의: 원 논문은 사람의 팔 동작(대개 20 Hz 이하)을 전제로 대역을 정했다. 로봇에서 쓸 때는 $\omega_c^{\max}$를 제어 주기의 Nyquist 주파수 이하로 잡아야 한다. 이 조정은 필자의 권고이며, 문헌에서 확인한 규칙이 아니다.

**(d) action(명령) 수준 지표** (로봇 학습 문헌)

| 지표 | 수식 (출처) | 무엇에 민감한가 |
|---|---|---|
| CAPS smoothness $Sm$ | $Sm=\dfrac{2}{n f_s}\sum_{i=1}^{n}M_i f_i$. $M_i$는 $i$번째 주파수 성분 $f_i$의 진폭, $f_s$는 샘플링 주파수 (CAPS, ICRA 2021) | 명령 신호의 "mean weighted normalized frequency"이다. 고주파 성분이 클수록 커진다. 원문은 "comparing smoothness numbers between different problems is not necessarily meaningful"이라고 경고한다. ASAP(AAAI 2026)도 같은 식을 쓴다. |
| continuity cost | $\mathcal C=100\times\mathbb E_t\!\left[\left(\dfrac{a_{t+1}-a_t}{\Delta^{a}_{\max}}\right)^2\right]$. 0(일정 출력)부터 100(매 스텝 한 극단에서 다른 극단으로)까지 (gSDE, CoRL 2021) | 연속 명령의 제곱 변화량이다. 본문 서술("mean absolute difference")과 수식(제곱)이 어긋나므로 인용할 때는 수식을 따른다. |
| action fluctuation ratio | $\xi(\pi)=\mathbb E_{\tau}\!\left[\tfrac1T\sum_{t=1}^{T}\|a_t-a_{t-1}\|\right]$ (LipsNet, ICML 2023) | 1차 차분의 크기이다. 느리지만 큰 동작에도 값이 커진다. |
| Action Total Variation (ATV) | $\mathrm{ATV}=\dfrac{1}{(L-1)d}\sum_{t=1}^{L-1}\sum_{j=1}^{d}\lvert a^{j}_{t+1}-a^{j}_{t}\rvert$ (FocalPolicy, ICML 2026) | 차원별 1차 변화량의 평균이다. chunk 경계 불연속을 잡는 데 썼다. |
| maximum acceleration | 명령의 2차 이산 차분의 최댓값 (RTC, NeurIPS 2025) | "jerkiness, a proxy for out-of-distribution actions"로 썼다. 정식 smoothness 지표로 제안한 것은 아니다. |
| overlap RMSE | 연속한 chunk의 겹치는 구간에서 두 예측 사이의 RMSE (Legato, RSS 2026) | chunk 사이의 일관성을 잰다. 원문은 저주파·대진폭 진동은 잘 못 잡는다고 적었다. |

이산 시간에서 jerk는 보통 3차 유한 차분으로 근사한다: $j_t\approx(x_{t+1}-3x_t+3x_{t-1}-x_{t-2})/\Delta t^3$. 표준 수치해석 근사이며, 특정 논문의 정의가 아니다. 3차 차분은 잡음을 크게 증폭하므로 LDLJ와 같은 경고가 적용된다.

### 6.3 메커니즘 용어

| 용어 | 정의 (출처) | 비고 |
|---|---|---|
| **compounding error** | 앞 시점의 오차가 누적되어 학습 분포 밖 상태로 벗어나는 현상이다. ACT: "errors from previous timesteps accumulate and cause the robot to drift off of its training distribution, leading to hard-to-recover states". BID: "deviations from the training distribution accumulate over time". Understanding BC with Action Quantization(ICML 2026)은 이론적으로 "exponential compounding error"를 다룬다. | 동작 품질 현상이 아니라 **원인 설명**이다. FocalPolicy는 이를 예측 궤적과 전문가 궤적 사이의 Euclidean 거리로 수치화했다. |
| **covariate shift / distribution shift** | 학습 때와 실행 때의 상태 분포가 어긋나는 것이다 (BEAST: "reduces covariate shift"; ACT: "states that are outside of training distribution"). | 코퍼스에 수식으로 정의한 논문은 없었다. compounding error의 결과로 서술된다. |
| **quantization error (quantization noise)** | QVLA: "The perturbation induced by quantization is modeled as the quantization error, $\Delta X_{l,c}\approx(Q(W_l)-W_l)X_l$". 이것이 action에 미치는 크기는 $\|\Delta\mathcal A\|\approx\|J_{\mathcal A,X_{l,c}}\|\cdot\|\Delta X_{l,c}\|$로 근사한다 (QVLA Eq. 6). | 양자화 연구에서 "왜 동작이 나빠지는가"를 설명할 때 쓸 용어이다. 동작 현상 이름으로 쓰지 않는다. SmoothQuant의 "smoothing"과 구분한다. |
| **mode switching / mode jumping** | 다봉(multimodal) 행동 분포에서 연속한 예측이 서로 다른 모드(전략)에서 뽑히는 것이다. RTC: "adjacent chunks may jump between different modes (or 'strategies')". DP: "consecutive actions could be drawn from different modes, resulting in jittery actions". Legato: "spurious multimodal switching". | jittery나 jerky 현상의 **원인**으로 쓰인다. "mode averaging"은 코퍼스에서 확인되지 않았으므로 쓰려면 직접 정의해야 한다. |
| **latency / inference delay** | chunk 실행 중 다음 추론이 늦어지는 것이다 (RTC, MAC). | 동작 결함의 원인이지만 이 연구의 초점(동작 품질)과 섞이지 않게 통제 변수로 둔다. OpenVLA의 int8 사례가 교란 예이다. |

---

## 7. 권장 용어: FP vs INT8/INT4 VLA의 SO-101 제어 비교 (동작 품질만)

| 용도 | 권장 용어 | 정의와 근거 |
|---|---|---|
| 상위 개념(제목, RQ) | **motion smoothness** / "degradation in motion smoothness" | 40편 중 28편이 쓰는 가장 넓은 말이다. 반드시 §6.2의 지표로 조작적으로 정의한다. |
| 주 지표 (궤적) | **SPARC**, 관절 속력 또는 EE 속력에 적용 | 무차원이고, 동작 시간 스케일에 독립적이고, 잡음에 강건하다 (Balasubramanian et al. 2015). 양자화로 동작 시간이 바뀌어도 비교할 수 있다. 로봇 정책 비교에 쓴 동료 심사 사례로 Legato(RSS 2026)가 있다. |
| 보조 지표 (궤적) | **LDLJ** (dimensionless jerk의 로그) | jerk 기반 지표 중 타당성이 확인된 유일한 형태이다 (Hogan & Sternad 2009; Balasubramanian et al. 2015). 잡음에 민감하므로 필터 설정을 함께 적는다. RMS jerk만 단독으로 쓰지 않는다. |
| 보조 지표 (명령) | **action fluctuation** (1차 차분: LipsNet의 $\xi$ 또는 FocalPolicy의 ATV)과 **CAPS $Sm$** (고주파 성분) | 양자화 오차는 명령 action에 먼저 나타난다. 서보의 저역통과 특성이 이를 가릴 수 있으므로 명령과 실제 관절 궤적(encoder)을 따로 잰다. |
| 관찰된 결함 (정성 서술) | **jerky motion** | 현상어로 가장 많이 쓰인다(11편). 양자화 맥락의 동료 심사 사례는 QVLA(ICLR 2026)의 "jerkiness"이다. 반드시 위 지표 값과 함께 쓴다. |
| 주기적 흔들림 | **(high-frequency) oscillation** | 9편이 쓰며 QVLA도 썼다. 명령 스펙트럼($Sm$)이나 SPARC 변화로 뒷받침한다. |
| chunk 경계 | **inter-chunk discontinuity** | 13편이 쓴다. ACT나 SmolVLA처럼 chunk를 쓰는 정책이라면 경계 전후의 명령 변화량(ATV, overlap RMSE)을 따로 보고한다. |
| 목표 지나침 | **overshoot** (조작적 정의 필수) | QVLA가 양자화 결함으로 썼다. 정식 정의가 코퍼스에 없으므로 직접 정의한다. |
| 기준 대비 이탈 | **trajectory deviation from the FP reference** | "drift"는 양자화 문헌에서 activation 통계의 뜻으로 쓰이므로(QuantVLA) 피한다. |
| 원인 설명 | **quantization error propagated to actions**, **compounding error** | 현상 이름과 분리한다 (QVLA Eq. 6; ACT). |
| 피할 말 | **jitter**(주 용어로), **tremor**, **chatter/chattering**, **mode averaging**, 수식어 없는 **drift** | jitter는 timing과 color의 뜻과 겹친다(MAC, π0.5). tremor는 0편이다. chattering은 최적제어의 정식 개념이다. mode averaging은 코퍼스에서 확인되지 않았다. |

권장 문장 예: "INT4 quantization preserved task success but degraded motion smoothness: SPARC of the joint-speed profile decreased from X (FP) to Y, and the commanded actions showed higher high-frequency content (CAPS $Sm$). Qualitatively, the arm exhibited jerky motion near grasp." 동작 품질 비교에서 지연 영향을 빼려면 추론 주기와 실행 주기를 FP 조건과 같게 고정한다(OpenVLA의 int8 1.2 Hz 사례).

---

## 8. 이전(preprint 기반) 분석에서 더는 성립하지 않는 주장

1. **"양자화가 원인인 결함은 jerky/jerkiness로 가장 많이 불린다(4편)."** 근거였던 FoldQuantVLA, HoloQ-VLA, arXiv 2603.19131은 모두 preprint이다. 동료 심사 기준으로는 QVLA 1편만 남는다. 그 한 편에서도 jerkiness, oscillation, overshoot가 각 1회씩이라 우열이 없다.
2. **"average jerk L2 norm은 양자화에 직접 적용된 유일한 지표이므로 주 지표로 쓴다."** 근거인 arXiv 2603.19131은 preprint이다. 동료 심사 문헌에는 양자화 조건에서 smoothness를 잰 연구가 없다. 주 지표는 정의 원전이 동료 심사 저널에 있는 SPARC와 LDLJ로 바꿨다.
3. **"SAL이 LDLJ보다 ~10× robust"(RINSE) 인용.** preprint이다. 같은 취지의 근거는 Balasubramanian et al.(2015, JNER)의 "we recommend the use of SPARC over LDLJ"로 대체했다.
4. **"jitter, oscillation, chatter, tremor를 지표 이름으로 쓴 논문은 없다."** 동료 심사 코퍼스에서 일부 수정된다. gSDE(CoRL 2021)는 "We quantify this jitter as … continuity cost"라고 jitter를 수치화했다. IAC(ICML 2026)는 "control jitter (Jerk)"를 Jerk RMS로 쟀다. ASAP(AAAI 2026)는 "To quantify action oscillations"로 $Sm$을 썼다. 다만 지표의 이름 자체는 여전히 continuity cost, Jerk RMS, $Sm$이다.
5. **"chatter는 0편."** 동료 심사 코퍼스에서는 1편(Bang-Bang, NeurIPS 2021)이 최적제어의 정식 의미로 썼다. 동작 결함을 가리키는 뜻으로는 여전히 0편이다.
6. **"oscillation을 양자화 결함에 쓴 논문은 2편(HB-VLA, QVLA)."** HB-VLA는 preprint이다. 한 2차 사이트는 ICAART 2026 게재라고 적었지만 확인하지 못했고, ICAART는 조사 대상 학회도 아니다. 그래서 1편(QVLA)이다.
7. **"kinematic drift"(DA-PTQ)를 drift 용례의 대표로 든 것.** preprint이다. 동료 심사 양자화 논문(QuantVLA)의 drift는 동작이 아니라 activation 통계의 뜻이다.
8. 순위의 큰 줄기(smooth가 가장 넓고, 결함 현상어 중 jerky가 가장 많고, jitter는 모호하다)는 동료 심사 기준으로도 유지된다.

---

## 9. 참고: 주목할 preprint (preprint, not peer-reviewed. 집계 제외)

2026-09-25 기준으로 조사 대상 학회·저널의 게재를 확인하지 못한 논문이다. 동료 심사 문헌의 공백(양자화 조건의 정량 동작 품질)을 메우는 직접 증거가 대부분 여기에 있다.

| 논문 | arXiv | 내용 |
|---|---|---|
| From Inference Efficiency to Embodied Efficiency | [2603.19131](https://arxiv.org/abs/2603.19131) | LIBERO, int8/int4 fake quantization에서 average jerk L2 norm이 늘었다(int4에서 최대 +19.5%). |
| FoldQuantVLA | [2609.24433](https://arxiv.org/abs/2609.24433) | SO-101에서 W8A8 SmoothQuant가 "Jerky motion risked the hardware". |
| HoloQ-VLA | [2605.28803](https://arxiv.org/abs/2605.28803) | 실로봇에서 baseline의 "jerky end-effector trajectories". |
| HBVLA | [2602.13710](https://arxiv.org/abs/2602.13710) | 1-bit baseline의 "persistent arm oscillations". |
| DA-PTQ | [2604.11572](https://arxiv.org/abs/2604.11572) | "kinematic drift". |
| GROOVE | [2609.13695](https://arxiv.org/abs/2609.13695) | VLA 실행의 EEF/TCP jerk 감소. |
| RINSE | [2604.23000](https://arxiv.org/abs/2604.23000) | 데모 데이터의 SAL/TED. |
| Grad-CAPS | [2407.04315](https://arxiv.org/abs/2407.04315) | arXiv 주석은 "Accepted to IROS 2024"이지만 IEEE Xplore 페이지를 찾지 못했다. |

---

## 10. 한계

- **ICRA, IROS, RA-L, T-RO, IJRR, Science Robotics의 전수 확인은 하지 못했다.** 이 학회·저널들은 accepted list를 한 번에 받을 수 없었고, dblp와 OpenReview API는 차단되었다. 그래서 개별 검색으로 찾은 논문(CAPS, Just Round, DP의 IJRR판)만 들어갔다. 그룹 A는 이 학회들에서 과소 집계되었을 수 있다.
- 학회 virtual site의 포스터 페이지를 "accepted"의 근거로 삼았다. 철회나 불참으로 proceedings에 빠진 경우는 가려내지 못했다.
- arXiv HTML 최신판을 게재본으로 가정했다. camera-ready와 문구가 다를 수 있다.
- smooth 횟수는 대형 논문(CAPS, IAC, Legato, ASAP, LipsNet, NIAF)에서 표본만 읽었으므로 근사치이다. LipsNet은 2단 PDF를 텍스트로 뽑아서 문장이 섞였고, 참고문헌 일부가 남았다(oscillation 1회를 수동으로 뺐다).
- 표 머리글과 캡션까지 세었으므로 지표 이름(예: IAC의 "Jerk_RMS")이 부풀려진다. 그래서 순위는 논문 수 기준이다.
- 코퍼스는 검색과 accepted list 필터링으로 골랐다. 무작위 표본이 아니다. 그룹 A에는 동작 품질을 다루지 않는 압축 논문이 많아서, "용어 0회"라는 결과 자체가 이 분야의 평가 관행(성공률, 지연 위주)을 반영한다.
- (i)/(ii)/(iii) 라벨은 smooth 외 용어의 모든 문맥을 사람이 읽고 붙였다. 표에는 논문별로 나타난 라벨 종류를 요약했다.

---

## Sources

**그룹 A (검증 링크 / 전문)**
- OpenVLA — CoRL 2024: https://proceedings.mlr.press/v270/kim25c.html ; https://arxiv.org/html/2406.09246
- SQIL — ICCV 2025: https://iccv.thecvf.com/virtual/2025/poster/958 ; https://arxiv.org/html/2505.15304
- QVLA — ICLR 2026: https://iclr.cc/virtual/2026/poster/10009282 ; https://arxiv.org/html/2602.03782
- QuantVLA — CVPR 2026: https://cvpr.thecvf.com/virtual/2026/poster/39915 ; https://arxiv.org/html/2602.20309
- DeeR-VLA — NeurIPS 2024: https://proceedings.neurips.cc/paper_files/paper/2024/hash/67b0e7c7c2a5780aeefe3b79caac106e-Abstract-Conference.html ; https://arxiv.org/html/2411.02359
- EfficientVLA — NeurIPS 2025: https://neurips.cc/virtual/2025/poster/117949 ; https://arxiv.org/html/2506.10100
- VLA-Cache — NeurIPS 2025: https://neurips.cc/virtual/2025/poster/118121 ; https://arxiv.org/html/2502.02175
- LightDP — ICCV 2025: https://iccv.thecvf.com/virtual/2025/poster/1292 ; https://arxiv.org/html/2508.00697
- SP-VLA — ICLR 2026: https://iclr.cc/virtual/2026/poster/10009455 ; https://arxiv.org/html/2506.12723
- Action-aware Dynamic Pruning — ICLR 2026: https://iclr.cc/virtual/2026/poster/10008304 ; https://arxiv.org/html/2509.22093
- SpecPrune-VLA — ICML 2026: https://icml.cc/virtual/2026/poster/64525 ; https://arxiv.org/html/2509.05614
- Sparse ActionGen — ICML 2026: https://icml.cc/virtual/2026/poster/65503 ; https://arxiv.org/html/2601.12894
- Consistency Policy — RSS 2024: https://www.roboticsproceedings.org/rss20/p071.html ; https://arxiv.org/html/2405.07503
- Just Round — ICRA 2023: https://ieeexplore.ieee.org/document/10160293/ ; https://arxiv.org/html/2210.08065

**그룹 B**
- ACT — RSS 2023: https://www.roboticsproceedings.org/rss19/p016.html ; https://arxiv.org/html/2304.13705
- Diffusion Policy — RSS 2023: https://www.roboticsproceedings.org/rss19/p026.html ; IJRR: https://doi.org/10.1177/02783649241273668 ; https://arxiv.org/html/2303.04137
- FAST — RSS 2025: https://www.roboticsproceedings.org/rss21/p012.html ; https://arxiv.org/html/2501.09747
- π0 — RSS 2025: https://www.roboticsproceedings.org/rss21/p010.html ; https://arxiv.org/html/2410.24164
- π0.5 — CoRL 2025: https://proceedings.mlr.press/v305/black25a.html ; https://arxiv.org/html/2504.16054
- CAPS — ICRA 2021: https://doi.org/10.1109/ICRA48506.2021.9561138 ; https://arxiv.org/html/2012.06644
- BID — ICLR 2025: https://iclr.cc/virtual/2025/poster/28245 ; https://arxiv.org/html/2408.17355
- RTC — NeurIPS 2025: https://proceedings.neurips.cc/paper_files/paper/2025/hash/300ccb2187dedd4edcc07f7e76d8e553-Abstract-Conference.html ; https://arxiv.org/html/2506.07339
- VQ-VLA — ICCV 2025: https://iccv.thecvf.com/virtual/2025/poster/1332 ; https://arxiv.org/html/2507.01016
- BEAST — NeurIPS 2025: https://neurips.cc/virtual/2025/poster/115779 ; https://arxiv.org/html/2506.06072
- Q-FAT — NeurIPS 2025: https://neurips.cc/virtual/2025/poster/120026 ; https://arxiv.org/html/2503.14259
- NIAF — ICML 2026: https://icml.cc/virtual/2026/poster/64538 ; https://arxiv.org/html/2603.01766
- Implicit Action Chunking (IAC) — ICML 2026: https://icml.cc/virtual/2026/poster/62846 ; https://arxiv.org/html/2605.19592
- Mixture of Horizons — ICML 2026: https://icml.cc/virtual/2026/poster/66600 ; https://arxiv.org/html/2511.19433
- FocalPolicy — ICML 2026: https://icml.cc/virtual/2026/poster/66520 ; https://arxiv.org/html/2605.15944
- Understanding BC with Action Quantization — ICML 2026: https://icml.cc/virtual/2026/poster/65817 ; https://arxiv.org/html/2603.20538
- Masked Action Chunking (REMAC) — ICLR 2026: https://iclr.cc/virtual/2026/poster/10007187 ; https://arxiv.org/html/2601.20130
- Adaptive Action Chunking — CVPR 2026: https://cvpr.thecvf.com/virtual/2026/poster/39692 ; https://arxiv.org/html/2604.04161
- Legato (Learning Native Continuation) — RSS 2026: https://www.roboticsproceedings.org/rss22/p058.html ; https://arxiv.org/html/2602.12978
- OAT — RSS 2026: https://www.roboticsproceedings.org/rss22/p075.html ; https://arxiv.org/html/2602.04215
- Streaming Flow Policy — CoRL 2025: https://proceedings.mlr.press/v305/jiang25a.html ; https://arxiv.org/html/2505.21851
- gSDE — CoRL 2021: https://proceedings.mlr.press/v164/raffin22a.html ; https://arxiv.org/html/2005.05719
- Bang-Bang — NeurIPS 2021: https://proceedings.neurips.cc/paper/2021/hash/e46be61f0050f9cc3a98d5d2192cb0eb-Abstract.html ; https://arxiv.org/html/2111.02552
- VQ-BeT — ICML 2024: https://icml.cc/virtual/2024/poster/33379 ; https://arxiv.org/html/2403.03181
- LipsNet — ICML 2023: https://proceedings.mlr.press/v202/song23b.html
- ASAP — AAAI 2026: https://doi.org/10.1609/aaai.v40i27.39432 ; https://arxiv.org/html/2601.18479

**그룹 C**
- Flash & Hogan 1985: https://doi.org/10.1523/JNEUROSCI.05-07-01688.1985
- Hogan & Sternad 2009: https://doi.org/10.3200/35-09-004-RC ; https://pmc.ncbi.nlm.nih.gov/articles/PMC3470860/
- Balasubramanian et al. 2012: https://doi.org/10.1109/TBME.2011.2179545
- Balasubramanian et al. 2015: https://doi.org/10.1186/s12984-015-0090-9 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC4674971/

**Accepted list (검증에 사용)**
- https://iclr.cc/virtual/2026/papers.html , https://iclr.cc/virtual/2025/papers.html
- https://neurips.cc/virtual/2025/papers.html , https://neurips.cc/virtual/2024/papers.html
- https://icml.cc/virtual/2026/papers.html , https://icml.cc/virtual/2024/papers.html
- https://cvpr.thecvf.com/virtual/2026/papers.html , https://iccv.thecvf.com/virtual/2025/papers.html
- https://www.roboticsproceedings.org/rss19/ , https://www.roboticsproceedings.org/rss20/ , https://www.roboticsproceedings.org/rss21/ , https://www.roboticsproceedings.org/rss22/
- https://proceedings.mlr.press/v164/ , https://proceedings.mlr.press/v202/ , https://proceedings.mlr.press/v270/ , https://proceedings.mlr.press/v305/
