# 양자화가 로봇 동작 품질에 미치는 영향: 문헌 조사

조사 시점: 2026-09-25. 대상: VLA(OpenVLA, pi0/pi0.5, SmolVLA, GR00T N1.x 등), diffusion/flow policy, ACT, RL policy.
질문: 제어 모델을 양자화하면 성공률뿐 아니라 **동작 품질**(jitter/tremor/oscillation, 부드럽지 않은 궤적, gripper chattering, drift, overshoot, action-chunk 경계 불연속)이 측정 가능한 수준으로 달라지는가?

모든 항목은 실제로 열어 본 URL에 근거한다. 인용은 원문 그대로이거나 원문에 가깝게 옮긴 것이다. 원문에서 확인하지 못한 수치는 넣지 않았다.

> **게재 상태 주의 (2026-09-25 확인).** 각 표의 "게재 상태" 열은 학회 proceedings, PMLR, roboticsproceedings.org, 학회 virtual site의 accepted paper 목록, DOI로 확인한 결과이다. 확인하지 못한 것은 `preprint`로 적었다.
> - **양자화가 동작 품질을 떨어뜨린다는 직접 증거는 대부분 preprint에만 있다.** 아래 (a) 표의 5편과 (d)의 average jerk L2 norm(arXiv 2603.19131)이 모두 그렇다.
> - 동료 심사 논문 중 양자화가 원인인 동작 결함을 서술한 것은 **QVLA (ICLR 2026, arXiv 2602.03782)** 1편이다. 시뮬레이션 rollout에서 "localized oscillation or jerkiness", 그리퍼의 "overshoot"를 정성적으로 적었다.
> - 양자화 조건에서 smoothness나 jerk를 수치로 잰 동료 심사 논문은 찾지 못했다.
> - 동료 심사 기준의 용어 정리와 지표 정의는 `motion-artifact-terminology.md`에 있다.

---

## 요약

**알려진 것**

1. **양자화가 동작 품질을 떨어뜨린다는 직접 정량 증거는 있으나, 한 편(시뮬레이션)에 가깝다.** *From Inference Efficiency to Embodied Efficiency* (arXiv 2603.19131)는 LIBERO에서 pi0, pi0.5, MolmoAct의 가중치를 int8/int4 fake-quantization으로 양자화했다. 성공률 하락은 최대 −1.8%에 그쳤지만, int4에서 average jerk L2 norm이 pi0 +19.5%, MolmoAct +14.1%, pi0.5 +3.5% 늘었다. int8에서는 변화가 거의 없었다(pi0 +0.4%, pi0.5 −3.4%, MolmoAct +0.8%). 논문 결론은 "quantization largely preserves task success rate … it introduces degradation in motion smoothness"이다.
2. **실제 로봇, 그중 SO-101에서 나온 정성적 직접 증거가 있다.** *FoldQuantVLA* (arXiv 2609.24433)의 Table V에서, SO-101 위 GR00T N1.7을 ModelOpt W8A8 SmoothQuant(static per-tensor scale)로 양자화하자 "Jerky motion risked the hardware"라는 이유로 평가가 중단되었다. 같은 설정의 median action cosine은 **0.99892**로 FP와 거의 같았다. 즉 오프라인 action 유사도가 높아도 실제 로봇에서는 jerky 동작이 나올 수 있다.
3. **다른 실로봇 사례도 정성적 기술에 머문다.** HoloQ-VLA (arXiv 2605.28803)는 ARX R5 양팔 로봇에서 QuantVLA(W4A8) baseline의 "jerky end-effector trajectories"와 open-loop action "spikes"를 보고했다. HB-VLA (arXiv 2602.13710)는 Mobile ALOHA에서 1-bit BiLLM baseline이 "persistent arm oscillations"를 보였다고 적었다. 둘 다 제안 기법이 이를 줄인다는 맥락이고, jitter를 수치 지표로 재지는 않았다.
4. **성공률만으로는 양자화 차이를 가릴 수 없다는 점이 명시적으로 보고되었다.** VLAQuantBench (arXiv 2609.25376)에서 OpenVLA-OFT의 여러 양자화 방법(AWQ, NF4, LLM.int8(), SmoothQuant)은 모두 LIBERO-Spatial 98–99%를 기록했지만 action deviation은 서로 달랐다. 저자들은 이를 "near-ceiling masking"이라 불렀다.
5. **간접 증거는 풍부하다.** action 이산화(FAST tokenizer가 jerk를 28.0–50.6% 늘림, 256-bin binning의 고주파 실패), chunk 경계 불연속, 추론 지연이 동작 품질을 바꾼다는 증거가 여러 편 있다.

**빠져 있는 것**

- **FP와 INT8/INT4를 같은 조건에서 비교하면서 jerk, SPARC 같은 smoothness 지표를 실로봇에서 정량 측정한 연구는 찾지 못했다.** 실로봇 증거는 모두 정성적 기술(영상, "jerky", "oscillation")이거나 성공률뿐이다.
- SO-101/LeRobot 커뮤니티(GitHub issue, 포럼)에서 "양자화 후 떨림"을 보고한 사례는 찾지 못했다. SO-101 INT8 연구(ACT TensorRT INT8, vla.simd int8)는 성공률만 보고한다.
- gripper chattering, overshoot, chunk 경계 불연속을 양자화 조건별로 측정한 연구도 찾지 못했다.
- 직접 정량 증거(2603.19131)는 fake quantization, 시뮬레이션, 단일 논문이라는 한계가 있다. 이 논문의 jerk는 Table II에서 모델과 bit에 따라 부호와 크기가 달라서(pi0.5 int8은 −3.4%), 효과가 모델마다 다를 수 있다.

**직접 증거의 강도 평가: 약함–중간.** 방향성(양자화 → jerk 증가, 특히 4-bit, 그리고 성공률은 이를 드러내지 못함)은 여러 출처가 같은 쪽을 가리킨다. 하지만 실로봇 정량 측정은 사실상 비어 있다.

---

## (a) 양자화가 jitter나 비매끄러운 동작을 일으켰다는 직접 증거

| 논문 | 연도 / ID | 게재 상태 | 모델 | 정밀도 | 설정 | 동작에 관한 관찰 | 링크 |
|---|---|---|---|---|---|---|---|
| From Inference Efficiency to Embodied Efficiency: Revisiting Efficiency Metrics for VLA Models (Li et al.) | 2026 / arXiv 2603.19131 (preprint) | preprint | pi0, pi0.5, MolmoAct | int8, int4 (weight fake quantization: quantize 후 dequantize) | Sim: LIBERO | Table II: 성공률 변화는 worst-case −1.8%인데 "average jerk L2 norm J̄ increases … int4 quantization yielding particularly pronounced jerk increases of up to +19.5% (π₀), +14.1% (MolmoAct), and +3.5% (π₀.₅)". int4 pi0는 task completion time +2.8%, joint-space path length +4.4%. int8은 jerk 변화가 작다(pi0 +0.4%, pi0.5 −3.4%, MolmoAct +0.8%). 실로봇 실험은 없다. | https://arxiv.org/html/2603.19131 |
| FoldQuantVLA: Native Low-Bit Quantization of VLA Models via Consistent Folding (Ho et al.) | 2026 / arXiv 2609.24433 | preprint | GR00T N1.7 (그 밖에 N1.5, N1.6, pi0.5) | baseline: ModelOpt W8A8 SmoothQuant, W4A16 AWQ. 제안: W8A8, W4A4 | **Real: SO-101** (Orin), LIBERO, SimplerEnv | Table V 각주: "‡Stopped after T4 because jerky motion risked the hardware". 본문: "ModelOpt W8A8 SmoothQuant uses static per-tensor scales and reached 30.0% on T4 versus 70.0% for BF16 … Jerky motion risked the hardware … Its median SO-101 action cosine is 0.99892 despite poor task performance." 정량 smoothness 지표는 없다. | https://arxiv.org/html/2609.24433 |
| HoloQ-VLA: Uniform W4A4 Quantization of VLA Models (Wang et al.) | 2026 / arXiv 2605.28803 | preprint | pi0.5, GR00T N1.5 | W4A4 (제안), QuantVLA W4A8 (baseline) | Real: ARX R5 양팔 (5개 task), Sim: LIBERO | 실로봇 결과 절: "QuantVLA produces jerky end-effector trajectories that accumulate over long horizons into task failures, whereas HoloQ-VLA yields substantially smoother actions." Appendix A.5, Fig. 8: QuantVLA는 "noticeable spikes and abrupt deviations in several action dimensions"를 보였다. 저자는 "improved action stability may reduce control jitter"라고 추정한다. 평가는 궤적 시각화에 의존한 정성적 평가다. | https://arxiv.org/html/2605.28803 |
| HB-VLA: Pushing 1-Bit Post-Training Quantization for VLA Models (Yan et al.) | 2026 / arXiv 2602.13710 (v2) | preprint (ICAART 2026 게재 주장 미확인, 조사 대상 학회 아님) | OpenVLA-OFT (실로봇), pi0, CogACT | 1-bit PTQ (BiLLM, HBLLM, HB-VLA) | Real: Mobile ALOHA, Sim: LIBERO, SIMPLER | Mobile ALOHA 결과: "BiLLM performs worst and exhibits persistent arm oscillations during execution." 서론: 작은 action 편차가 "unstable grasps, oscillatory motions, or large trajectory drift"로 증폭될 수 있다. 진동은 정성적으로만 기술되었다. | https://arxiv.org/html/2602.13710 |
| DA-PTQ: Drift-Aware PTQ for Efficient VLA Models (Xu et al.) | 2026 / arXiv 2604.11572 | preprint | CogACT | W4A8 | Sim: SimplerEnv (WidowX, Google Robot) | 초록: PTQ의 "quantization perturbations at the vision-language-to-action interface are progressively amplified, leading to kinematic drift". 서론: PTQ가 "in some cases unstable control behaviors"를 낳는다. Appendix B: "a hallmark of severe quantization degradation in continuous control is the emergence of high-variance, high-frequency oscillations". 제안 기법의 action 곡선(Fig. 4–6)이 매끄럽다는 정성적 주장이다. baseline의 진동을 수치로 재지는 않았다. | https://arxiv.org/html/2604.11572v1 |

**해석.** (a)의 실로봇 항목은 모두 **baseline 양자화 기법**에서 나타난 현상을 제안 기법의 장점으로 기술한 것이다. 사전에 정한 smoothness 지표로 FP와 비교한 것이 아니다. 정량 비교는 2603.19131(시뮬레이션)이 사실상 유일하다.

---

## (b) 양자화로 성공률이 바뀌었지만 동작 품질은 측정하지 않은 연구

| 논문 | 연도 / ID | 게재 상태 | 모델 | 정밀도 | 설정 | 관찰 (동작 품질 관련) | 링크 |
|---|---|---|---|---|---|---|---|
| VLAQuantBench: Closed-Loop Evaluation of PTQ for VLA Models (Xu et al.) | 2026 / arXiv 2609.25376 | preprint | OpenVLA-OFT, pi0, pi0.5, X-VLA | W3, W4, W8, W4A4, W4A8, W8A8 | Sim: LIBERO, SIMPLER, CALVIN, VLABench. Real: Franka Research 3 | smoothness는 재지 않았다. 대신 matched-observation replay로 **action-chunk MAE**, executed action MAE, **gripper bias**(부호가 있는 gripper 명령 편차)를 측정했다(Table 4). §5.5: 성공률이 천장에 가까우면 action fidelity 차이를 "cannot resolve"한다. OpenVLA-OFT의 AWQ, NF4, LLM.int8(), SmoothQuant가 모두 98–99%였다. Franka 실로봇: W8/W8A8은 BF16 대비 6%p 이내, W4A8은 18–40%p 하락, W3은 6–16%. | https://arxiv.org/html/2609.25376 |
| OpenVLA: An Open-Source VLA Model (Kim et al.) | 2024 / arXiv 2406.09246 | **CoRL 2024** ([PMLR v270](https://proceedings.mlr.press/v270/kim25c.html)) | OpenVLA 7B | bf16, int8, int4 (bitsandbytes) | Real: WidowX (BridgeData V2, 8 task, 80 rollouts) | Table 2: bf16 71.3%, int8 58.1%, int4 71.9%. int8 하락의 원인을 지연으로 보았다: "we can only run the model at 1.2Hz, which significantly changes the system dynamics compared to the training dataset for the 5Hz non-blocking controller." 동작 품질에 대한 언급은 없다. | https://arxiv.org/html/2406.09246v3 |
| Saliency-Aware Quantized Imitation Learning (SQIL) (Park et al.) | 2025 / arXiv 2505.15304 | **ICCV 2025** ([poster](https://iccv.thecvf.com/virtual/2025/poster/958)) | OpenVLA | INT4 (QAT, AWQ/QuaRot baseline) | Sim: LIBERO. Real: UR5 | Fig. 1: 양자화 오차는 대부분의 timestep에서 작지만 "Certain critical states … experience large deviations in actions due to quantization errors"이고, 이것이 잡기나 놓기 실패로 이어진다. 편차는 FP 대비 action L2로 쟀다. UR5에서 INT4 77%, FP 79%. smoothness 지표는 없다. | https://arxiv.org/html/2505.15304v1 |
| DyQ-VLA: Temporal-Dynamic-Aware Quantization for Embodied VLA Models (Zheng et al.) | 2026 / arXiv 2603.07904 | preprint | OpenVLA | W4 + 동적 activation 2/4/8/16-bit | Sim: LIBERO. Real (grasping, sequential) | §III-A: "coarse movements are naturally robust to local noise … fine-grained manipulations are highly sensitive". 양자화 민감도의 proxy로 **angular jerk**(연속 rotation action의 차이)와 motion fineness를 썼다. 다만 이 값은 동작 품질을 평가한 결과가 아니라 bit 할당에 쓰는 입력이다. | https://arxiv.org/html/2603.07904v1 |
| QuantVLA: Scale-Calibrated PTQ for VLA Models (Zhang et al.) | 2026 / arXiv 2602.20309 | **CVPR 2026** ([poster](https://cvpr.thecvf.com/virtual/2026/poster/39915)) | DiT action head를 가진 VLA (pi0.5, GR00T N1.5 등) | low-bit W/A | Sim: LIBERO | 성공률과 메모리만 보고한다. 이후 HoloQ-VLA는 실로봇에서 이 기법의 jerky 궤적을 보고했다((a) 참조). | https://arxiv.org/abs/2602.20309 |
| BitVLA: 1-bit VLA Models for Robotics Manipulation (Wang et al.) | 2025 / arXiv 2506.07530 | preprint | BitVLA, OpenVLA, OpenVLA-OFT | 1-bit (ternary). baseline INT8/INT4 PTQ | Sim: LIBERO. Real: Franka | Table II: OpenVLA INT8 76.9%, INT4 72.7%. OpenVLA-OFT INT8 96.7%, INT4 96.9%. 동작 품질 언급은 없다. | https://arxiv.org/html/2506.07530v2 |
| ActQuant: Sub-4-bit Action-Guided Quantization for VLA Models (Akbari et al.) | 2026 / arXiv 2605.24011 | preprint | VLA | 2–3 bit | Sim: LIBERO. Real: UR3 | 성공률, 메모리, 지연만 보고한다. 동작 품질 기술은 없다. | https://arxiv.org/html/2605.24011 |
| Bimanual Manipulation Within an 8 GB Budget: Zero-Copy Sensing and Quantized ACT on an Entry-Level Jetson (Singh et al.) | 2026 / arXiv 2608.03938 | preprint | ACT | TensorRT FP16, INT8 | **Real: 양팔 SO-101** | FP32/FP16/INT8 성공률은 19/20, 18/20, 19/20이다. TensorRT INT8 calibration은 "quantizes the ResNet18 backbone but accepts zero of 145 transformer layers". 즉 실제로는 백본만 INT8이 되었다. 동작 품질은 측정하지 않았다. | https://arxiv.org/abs/2608.03938 |
| vla.simd: Efficient CPU Inference for Language-Conditioned Manipulation (Nguyen et al.) | 2026 / arXiv 2609.24274 | preprint | IMPACT (제안), ACT, DP, Octo-Small, SmolVLA 등 | int8 (symmetric, per-channel weight, dynamic activation) | **Real: SO-101** | Table VI: fp32 대비 int8 성공률은 90→85, 85→95, 60→50이다. 저자 스스로 int8이 시뮬레이션 성공률과 장기 과제에 미치는 영향을 "unmeasured"라고 적었다. 동작 품질 지표는 없다. | https://arxiv.org/html/2609.24274 |
| When Faster VLA Deployment Changes Closed-Loop Behavior: SmolVLA Across PyTorch and ONNX Variants (Islam) | 2026 / arXiv 2609.14146 | preprint | SmolVLA (smolvla_libero) | "requested" FP16/INT8 ONNX | Sim: LIBERO | 초록: requested-INT8 ONNX에서 Spatial 성공률이 70→40%로 떨어졌지만, graph audit 결과 "byte-identical FP32 graphs, so the requested-INT8 row is not operator-level INT8 quantization"이었다. **"INT8로 export했다"는 것이 실제 INT8 연산을 뜻하지 않을 수 있다**는 방법론상 경고다. 동작 품질 지표는 없다. | https://arxiv.org/abs/2609.14146 |
| LiteVLA-Edge: Quantized On-Device Multimodal Control for Embedded Robotics | 2026 / arXiv 2603.03380 | preprint | SmolVLM-256M 기반 | 4-bit GGUF (Q4_K_M) | Jetson AGX Orin | §VI-B: "A common critique of 4-bit quantization in robotics is the potential for 'Action Jitter' or numerical drift in motor coordinates." 반박 근거로 든 것은 추론 **지연**의 표준편차(σ=0.125 ms)뿐이고, action 값의 안정성은 측정하지 않았다. | https://arxiv.org/html/2603.03380 |
| QuaRL: Quantization for Reinforcement Learning (Krishnan, Lam et al.) | 2019–2022 / arXiv 1910.01055 | 미확인 (게재처 검증 안 함) | A2C, DDPG, DQN, PPO, D4PG | int8, fp16, 2–32 bit PTQ/QAT | Sim: MuJoCo, PyBullet 등 | reward 기준으로 양자화 영향을 평가했다. 동작 smoothness는 측정하지 않았다. | https://github.com/harvard-edge/QuaRL |
| Control of Microrobots with RL under On-Device Compute Constraints (Liu et al.) | 2025 / arXiv 2512.24740 | preprint | RL locomotion policy | Int8 (per-tensor, per-feature) | MCU 탑재 microrobot | 초록: 더 높은 업데이트 주기를 위해 Int8을 검토했다. 초록 수준에서 smoothness나 진동 수치는 확인하지 못했다. | https://arxiv.org/abs/2512.24740 |

---

## (c) 간접 증거: action 이산화, 수치 정밀도, 지연과 비동기 실행이 smoothness에 미치는 영향

### c-1. Action 이산화와 tokenizer

| 논문 | 연도 / ID | 게재 상태 | 관찰 | 링크 |
|---|---|---|---|---|
| From Inference Efficiency to Embodied Efficiency (Table III) | 2026 / arXiv 2603.19131 | preprint | pi0 + **FAST** tokenizer는 "generates less smooth actions, even increasing the average jerk L2 norm by 28.0% to 50.6%, while reducing completion time by 1.5% to 5.6%"이다(LIBERO). 같은 논문에서 visual token pruning 비율을 12%→56%→78%로 올리면 pi0.5의 jerk가 비가지치기 대비 204%→337%→375%가 되었다(Fig. 5). 가중치 pruning은 성공률 −0.2% 조건에서 EE path length를 +46.2% 늘렸다(Table I). 압축 전반이 "성공률은 유지, 동작 품질은 저하"라는 같은 패턴을 보인다. | https://arxiv.org/html/2603.19131 |
| FAST: Efficient Action Tokenization for VLA Models (Pertsch et al.) | 2025 / arXiv 2501.09747 | **RSS 2025** ([p012](https://www.roboticsproceedings.org/rss21/p012.html)) | per-dimension, per-timestep **binning**(RT-2/OpenVLA 방식)은 고주파 데이터에서 실패한다. §IV Fig. 3: 주파수가 높아지면 모델이 "simply copies the first action"에 빠진다. §VI-B Fig. 6: 20 Hz, 50 Hz task에서 naive tokenization 정책은 "unable to make progress". FAST 출력의 smoothness 자체는 측정하지 않았다. | https://arxiv.org/html/2501.09747v1 |
| OpenVLA | 2024 / arXiv 2406.09246 | **CoRL 2024** ([PMLR v270](https://proceedings.mlr.press/v270/kim25c.html)) | action을 차원별 **256 bins**로 이산화하고, bin 폭은 학습 데이터 action의 1st–99th quantile 구간을 균등 분할해 정한다. 이 해상도 자체가 action에 하한 양자화 오차를 둔다(smoothness 측정은 없다). | https://arxiv.org/html/2406.09246v3 |
| VQ-VLA (Wang et al.) | 2025 / arXiv 2507.01016 (ICCV 2025) | **ICCV 2025** ([poster](https://iccv.thecvf.com/virtual/2025/poster/1332)) | 초록은 VQ tokenizer가 "smoother and more coherent action outputs"를 낸다고 주장한다. 그러나 본문에 smoothness의 정량 비교는 없다(성공률과 속도만). | https://arxiv.org/html/2507.01016v1 |
| Is Bang-Bang Control All You Need? (Seyde et al.) | 2021 / NeurIPS | **NeurIPS 2021** (proceedings) | 극단값 두 개로 이산화한 Bernoulli(bang-bang) 정책도 벤치마크 성능은 SOTA 수준이다. 저자는 이것이 "in contrast to robotic hardware, where energy and maintenance cost affect controller choices"라고 지적한다. 거친 action 이산화가 보상과 성공 지표에는 드러나지 않을 수 있다는 고전적 근거다. | https://proceedings.neurips.cc/paper/2021/hash/e46be61f0050f9cc3a98d5d2192cb0eb-Abstract.html |

### c-2. Action chunk 경계와 지연

| 논문 | 연도 / ID | 게재 상태 | 관찰 | 링크 |
|---|---|---|---|---|
| ACT: Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (Zhao et al.) | 2023 / arXiv 2304.13705 | **RSS 2023** ([p016](https://www.roboticsproceedings.org/rss19/p016.html)) | §IV-A: "A naïve implementation of action chunking can be sub-optimal: a new environment observation is incorporated abruptly every k steps and can result in jerky robot motion." 이를 temporal ensembling으로 완화했다. | https://arxiv.org/html/2304.13705 |
| Real-Time Execution of Action Chunking Flow Policies (RTC) (Black et al.) | 2025 / arXiv 2506.07339 | **NeurIPS 2025** ([proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/300ccb2187dedd4edcc07f7e76d8e553-Abstract-Conference.html)) | §3: chunk 사이 전략이 바뀌는 mode-jumping 때문에 "jerky behavior resulting from discontinuities between chunks"가 생기고, 이는 "worsened dramatically with higher delays". Fig. 1은 실로봇 관절의 위치, 속도, 가속도 곡선이다. App. A.2는 "maximum acceleration (second discrete difference)"를 OOD proxy로 쓴다. temporal ensembling은 "reduces the acceleration but produces poor actions"(Fig. 2). | https://arxiv.org/html/2506.07339v1 |
| SmolVLA 블로그 (Hugging Face) | 2025 | 블로그 (비심사) | action expert의 causal self-attention이 temporal smoothness를 높인다. "jittery predictions can result in unsafe or unstable behavior". 비동기 추론에서 "Overlapping actions from successive chunks are stitched with a simple merge rule to avoid jitter". | https://github.com/huggingface/blog/blob/main/smolvla.md |
| GROOVE: Geometry-Guided Reduction of Operational-Space Jerk in VLA Execution (Yun et al.) | 2026 / arXiv 2609.13695 | preprint | 초록: chunk 내부와 replanning 경계의 jerk가 "can induce oscillatory motion and sharp actuator transients". 후처리 QP로 LIBERO의 EEF jerk를 병진 −33.02%, 회전 −43.42% 줄였다. UR5e 50쌍에서는 TCP jerk를 −16.39%, −19.49%, joint current slew를 −29.09% 줄였다. | https://arxiv.org/abs/2609.13695 |
| OpenVLA (Table 2) | 2024 / arXiv 2406.09246 | **CoRL 2024** ([PMLR v270](https://proceedings.mlr.press/v270/kim25c.html)) | int8(bitsandbytes)이 오히려 느려져(1.2 Hz) 5 Hz 학습 dynamics와 어긋났고, 성공률이 71.3→58.1%로 떨어졌다. 양자화 커널 속도가 폐루프 dynamics를 바꿀 수 있다는 교란 변수다. VLAQuantBench(Table 10)도 RTX 4090에서 AWQ와 SmoothQuant 경로가 BF16보다 느렸다고 보고했다("Memory reduction does not imply lower latency"). | https://arxiv.org/html/2406.09246v3 |

### c-3. 수치 정밀도 / action 유사도 지표의 한계

- **FoldQuantVLA**: ModelOpt W8A8 SQ는 median action cosine 0.99892, W4A16 AWQ는 mean 0.99980으로 FP와 매우 가깝다. 그런데도 실로봇 성공률은 30–40%로 떨어졌고, 앞의 것은 jerky 동작을 보였다. **per-step action cosine은 폐루프 동작 품질을 대변하지 못한다.** https://arxiv.org/html/2609.24433
- **VLAQuantBench**: W4A4에서 두 layer 집합의 오차가 비가산적으로 상호작용했다(median ratio 2.90, Fig. 2). layer를 **더 많이** 양자화하자 오히려 action-chunk MAE가 0.514→0.390으로 줄고 성공률이 7.0→70.5%로 회복되었다(Table 4). 오차가 layer를 늘릴수록 단조롭게 커진다고 가정하면 안 된다. https://arxiv.org/html/2609.25376
- **DyQ-VLA**: 양자화 오차는 식 (3)의 Jacobian 누적으로 시간에 따라 전파된다. 거친 이동 구간은 강건하고 정밀 조작 구간은 민감하다. https://arxiv.org/html/2603.07904v1

---

## (d) smoothness와 jitter를 정량화하는 데 쓰인 지표

| 지표 | 정의 / 출처 | 사용 예 | 출처 게재 상태 | 링크 |
|---|---|---|---|---|
| Average jerk L2 norm J̄ | J = f⁴/(T−2) · Σ‖q̇_{t+1} − 2q̇_t + q̇_{t−1}‖² (관절 속도의 2차 차분, f = 제어 주파수) (§III-B) | 양자화, pruning, FAST 비교 | preprint | https://arxiv.org/html/2603.19131 |
| Average action rate R | R = 1/(T−1) · Σ‖a_{t+1} − a_t‖₂ (연속 명령 변화량, action-delta 기반) | 같은 논문 | preprint | https://arxiv.org/html/2603.19131 |
| End-effector / joint-space path length | L_ee = Σ‖p_{t+1} − p_t‖, L_joint = Σ‖q_{t+1} − q_t‖. 불필요한 움직임과 drift를 반영한다. | 같은 논문 | preprint | https://arxiv.org/html/2603.19131 |
| Task completion time | τ = T/f | 같은 논문 | preprint | https://arxiv.org/html/2603.19131 |
| EEF/TCP jerk (병진·회전 분리), joint current slew | 3차 미분 기반 jerk, 모터 전류 변화율 | GROOVE (LIBERO, UR5e) | preprint | https://arxiv.org/abs/2609.13695 |
| Max acceleration (2차 이산 차분) | chunk 경계 불연속의 proxy | RTC App. A.2 | **NeurIPS 2025** ([proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/300ccb2187dedd4edcc07f7e76d8e553-Abstract-Conference.html)) | https://arxiv.org/html/2506.07339v1 |
| Angular jerk 𝒥_t | ‖a_t^rot − a_{t−1}^rot‖ / ν_max | DyQ-VLA (bit 할당용) | preprint | https://arxiv.org/html/2603.07904v1 |
| Action-chunk MAE, executed-action MAE, gripper bias (matched-observation replay) | 같은 관측과 같은 flow noise에서 FP 대비 action 오차, gripper 명령의 부호 있는 편향 | VLAQuantBench Table 4 | preprint | https://arxiv.org/html/2609.25376 |
| Action cosine similarity | per-step FP 대비 cosine. 폐루프 품질과 괴리가 확인되었다. | FoldQuantVLA | preprint | https://arxiv.org/html/2609.24433 |
| SPARC (spectral arc length) | 속도 프로파일의 정규화 Fourier magnitude spectrum의 arc length. 음수이며 0에 가까울수록 매끄럽다. 저자들은 "we recommend the use of SPARC over LDLJ"(LDLJ는 잡음에 민감하다고 봄). | 운동재활 분야 표준 (Balasubramanian et al., 2015) | **J. NeuroEng. Rehabil. 2015** (심사 저널) | https://pmc.ncbi.nlm.nih.gov/articles/PMC4674971/ |
| SAL + Trajectory-Envelope Distance (TED) | 데모 궤적의 smoothness 점수. SAL이 LDLJ보다 "~10× more robust to noise"라고 주장한다. 정책 rollout이 아니라 데이터 선별에 쓴다. | RINSE (Kulkarni et al., 2026, arXiv 2604.23000) | preprint | https://arxiv.org/html/2604.23000v1 |

---

## 연구 공백과 시사점

SO-101 팔에서 FP와 INT8/INT4 VLA 제어를 **동작 품질** 관점에서 비교하는 연구에 대한 시사점이다(엣지 디바이스와 지연은 주제가 아님).

1. **공백은 분명하다.** 실로봇에서 FP 대 INT8/INT4를 같은 조건으로 두고 jerk, SPARC, action rate, gripper chattering을 정량 비교한 공개 연구는 찾지 못했다. SO-101에서는 "jerky motion risked the hardware"라는 정성적 기록(FoldQuantVLA, GR00T N1.7, W8A8 SmoothQuant)과 성공률만 있는 INT8 연구(ACT TensorRT, vla.simd)가 전부다. 시뮬레이션 정량 증거(2603.19131)는 fake quantization이다.
2. **성공률은 보조 지표로만 쓰는 편이 안전하다.** 2603.19131(성공률 −1.8% 이내, jerk +19.5%), VLAQuantBench("near-ceiling masking"), FoldQuantVLA(action cosine 0.999인데 jerky)가 모두 같은 결론을 가리킨다.
3. **권장 지표 세트.** 관절 jerk L2(2603.19131 정의), SPARC(관절 또는 EEF 속도), action rate와 action-delta 분산, chunk 경계 전후의 가속도 불연속(RTC 방식), gripper 명령의 부호 전환 횟수(chattering), FP 궤적 대비 EE path length와 최종 위치 오차(drift), matched-observation replay에서의 action-chunk MAE(VLAQuantBench 방식). 실제 관절 궤적(모터 encoder)과 명령 action을 **따로** 기록해야 한다. 명령의 jitter가 서보의 저역통과 특성 때문에 실제 동작에서는 가려질 수 있기 때문이다.
4. **교란 변수를 통제해야 한다.** (i) 양자화 커널 속도가 폐루프 주기를 바꾸는 효과(OpenVLA int8의 1.2 Hz 사례). 지연을 주제에서 빼려면 추론 주기와 실행 주기를 고정하거나 동기 실행으로 맞춰야 한다. (ii) "INT8 export"가 실제로 INT8 연산인지 graph를 검사해야 한다(2609.14146, 2608.03938의 TensorRT 사례). (iii) flow/diffusion policy는 noise seed를 고정해야 한다(VLAQuantBench 방식). (iv) chunk 크기와 temporal ensembling 설정을 FP와 양자화 조건에서 같게 둬야 한다(ACT, SmolVLA의 chunk fusion이 양자화 jitter를 가릴 수 있음).
5. **양자화 방식을 구분해야 한다.** weight-only(W8, W4A16)와 W8A8, W4A4는 결과가 크게 다르다. static per-tensor activation scale이 가장 위험 신호였다(FoldQuantVLA). action head와 출력 projection을 보호하는지도 따로 봐야 한다(VLAQuantBench: 28,672-parameter output projection 하나가 W4A8에서 82%p 하락을 설명). layer 범위에 따라 결과가 비단조적이라는 점도 고려해야 한다.
6. **구간별로 분석해야 한다.** DyQ-VLA와 SQIL은 오차가 grasp, place 같은 정밀 구간에 집중된다고 보고한다. 에피소드 전체 평균만 보지 말고 접근, 잡기, 운반, 놓기 구간별로 smoothness를 나눠 보고하면 기여가 분명해진다.

---

## Sources

- From Inference Efficiency to Embodied Efficiency (arXiv 2603.19131): https://arxiv.org/html/2603.19131 — 게재 상태: preprint
- FoldQuantVLA (arXiv 2609.24433): https://arxiv.org/html/2609.24433 — 게재 상태: preprint
- HoloQ-VLA (arXiv 2605.28803): https://arxiv.org/html/2605.28803 — 게재 상태: preprint
- HB-VLA (arXiv 2602.13710): https://arxiv.org/html/2602.13710 — 게재 상태: preprint (ICAART 2026 게재 주장 미확인, 조사 대상 학회 아님)
- DA-PTQ (arXiv 2604.11572): https://arxiv.org/html/2604.11572v1 , https://arxiv.org/abs/2604.11572 — 게재 상태: preprint
- VLAQuantBench (arXiv 2609.25376): https://arxiv.org/html/2609.25376 — 게재 상태: preprint
- OpenVLA (arXiv 2406.09246): https://arxiv.org/html/2406.09246v3 — 게재 상태: **CoRL 2024**
- SQIL (arXiv 2505.15304): https://arxiv.org/html/2505.15304v1 — 게재 상태: **ICCV 2025**
- Quantization-Aware Imitation-Learning (arXiv 2412.01034): https://arxiv.org/abs/2412.01034 — 게재 상태: preprint
- DyQ-VLA (arXiv 2603.07904): https://arxiv.org/html/2603.07904v1 — 게재 상태: preprint
- QuantVLA (arXiv 2602.20309): https://arxiv.org/abs/2602.20309 — 게재 상태: **CVPR 2026**
- BitVLA (arXiv 2506.07530): https://arxiv.org/html/2506.07530v2 — 게재 상태: preprint
- ActQuant (arXiv 2605.24011): https://arxiv.org/html/2605.24011 — 게재 상태: preprint
- Quantized ACT on Jetson, bimanual SO-101 (arXiv 2608.03938): https://arxiv.org/abs/2608.03938 — 게재 상태: preprint
- vla.simd (arXiv 2609.24274): https://arxiv.org/html/2609.24274 — 게재 상태: preprint
- SmolVLA PyTorch vs ONNX (arXiv 2609.14146): https://arxiv.org/abs/2609.14146 — 게재 상태: preprint
- LiteVLA-Edge (arXiv 2603.03380): https://arxiv.org/html/2603.03380 — 게재 상태: preprint
- QuaRL: https://github.com/harvard-edge/QuaRL — 게재 상태: 미확인 (게재처 검증 안 함)
- Microrobot RL on-device (arXiv 2512.24740): https://arxiv.org/abs/2512.24740 — 게재 상태: preprint
- FAST (arXiv 2501.09747): https://arxiv.org/html/2501.09747v1 — 게재 상태: **RSS 2025**
- VQ-VLA (arXiv 2507.01016): https://arxiv.org/html/2507.01016v1 — 게재 상태: **ICCV 2025**
- Is Bang-Bang Control All You Need? (NeurIPS 2021): https://proceedings.neurips.cc/paper/2021/hash/e46be61f0050f9cc3a98d5d2192cb0eb-Abstract.html — 게재 상태: **NeurIPS 2021** (proceedings)
- ACT (arXiv 2304.13705): https://arxiv.org/html/2304.13705 — 게재 상태: **RSS 2023**
- Real-Time Chunking (arXiv 2506.07339): https://arxiv.org/html/2506.07339v1 — 게재 상태: **NeurIPS 2025**
- SmolVLA blog: https://github.com/huggingface/blog/blob/main/smolvla.md — 게재 상태: 블로그 (비심사)
- GROOVE (arXiv 2609.13695): https://arxiv.org/abs/2609.13695 — 게재 상태: preprint
- On the Analysis of Movement Smoothness (SPARC, 2015): https://pmc.ncbi.nlm.nih.gov/articles/PMC4674971/ — 게재 상태: **J. NeuroEng. Rehabil. 2015** (심사 저널)
- RINSE / Smoothness-Driven Metrics (arXiv 2604.23000): https://arxiv.org/html/2604.23000v1 — 게재 상태: preprint
