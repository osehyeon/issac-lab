# Isaac Sim + Isaac Lab 설치 가이드 (RTX 5090, Ubuntu 24.04, driver 595)

- 작성일: 2026-09-25 (자료 조사 기준일도 같음. 설치는 하지 않았고 문서와 소스만 읽음)
- 대상 머신: Ubuntu 24.04.4 / kernel 7.0.0-30 / glibc 2.39 / RTX 5090 32 GB (sm_120) / driver 595.84 / Python 3.12.3 / `uv` 있음 / sudo 없이 설치
- 접속 환경: macOS 노트북에서 Tailscale로 접속 (RTT 약 66 ms). 서버 주소는 `<SERVER_IP>`로 표기
- 읽은 자료: Isaac Lab `release/3.0.0` 브랜치 (commit `44e290c`, 2026-09-25)와 `v3.0.0-EA` 태그, Isaac Sim 6.1.0 문서. 출처 번호 [n]은 맨 아래 Sources에 있음.

> 이 문서에서 **"(공식)"** 표시가 있는 명령은 공식 문서에 있는 그대로 옮긴 것이다. **"(조합, 미검증)"** 표시는 공식 문서의 패턴을 이 머신에 맞춰 조합한 것으로, 아직 실행해 보지 않았다.

---

## 0. 요약

| 항목 | 결론 |
|---|---|
| 현재 Isaac Lab | **3.0.0 Early Access** (`v3.0.0-EA`, 2026-09-16 공개). GA는 2026년 10월 말 목표 [1] |
| 짝이 되는 Isaac Sim | **6.1.0** (`isaacsim[all,extscache]==6.1.0.0`, 2026-09-10 공개) [1][6][18] |
| Python | **3.12 전용** (`requires-python = ">=3.12,<3.13"`) [6] |
| 권장 설치 방법 | **`uv run` 자동 설정** (공식 권장). Isaac Sim은 `--extra isaacsim`으로 pip 휠 설치 [3] |
| 옛 preset 이름 | `physics=physx/newton_mjwarp/newton_kamino/ovphysx`는 3.0 이름 그대로다. `renderer=isaacsim_rtx_renderer/ovrtx_renderer`는 3.0 beta2 시절 이름이고, EA에서는 `isaacsim_rtx`/`ovrtx`로 바뀌었다. 옛 이름은 legacy alias로 아직 받아 준다 [5][7][8] |
| RTX 5090 | 지원됨. Isaac Sim 6.1 요구사항 표의 "Ideal" GPU가 Blackwell이다. Isaac Lab은 CUDA 13.0(cu130) PyTorch를 쓰는데, 이 빌드는 Blackwell을 지원한다 [3][11] |
| Ubuntu 24.04 | Isaac Sim 6.1은 22.04와 24.04를 모두 공식 지원한다 [11] |
| 드라이버 595.84 | 최소 요구(595.58.03)는 넘는다. 다만 NVIDIA가 R595 브랜치에서 테스트한 버전은 **595.58.03**이다. Isaac Sim 5.1(Isaac Lab 2.3.2의 짝)은 595 드라이버와 호환되지 않는다 [11][12][28][36]. 아래 7절 참고 |

**주의할 점 (이 머신 기준)**
1. **2.x의 task 이름이 3.0에서 바뀌었다.** `-v0`가 빠졌고, Lift-Cube는 contrib로 옮겨졌다 [9].
   - `Isaac-Cartpole-v0` → `Isaac-Cartpole`
   - `Isaac-Reach-Franka-v0` → `Isaac-Reach-Franka`
   - `Isaac-Lift-Cube-Franka-v0` → **`IsaacContrib-Lift-Cube-Franka`**. 3.0의 `Isaac-Lift-Franka`는 이름만 비슷하고 예전 Dexsuite 계열의 다른 task다.
2. **3.0에서 `--headless` CLI 플래그가 없어졌다** [1][8]. 시각화 도구를 켜지 않으면(`--viz` 생략 또는 `--viz none`) 그 자체로 headless 실행이다. 마이그레이션 문서와 visualization 문서 일부에는 `--headless`/`--enable_cameras`가 아직 남아 있지만, EA 소스의 AppLauncher 인자 목록에는 둘 다 없다 [20]. 7절 참고.
3. **3.0에서 `env_cfg.viewer`(ViewerCfg)는 deprecated다.** 카메라 시점은 `env.sim.default_visualizer_cfg` 또는 `KitVisualizerCfg(eye=..., lookat=...)`로 설정한다 [23].
4. **sudo 없이 설치하려면 `uv run` 방식이어야 한다.** 바이너리 zip 방식과 `isaaclab.sh -i` 방식은 문서상 `sudo apt install cmake build-essential`이 필요하다. Docker 방식은 NVIDIA Container Toolkit 설치가 필요하다. `uv run` 방식은 문서상 sudo가 필요 없다 [3].
5. **SSH X11 포워딩(`ssh -Y`)으로는 Kit(RTX) 창을 보기 어렵다.** 원격 GUI는 WebRTC livestream(Mac용 클라이언트 있음)이나 브라우저 기반 Viser로 보는 것이 공식 경로다 [16][19][21]. 5절 참고.

---

## 1. 버전 매트릭스

| Isaac Lab | 공개일 | Isaac Sim | Python | PyTorch | OS | 비고 |
|---|---|---|---|---|---|---|
| **3.0.0-EA** (`release/3.0.0` 브랜치) | 2026-09-16 | **6.1** | 3.12 | 2.11 (EA 태그) / 2.12.0+cu130 (브랜치 최신) | Ubuntu 22.04+ , Windows 11 | 현재 최신. `uv run` 권장, `isaaclab.sh`는 deprecated [1][3][6] |
| 3.0.0-beta2(.patch1) | 2026-06-17 / 07-02 | 6.0 / 6.0.1 | 3.12 | | | preset 선택자 도입. `isaacsim_rtx_renderer` 같은 옛 이름을 쓰던 때 [10] |
| 3.0.0-beta | 2026-03-17 | 6.0 | 3.12 | | | |
| 2.3.2 | 2026-02-02 | 5.1 | 3.11 | | | 2.x 마지막. `-v0` task 이름과 `--headless`를 쓴다 |

출처: GitHub releases API로 확인한 날짜 [1][10], README 호환표 [2].

**참고: EA 태그와 브랜치 최신의 차이.** `v3.0.0-EA` 태그의 `pyproject.toml`은 torch 2.11.0을 cu128 인덱스에서 받는다 (Linux x86_64 기준). `release/3.0.0` 브랜치 최신(2026-09-25)은 torch 2.12.0을 **cu130** 인덱스에서 받고, Newton도 1.6.0으로 올렸다 [6]. 공개 문서 사이트는 브랜치 최신을 따르고, 명시하는 PyTorch도 cu130이다 [3]. 두 빌드 모두 sm_120을 지원한다. cu128 이상이면 Blackwell을 지원하고, 문서에도 "CUDA 13.0 wheels support Blackwell GPUs"라고 적혀 있다 [3].

**드라이버 요구사항**
- Isaac Sim 6.1.0: Linux 최소 **595.58.03**. 표의 Minimum/Good/Ideal 열이 모두 같은 값이다 [11].
- Isaac Lab 3.0: CUDA 13.0 PyTorch 빌드는 Linux 드라이버 **580.65.06 이상**이 필요하다. "Use the latest NVIDIA production branch driver"라고 권장한다 [3].
- Omniverse technical requirements (2026-09-21 갱신): Blackwell GeForce용 R595 Production Branch 드라이버로 **595.58.03**이 올라 있다 [12].
- 대상 머신의 595.84는 R595 브랜치이고 위 최소값보다 높다. 요구사항은 충족한다. 다만 "테스트된 버전"과 정확히 일치하지는 않는다.

**옛 preset 이름 대응표** (EA의 `preset_target.py` legacy alias 기준 [7], 이름 변경 changelog [8])

| 옛 표기 | 3.0 EA 정식 이름 | 설명 [4][5] | 필요한 uv extra |
|---|---|---|---|
| `physics=physx` | `physx` (자동 선택) | Kit가 필요하면 Isaac Sim PhysX, 아니면 OvPhysX | 상황에 따름 |
| (없음) | `physics=isaacsim_physx` | Isaac Sim PhysX. Kit 기반 기본값 | `isaacsim` |
| `physics=newton_mjwarp` | 같음 (`newton`은 옛 alias) | Newton + MuJoCo-Warp | 없음 |
| `physics=newton_kamino` | 같음 (`kamino`는 옛 alias) | Newton + Kamino. **beta**, 일부 task만 지원 | 없음 |
| `physics=ovphysx` | 같음 | OV PhysX (kit-less) | `ovphysx` 또는 `ov` |
| `renderer=isaacsim_rtx_renderer` | `renderer=isaacsim_rtx` | Isaac Sim RTX 렌더러 | `isaacsim` |
| `renderer=newton_renderer` | 같음 | Newton Warp 렌더러 | 없음 |
| `renderer=ovrtx_renderer` | `renderer=ovrtx` | OV RTX (kit-less) | `ovrtx` 또는 `ov` |

`*_renderer` 접미사가 붙은 이름은 beta2(Isaac Sim 6.0) 무렵의 표기이고, 현재 EA/Isaac Sim 6.1에서도 alias로 동작한다 [7][8]. 지원하는 preset은 task마다 다르므로 `--help`나 `list_envs.py --show_presets`로 확인한다 [5].

---

## 2. 시스템 요구사항과 대상 머신 비교

기준: Isaac Sim 6.1.0 requirements [11], Isaac Lab 3.0 installation [3]

| 항목 | 요구 (Min / Good / Ideal) | 대상 머신 | 판정 |
|---|---|---|---|
| OS | Ubuntu 22.04/24.04, Windows 11 | Ubuntu 24.04.4 LTS | OK |
| Kernel | 문서에 명시 없음 | 7.0.0-30-generic | 주의: 검증 사례를 찾지 못했다. 드라이버가 이미 동작하므로 문제 가능성은 낮다 |
| glibc | pip 설치는 GLIBC 2.35 이상 (`manylinux_2_35_x86_64`) [13] | 2.39 | OK |
| CPU 코어 | 4 / 8 / 16 | 24 threads | OK |
| RAM | 32 / 64 / 64 GB | 125 GB | OK |
| 저장공간 | 50 GB SSD / 500 GB / 1 TB NVMe | 3.0 TB free | OK |
| GPU | RTX 4080 / RTX 5080 / RTX PRO 6000 Blackwell | RTX 5090 (Blackwell) | OK |
| VRAM | 16 / 16 / 48 GB | 32 GB | OK |
| 드라이버 (Linux) | ≥ 595.58.03 [11]. Isaac Lab cu130 torch는 ≥ 580.65.06 [3] | 595.84 | 주의: 요구사항은 충족. 테스트 버전은 595.58.03 [12], 7절 참고 |
| RT 코어 | 필수 (A100/H100 미지원) | 있음 | OK |
| NVENC (livestream) | livestream에 필요 (A100 미지원) [16] | GeForce라 있음 | OK |
| Python | 3.12 | 시스템 3.12.3. `uv`는 자체 관리 Python을 받아 쓴다 (`python-preference = "only-managed"`) [6] | OK |
| 인터넷 | 에셋과 확장을 온라인에서 받으므로 필요 [11] | 있음 | OK. 첫 실행은 10분 이상 걸릴 수 있다 [3] |
| sudo | binary/`isaaclab.sh`는 `sudo apt install cmake build-essential`, Docker는 Container Toolkit 설치가 필요 [3] | 쓰지 않음 | 주의: `uv run` 경로를 권장하는 이유 |

---

## 3. 설치 방법 비교

공식 문서의 설치 경로 카드 [3]: (1) Automatic setup with uv (**Recommended for most users**), (2) `isaaclab.sh` installer (legacy), (3) Python environment with Isaac Sim (pip), (4) Isaac Lab Python package (wheel), (5) Downloaded Isaac Sim package, (6) Build from source, (7) Docker/HPC, (8) Cloud.

| 방법 | 장점 | 단점 / 이 머신에서의 문제 |
|---|---|---|
| **(a) `uv run` + `--extra isaacsim`** (Isaac Sim을 pip 휠로 받음) | 공식 권장. 환경을 직접 만들거나 활성화할 필요가 없다. `uv.lock`으로 버전이 고정된다. torch CUDA 빌드도 자동으로 고른다 ("No additional command flags are needed") [3]. `uv`가 이미 있다. 문서상 sudo가 필요 없다 | 첫 `uv run --extra isaacsim`에서 받는 양이 많다 (Isaac Sim 휠 + extscache). EA 단계라 버그가 있을 수 있다 |
| (a') 직접 만든 venv + `uv pip install isaacsim...` + `./isaaclab.sh -i` ("Python environment with Isaac Sim") | 환경 구성을 직접 통제할 수 있다 | 문서상 `sudo apt install cmake build-essential`이 필요하다 [3]. torch와 Isaac Sim 버전을 직접 맞춰야 한다 |
| (b) Isaac Sim standalone zip + `ln -s … _isaac_sim` + `./isaaclab.sh -i` | Isaac Sim GUI 앱(`isaac-sim.sh`)과 VS Code 연동이 편하다. `isaac-sim.streaming.sh`, compatibility checker 스크립트가 들어 있다 [14][15] | 번들 Python만 써야 하고 uv/venv/conda와 섞을 수 없다 [3]. `isaaclab.sh`는 deprecated이고 3.1에서 제거될 예정이다 [1]. sudo apt가 필요하다. 수동 단계가 많다 |
| (c) Docker (`./docker/container.py start`, 또는 `nvcr.io/nvidia/isaac-lab:3.0.0-rc1`) | 환경이 격리된다. 공식 이미지가 있다 [27] | NVIDIA Container Toolkit 설치(sudo)가 필요하다. snap docker는 checkout이 `/home` 아래에 있어야 한다 [3]. snap docker에서 GPU 연동은 추가 확인이 필요하다. WebRTC에 `--network=host`가 필요하다 [16] |

**권장: (a) `uv run --extra isaacsim`**. 이유는 네 가지다.
1. 공식 문서가 대부분의 사용자에게 권장하는 경로이고, 3.0 릴리스 노트도 `uv run`을 기본 워크플로로 삼는다 [1][3].
2. sudo 없이 설치할 수 있다. uv가 Python 3.12를 스스로 받아 쓰므로 시스템 Python과 부딪히지 않는다.
3. Blackwell에 맞는 torch CUDA 빌드(cu130)를 lock 파일이 자동으로 고른다 [3][6].
4. Lift-Cube(contrib) task는 PhysX(`PhysxCfg`)만 설정되어 있다. 그래서 Kit 기반 Isaac Sim PhysX가 필요하고, `--extra isaacsim`이 이것을 제공한다 [34].

---

## 4. 권장 경로 단계별 명령

### 4.1 사전 확인 (서버에서, 설치 없음)

```bash
nvidia-smi                      # 드라이버 595.84, RTX 5090 확인
ldd --version                   # glibc >= 2.35 [13]
~/.local/bin/uv --version       # 버전 확인. 너무 오래됐으면 `uv self update` (uv 자체 명령)
which cmake gcc                 # mimic extra 등에만 필요. 없어도 기본 경로에는 문제없다 [3]
```

### 4.2 uv 설치와 clone (공식) [3][4]

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh        # uv가 이미 있으면 생략
git clone https://github.com/isaac-sim/IsaacLab.git --branch release/3.0.0
cd IsaacLab
```

> 재현성이 중요하면 `--branch v3.0.0-EA`로 태그에 고정한다 (조합, 미검증). 태그에서는 torch 2.11+cu128이, 브랜치 최신에서는 torch 2.12+cu130이 설치된다 [6].

### 4.3 EULA 동의 (공식)

첫 실행에서 NVIDIA Omniverse EULA 동의를 묻는다. SSH 같은 비대화형 환경에서는 환경변수로 미리 동의한다 [3][13].

```bash
export OMNI_KIT_ACCEPT_EULA=YES      # Isaac Lab 문서 표기는 yes, Isaac Sim 문서 표기는 YES
```

### 4.4 첫 실행: kit-less (Newton) 스모크 테스트 (공식) [3][4]

Isaac Sim 없이 동작하는지 먼저 확인한다. 첫 `uv run`에서 핵심 의존성이 자동으로 설치된다.

```bash
uv run isaaclab train --rl_library rsl_rl --task Isaac-Cartpole-Direct physics=newton_mjwarp
uv run python scripts/environments/list_envs.py                 # 등록된 task 목록 [4]
uv run python scripts/environments/list_envs.py --show_presets  # task별 preset 목록 [5]
uv run isaaclab train --help
```

### 4.5 Isaac Sim 포함 (full Kit / PhysX / RTX) (공식) [1][3]

```bash
uv run --extra isaacsim isaaclab train --rl_library rsl_rl \
   --task Isaac-Cartpole-Direct physics=isaacsim_physx
```

- `--extra isaacsim`은 `isaacsim[all,extscache]==6.1.0.0`을 `pypi.nvidia.com`에서 받는다 [3][6].
- 첫 실행은 확장을 받느라 10분 이상 걸릴 수 있다 [3].
- Isaac Sim 자체 검증 명령은 문서상 `isaacsim`이다 [3][13]. uv 환경에서는 `uv run --extra isaacsim isaacsim`으로 실행할 수 있다 (조합, 미검증). GUI가 필요하므로 5절 방식과 함께 쓴다.
- compatibility checker (pip 설치판, 공식): `isaacsim isaacsim.exp.compatibility_check` [15]. uv에서는 `uv run --extra isaacsim isaacsim isaacsim.exp.compatibility_check` (조합, 미검증). 휠에 따라 `compatibility-check` bundle이 따로 필요할 수 있다 [13].

**참고: 수동 pip 설치 명령** (직접 venv를 관리하는 경로 (a'), 공식 문서 그대로) [3]

```bash
uv venv --python 3.12 --seed env_isaaclab
source env_isaaclab/bin/activate
uv pip install "isaacsim[all,extscache]==6.1.0.0" --extra-index-url https://pypi.nvidia.com --index-strategy unsafe-best-match --prerelease=allow
uv pip install -U torch==2.12.0 torchvision==0.27.0 --index-url https://download.pytorch.org/whl/cu130
sudo apt install cmake build-essential     # sudo가 없어서 이 머신에서는 막힐 수 있다
./isaaclab.sh -i
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py --viz kit
```

### 4.6 검증 절차

| 목적 | 명령 | 근거 |
|---|---|---|
| 빈 장면 (create_empty 튜토리얼) | `uv run --extra isaacsim python scripts/tutorials/00_sim/create_empty.py --viz kit` | 공식 형태는 `./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py --viz kit`. 검은 viewport가 뜨면 성공이다 [3]. uv 형태는 조합(미검증)이고 `uv run --extra isaacsim python scripts/...` 패턴을 따른다 [19] |
| 같은 장면을 livestream으로 | `LIVESTREAM=2 uv run --extra isaacsim python scripts/tutorials/00_sim/create_empty.py` | 조합, 미검증. LIVESTREAM 예시는 [19] |
| task 목록 | `uv run python scripts/environments/list_envs.py` | 공식 [4] |
| Cartpole 동작 확인 | `uv run isaaclab zero_agent --task Isaac-Cartpole --viz newton` / `random_agent` | 공식 [4] |
| Cartpole 학습/재생 | `uv run isaaclab train --task Isaac-Cartpole` → `uv run isaaclab play --task Isaac-Cartpole --checkpoint latest --viz newton` | 공식 [4] |
| Cartpole (Isaac Sim PhysX + Kit) | `uv run --extra isaacsim isaaclab train --rl_library rsl_rl --task Isaac-Cartpole physics=isaacsim_physx --viz kit` | 공식 [1] |
| Reach | `uv run isaaclab train --rl_library rsl_rl --task Isaac-Reach-Franka physics=newton_mjwarp` | 공식 형태 (known issues 예시) [26] |
| **Lift-Cube** (2.x의 `Isaac-Lift-Cube-Franka-v0`) | `uv run --extra isaacsim isaaclab zero_agent --task IsaacContrib-Lift-Cube-Franka --viz kit` → `uv run --extra isaacsim isaaclab train --rl_library rsl_rl --task IsaacContrib-Lift-Cube-Franka` → `... play ... --checkpoint latest --viz kit` | 조합, 미검증. task ID [9][34], 명령 형태 [4] |
| 학습 환경 수 줄이기 | `--num_envs 16` 같이 추가 | 공식 [4] |
| 영상 녹화 | `uv run --extra isaacsim,video isaaclab train --rl_library rsl_rl --task Isaac-Cartpole --viz kit --video` | 문서 예시는 `uv run isaaclab train ... --viz kit --video` [22]. `moviepy`가 필요해서 `video` extra를 붙였다 (조합, 미검증) [35]. 5.3절 참고 |

---

## 5. 원격 실행: headless, GUI 보기, 스크린샷과 영상

### 5.1 headless (3.0 방식)

- 3.0에서는 `--viz`를 생략하면 시각화 도구 없이 headless로 돈다 ("Without a visualizer, commands run headless by default") [23]. 명시적으로 끄려면 `--viz none`을 쓴다 [1].
- `--headless` 플래그는 3.0에서 제거됐다 [1][8]. 환경변수 `HEADLESS=1`은 AppLauncher가 여전히 읽는다 [19].
- 카메라와 offscreen 렌더링은 자동으로 켜진다. "No environment variable or command-line option is required for camera tasks" [19].

### 5.2 GUI 보기: Mac + Tailscale 환경의 선택지

**(1) SSH X11 포워딩 (`ssh -Y <server>`) — Kit에는 권장하지 않는다**
- NVIDIA 문서와 포럼에서 "X11 forwarding 지원"을 명시한 곳은 찾지 못했다. 원격 호스트에서는 headless 실행 후 streaming client로 붙으라는 안내만 있다 [16][32]. Isaac Lab 공식 Docker 이미지도 "headless only and does not allow for X11 forwarding"이라고 적고 있다 [27].
- 기술적 추론 (미검증): Kit viewport는 Vulkan swapchain으로 화면을 그린다. SSH로 넘어온 원격 X 서버(Mac의 XQuartz)에서는 NVIDIA GPU가 직접 present할 수 없다. 따라서 `vkCreateSwapchainKHR` 실패나 극단적 저속이 예상된다. Newton GL(pyglet/OpenGL)도 XQuartz의 indirect GLX(구버전 OpenGL)에 걸릴 가능성이 높다.
- 결론: xclock 수준은 되지만, Isaac Sim/Isaac Lab GUI 확인 용도로는 기대하지 않는 편이 좋다.

**(2) Isaac Sim WebRTC livestream + Mac용 Streaming Client — 1순위 (Kit/RTX 화면을 그대로 볼 수 있음)**
- 클라이언트: **Isaac Sim WebRTC Streaming Client 2.0.0** (2026-06). **macOS aarch64와 x86_64 빌드가 있다** [14]. 다운로드는 Isaac Sim 6.1.0 download 페이지의 Latest Release 섹션에 있다 [14][16].
- 필요한 포트: **TCP 49100** (signaling), **UDP 47998** (media) [16]. 미디어가 SRTP over UDP라서 **SSH 포트포워딩(TCP만 지원)으로는 동작하지 않는다**. 실제 실패 사례 [30]와 NVIDIA 직원의 확인 [31]이 있다. Tailscale은 IP 레벨 VPN이라 UDP도 통과한다. 그래서 원리상 Tailscale IP로 바로 붙는 방식이 맞다 (미검증).
- Isaac Lab에서 켜는 법 (공식) [19][20]:
  - `LIVESTREAM=1`: public network 모드. `PUBLIC_IP` 환경변수 값이 `--/exts/omni.kit.livestream.app/primaryStream/publicIp`로 들어간다 (기본값 `127.0.0.1`).
  - `LIVESTREAM=2`: private/local network 모드. publicIp를 지정하지 않는다.
  - CLI로는 `--livestream {0,1,2}`를 쓴다 (AppLauncher 인자) [20]. livestream을 켜면 headless가 강제된다.
  - 인스턴스 하나에 클라이언트 하나만 붙을 수 있다 [16][19].
- 권장 시도 순서 (조합, 미검증):
  ```bash
  # 서버에서
  export OMNI_KIT_ACCEPT_EULA=YES
  LIVESTREAM=1 PUBLIC_IP=<SERVER_IP> uv run --extra isaacsim isaaclab zero_agent \
      --task IsaacContrib-Lift-Cube-Franka --num_envs 4 --viz kit
  # 안 되면 LIVESTREAM=2 로 바꿔서 다시 시도
  ```
  Mac에서 Streaming Client를 열고 서버 주소에 `<SERVER_IP>`를 입력한다. 문서 원문은 "replace 127.0.0.1 with the IP address of the machine running Isaac Sim"이고, public IP 모드에서는 "Use the same Public IP in the ... app"이다 [16].
- 문제가 생기면 확인할 것:
  - 포트 49100이 이미 잡혀 있으면 `NVST_R_BUSY`가 난다. `ss -tlnp | grep 49100`으로 확인하고 해당 프로세스를 종료한다 [25].
  - 서버 방화벽(ufw)이 tailscale0의 UDP 47998을 막고 있지 않은지 확인한다. sudo가 없으면 관리자에게 확인해야 한다.
  - 공식 안내는 "same network" 사용을 권장한다 [16]. Tailscale이 이 조건을 만족하는지는 직접 확인해야 한다.
- Isaac Sim 단독 앱을 streaming으로 띄우는 공식 명령 (pip 설치판): `isaacsim isaacsim.exp.full.streaming --no-window` [13][16].
- 알려진 이슈: livestream 중에 에러 로그가 여러 개 떠도 연결이 인터랙티브하면 무시해도 된다 [17].

**(3) 브라우저 기반 Viser 시각화 — 2순위 (TCP만 쓰고 Mac 브라우저로 바로 볼 수 있음)**
- `--viz viser`는 창을 띄우지 않고 웹 UI를 띄운다. 기본 포트는 **8080**이고, 터미널에 URL이 출력된다 [25]. "useful for remote connections"라고 소개되어 있다 [4].
- 예시: `uv run --extra viser isaaclab random_agent --task Isaac-Cartpole physics=newton_mjwarp --viz viser` (조합, 미검증). Mac에서 `http://<SERVER_IP>:8080`으로 접속한다.
- 한계: RTX 화질이 아니다. 또 `--video` 녹화 소스로 쓸 수 없다 ("streaming visualizers do not expose a local frame-capture API") [35]. Isaac Sim extra와 viser extra를 한 환경에 같이 설치할 수 있는지는 문서가 서로 다르게 말한다 [3][8]. 확인이 필요하다.
- Rerun(`--extra rerun`, `--viz rerun`)도 웹 뷰와 녹화 타임라인을 제공한다 [21].

**(4) 서버의 :1 디스플레이에 GUI 띄우기 + 원격 데스크톱 — 3순위**
- 서버에 로그인된 GDM Xorg 세션(예: :1)이 있으면 쓸 수 있다. ssh에서 `DISPLAY=:1`로 Kit 창을 여기에 띄우면 NVIDIA GPU가 직접 그린다 (조합, 미검증. `XAUTHORITY` 지정이 필요할 수 있다).
- 이 화면을 보려면 :1을 원격으로 공유해야 한다. chrome-remote-desktop은 별도 가상 세션을 만들어서 이 화면을 보여주지 않는다. x11vnc가 없으면 설치에 sudo가 필요하다.
- gnome-remote-desktop(`grdctl`)은 사용자 모드에서 `grdctl vnc enable`, `grdctl vnc set-password`, `grdctl rdp enable`, `grdctl rdp set-credentials` 같은 명령을 제공한다 [33]. 다만 Ubuntu 24.04(GNOME 46)의 **Xorg 세션**에서 동작하는지, **잠긴 화면**에서 공유가 되는지는 확인하지 못했다 (미검증).
- NVIDIA 포럼에는 Xvfb + x11vnc + noVNC로 GUI를 보는 우회 사례가 있다 [31]. 이 방식에는 패키지 설치(sudo)가 필요하다.

**Mac + Tailscale에서의 권장 순서**: ① WebRTC Streaming Client (macOS aarch64) + `LIVESTREAM=1 PUBLIC_IP=<SERVER_IP>` → ② 탐색용으로 `--viz viser` (브라우저) → ③ 이미지는 headless `--video`로 확보 (5.3). X11 포워딩은 Kit용으로 쓰지 않는다.

### 5.3 headless로 스크린샷과 영상 확보

- **`--video`** (train/play 공통) [22][35]
  - `--viz`를 생략하면 headless Kit 시각화 도구를 자동으로 만들어서 녹화한다. Kit가 없으면 Newton GL로 대체한다 [23][35].
  - `--viz none`과 `--video`는 함께 쓸 수 없다 (에러) [35].
  - 저장 위치는 `<log_dir>/videos/train` 또는 `.../videos/play`. 기본값은 `video_length=200` step, 2000 step 간격이다 [22][35].
  - `--video_length`와 `--video_interval`로 조절한다 [35].
  - 녹화에는 `moviepy`가 필요하다. `video` extra에 들어 있다 [6][35].
  - 예시 (조합, 미검증):
    ```bash
    uv run --extra isaacsim,video isaaclab play --rl_library rsl_rl \
        --task IsaacContrib-Lift-Cube-Franka --checkpoint latest --num_envs 4 \
        --viz kit --video --video_length 300
    ```
- **Newton GL은 headless에서 EGL을 쓴다**: `$DISPLAY`가 없으면 자동으로 EGL을 선택한다 [23]. kit-less task는 `--viz newton_gl --video`로 녹화할 수 있다 (조합, 미검증).
- **Kit headless 녹화**에는 카메라 렌더링이 필요하다. `--video`를 쓰면 자동으로 설정된다 [23].
- **스크린샷**: 전용 CLI 플래그는 찾지 못했다. 다음 방법이 현실적이다.
  1. livestream 클라이언트 화면을 Mac에서 캡처한다 (Cmd+Shift+4).
  2. `--video`로 만든 mp4에서 프레임을 뽑는다. `ffmpeg -i clip.mp4 -vf "select=eq(n\,100)" -vframes 1 shot.png` 같은 일반 ffmpeg 명령을 쓴다 (서버에 ffmpeg가 없으면 pip 패키지 `imageio-ffmpeg`의 바이너리를 쓴다. 조합, 미검증).
  3. `VideoRecorderCfg(source="sensor:<camera>")`로 장면 카메라 센서를 녹화한다. 센서에 rgb가 있어야 한다 [22].

---

## 6. 환경 설정 파일 위치와 수정 방법

경로는 `release/3.0.0` / `v3.0.0-EA` 기준이다 [34].

| Task (3.0 ID) | 설정 파일 |
|---|---|
| `Isaac-Cartpole` (manager-based) | `source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_manager_env_cfg.py` |
| `Isaac-Cartpole-Direct` | `.../core/cartpole/cartpole_direct_env_cfg.py` |
| `Isaac-Reach-Franka` | 공통: `.../core/reach/reach_env_cfg.py`, Franka: `.../core/reach/config/franka/franka_reach_env_cfg.py` |
| `IsaacContrib-Lift-Cube-Franka` (구 `Isaac-Lift-Cube-Franka-v0`) | 공통: `.../contrib/lift/lift_env_cfg.py`, Franka + 큐브: `.../contrib/lift/config/franka/joint_pos_env_cfg.py` |
| Franka 로봇 기본 자세 | `source/isaaclab_assets/isaaclab_assets/robots/franka.py` (`FRANKA_PANDA_CFG.init_state.joint_pos`) |
| SimulationCfg (dt, gravity 등) | `source/isaaclab/isaaclab/sim/simulation_cfg.py` |

**주요 필드** (소스에서 확인) [34]

| 바꿀 대상 | 필드 | 기본값 예시 |
|---|---|---|
| 물체 위치 | `scene.object.init_state.pos`, `rot` (**3.0은 쿼터니언을 XYZW 순서로 씀**) [1] | Lift-Cube: `pos=[0.5, 0, 0.055]`, `rot=[0,0,0,1]` |
| 물체 리셋 랜덤 범위 | `events.reset_object_position.params.pose_range` | `{"x": (-0.1, 0.1), "y": (-0.25, 0.25), "z": (0.0, 0.0)}`. 리셋할 때마다 init_state 기준으로 이 범위 안에서 흔든다 |
| 로봇 초기 자세 | `scene.robot.init_state.joint_pos` (Franka `panda_joint1..7`), `init_state.pos` | `panda_joint2=-0.569`, `panda_joint4=-2.810` 등 |
| Cartpole 리셋 범위 | `events.reset_cart_position.params.position_range` | Hydra 문서 예시 [24] |
| 카메라 시점 | 3.0: `sim.default_visualizer_cfg = VisualizerCfg(eye=..., lookat=...)` 또는 `sim.visualizer_cfgs=[KitVisualizerCfg(eye=..., lookat=...)]` [21][23]. 옛 `viewer.eye`/`viewer.lookat`은 한 릴리스 동안 shim으로 동작하는 deprecated 필드다 [23] | Cartpole `eye=(8.0, 0.0, 5.0)`, Reach `eye=(3.5, 3.5, 3.5)`. Lift-Cube contrib는 따로 지정하지 않는다 |
| 시뮬레이션 dt | `sim.dt` | Lift 0.01, Reach 1/120, Cartpole 1/120 |
| decimation | `decimation` (+ `sim.render_interval`) | Lift 2, Reach 4, Cartpole 2 |
| 환경 수 / 간격 | `scene.num_envs`, `scene.env_spacing` | Lift 4096 / 2.5, Cartpole 4096 / 4.0 |
| 중력 | `sim.gravity` | `(0.0, 0.0, -9.81)` |
| 에피소드 길이 | `episode_length_s` | Lift 5.0, Reach 12.0, Cartpole 5 |
| 물리 백엔드 | `physics=` 선택자. Cartpole과 Reach의 기본값은 **`newton_mjwarp`**이고, Lift-Cube contrib는 `PhysxCfg`(Isaac Sim PhysX)만 있다 | |

**CLI로 덮어쓰기 (Hydra)** [5][24]
- `env.<경로>=값` 형식으로 환경 설정을 바꾸고, `agent.<경로>=값`으로 에이전트 설정을 바꾼다. 선택자(`physics=` 등)처럼 앞에 대시를 붙이지 않는다.
- 적용 순서: preset default → `presets=` → 경로 지정 preset → 스칼라 Hydra override [5].
- 공식 예시:
  - `uv run isaaclab train --rl_library rsl_rl --task=Isaac-Cartpole env.actions.joint_effort.scale=10.0 agent.seed=2024` [24]
  - `uv run isaaclab train --rl_library rsl_rl --task Isaac-Cartpole-Direct physics=newton_mjwarp env.sim.dt=0.002` [5]
  - 리스트 값은 따옴표로 감싼다: `env.events.reset_cart_position.params.position_range="[-2.0, 2.0]"`. Hydra는 tuple을 지원하지 않아서 list로 쓴다 [24].
- `--num_envs`, `--seed`, `--max_iterations`는 Hydra 값보다 우선한다 [24].
- 예시 (조합, 미검증):
  ```bash
  uv run --extra isaacsim isaaclab zero_agent --task IsaacContrib-Lift-Cube-Franka --viz kit --num_envs 4 \
     env.scene.object.init_state.pos="[0.6, 0.1, 0.055]" \
     env.events.reset_object_position.params.pose_range.x="[0.0, 0.0]" \
     env.scene.robot.init_state.joint_pos.panda_joint1=0.5 \
     env.sim.gravity="[0.0, 0.0, -1.62]" \
     env.sim.dt=0.005 env.decimation=4 env.sim.render_interval=4
  # 카메라 시점 (default_visualizer_cfg가 설정된 task에서만 가능할 것으로 봄)
  uv run isaaclab zero_agent --task Isaac-Cartpole --viz newton env.sim.default_visualizer_cfg.eye="[4.0, 4.0, 3.0]"
  ```
- **주의** [24]
  - `__post_init__` 안에서 다른 값으로부터 계산한 값은 override해도 다시 계산되지 않는다. 예를 들어 `render_interval = decimation`이므로 decimation을 바꾸면 `render_interval`도 함께 넘겨야 한다.
  - 코드를 직접 고치고 싶으면 위 설정 파일을 수정한다. 소스 checkout이 editable로 설치되어 있어서 바로 반영된다 [6].

---

## 7. 알려진 문제와 트러블슈팅 (이 머신 관련)

1. **드라이버 595.84**
   - 2026-07에 보고된 이슈: RTX 5090 + **595.84**에서 **Isaac Sim 5.1** 앱이 `librtx.scenedb.plugin.so`에서 segfault했다. `--no-window`도 같았고, 렌더링 없는 Isaac Lab 학습만 정상이었다 [28].
   - NVIDIA는 "595 드라이버는 Isaac Sim 5.1과 호환되지 않는다"며 드라이버 580으로 내리거나 Isaac Sim 6.0 / Isaac Lab 3.0으로 올리라고 답했다 [36]. 5.1 요구사항 문서도 580.65.06 기준이다 [37]. 그래서 드라이버를 바꿀 수 없으면 안정판 2.3.2 + 5.1 대신 3.0 + 6.1을 쓴다.
   - 6.1은 R595(최소 595.58.03)를 기준으로 하므로 같은 문제는 없을 것으로 보지만 595.84에서 직접 확인하지는 않았다.
   - Kit GUI나 streaming에서 비슷한 crash가 나면 드라이버를 **595.58.03**(테스트된 R595 Production Branch)으로 맞추는 것을 고려한다 [12]. sudo가 필요하니 관리자에게 요청해야 한다.
2. **Blackwell 관련 과거 이슈**
   - Isaac Sim 5.1에서 TiledCamera가 멈춘 사례가 있다. RTX 5090 Laptop, driver 590에서 발생했고 NVIDIA 답변은 5.1은 580 드라이버를 쓰라는 것이었다 [29].
   - Isaac Sim 6.1 known issue에는 Blackwell에서 Franka Open Drawer 예제가 기본 설정으로 실패하고 `physics_rate`를 600으로 올리면 해결된다는 항목이 있다 [17].
3. **task 이름 변경**: `-v0` 이름을 쓰면 등록되지 않은 task라는 에러가 난다. 1번 요약표와 [9]를 참고한다.
4. **`--headless` / `--enable_cameras`**: 3.0 EA의 AppLauncher 인자 목록에는 없다 [20]. changelog에도 "the `--headless` CLI flag removed in 3.0"이라고 되어 있다 [8]. 일부 문서 예시(visualization, migration)에는 아직 남아 있으니 에러가 나면 빼고 실행한다.
5. **livestream**
   - UDP가 필요하다. SSH 터널로는 안 된다 [30][31].
   - 포트 49100 점유 시 `NVST_R_BUSY`가 난다 [25].
   - 클라이언트는 한 번에 하나만 붙을 수 있다 [16].
   - 웹 뷰어를 쓸 경우 Firefox보다 Chrome을 권장한다 [17].
6. **첫 실행 지연**: 확장과 셰이더 캐시 때문에 10분 이상 걸릴 수 있다 [3][15]. 에셋 다운로드가 느리면 Hub Workstation Cache를 켠다 (`./isaaclab.sh -s`로 Isaac Sim을 띄운 뒤 CACHE 메뉴에서 설정) [3].
7. **의존성 경고**: 설치가 끝났다면 `requires ..., but ...` 류의 경고는 대체로 무시해도 된다. `No solution found`가 나면 환경을 새로 만든다 [25].
8. **`ModuleNotFoundError: No module named 'isaacsim'`**: `--extra isaacsim` 없이 Kit가 필요한 task나 `--viz kit`를 실행했을 때 난다 [25].
9. **Ctrl+C 종료 시** `[omni.physx.plugin] Subscription cannot be changed during the event call`가 나올 수 있다. 무시해도 된다 [26].
10. **카메라 첫 프레임이 빈 화면**: RTX 계열 렌더러의 알려진 문제다. 몇 번 `sim.render()`한 뒤 쓴다 [26].
11. **2.x 환경을 업그레이드해서 쓰지 말 것**: 반드시 새 Python 3.12 환경에서 시작한다 [1]. 이 머신은 새로 설치하므로 해당 없다.
12. **Docker(snap)**: checkout을 `/home` 아래에 두어야 한다. NVIDIA Container Toolkit이 필요하다 [3].

---

## 8. 아직 모르는 것 / 확인 필요

- [ ] 드라이버 **595.84 + Isaac Sim 6.1.0 + RTX 5090** 조합에서 Kit GUI와 livestream이 crash 없이 뜨는지. 공식 테스트 버전은 595.58.03이다 [12]
- [ ] kernel **7.0**에서 검증된 사례 (문서에 커널 요구사항 없음)
- [ ] `uv run --extra isaacsim` 첫 설치에 필요한 디스크와 시간 (문서에 수치 없음)
- [ ] Tailscale로 Kit livestream이 실제로 붙는지. `LIVESTREAM=1 PUBLIC_IP=<SERVER_IP>`와 `LIVESTREAM=2` 중 어느 쪽이 되는지. (TCP 49100, UDP 47998이 Tailscale로 양방향 통과하는 것은 2026-09-25에 소켓 테스트로 확인했다)
- [ ] `isaaclab train/play/zero_agent`에서 `--livestream` CLI 인자가 실제로 받아지는지 (소스상 AppLauncher 인자로 등록됨 [20]). 안 되면 `LIVESTREAM` 환경변수를 쓴다
- [ ] `IsaacContrib-Lift-Cube-Franka`가 `zero_agent`/`train`에서 문제없이 도는지와 기본 RL 설정 (rsl_rl cfg 존재 확인 [34])
- [ ] Hydra로 `env.sim.default_visualizer_cfg.eye`나 `env.scene.robot.init_state.joint_pos.<joint>`를 override할 수 있는지 (문서의 일반 규칙에서 추론)
- [ ] `--extra isaacsim`과 `--extra viser`를 한 환경에 함께 설치할 수 있는지. 설치 문서는 "No extras conflict"라고 하지만 과거 changelog는 충돌을 언급한다 [3][8]
- [ ] Ubuntu 24.04 Xorg 세션에서 `grdctl`(사용자 모드) VNC/RDP로 잠긴 :1 화면을 공유할 수 있는지
- [ ] `ssh -Y`에서 Kit/Newton GL 창이 실제로 실패하는지 (공식 명시 없음, 기술적 추론)
- [x] 서버 도구: `gcc`/`g++`/`make`는 있고 `ffmpeg`, `cmake`는 없다 (2026-09-25 확인). 기본 `uv run` 경로에는 필요 없다 [3]
- [ ] 문서의 `uv run isaaclab train ... --viz kit --video` 예시 [22]가 `--extra isaacsim` 없이도 도는지 (quickstart 표는 `--viz kit`에 `isaacsim` extra가 필요하다고 함 [4])

---

## Sources

(모두 2026-09-25에 읽음. Isaac Lab 소스는 `release/3.0.0` commit `44e290c`와 `v3.0.0-EA` 태그 기준)

1. Isaac Lab v3.0.0-EA 릴리스 노트 (2026-09-16) — https://github.com/isaac-sim/IsaacLab/releases/tag/v3.0.0-EA
2. Isaac Lab README (호환표) — https://github.com/isaac-sim/IsaacLab
3. Isaac Lab 3.0 Installation — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/setup/installation/index.html (source: `docs/source/setup/installation/index.rst`, `docs/_extensions/isaaclab_docs.py`)
4. Isaac Lab 3.0 Quickstart — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/setup/quickstart.html
5. Backends and Presets — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/concepts/backends_and_presets.html
6. `pyproject.toml` (버전 pin, extras, torch 인덱스) — https://github.com/isaac-sim/IsaacLab/blob/release/3.0.0/pyproject.toml , https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/pyproject.toml
7. `preset_target.py` (legacy alias: `ovrtx_renderer`→`ovrtx`, `isaacsim_rtx_renderer`→`isaacsim_rtx`, `newton`→`newton_mjwarp`, `kamino`→`newton_kamino`) — https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab_tasks/isaaclab_tasks/utils/preset_target.py
8. `isaaclab` CHANGELOG (renderer preset 접미사 제거, `--headless` 제거) — https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab/docs/CHANGELOG.rst
9. `isaaclab_tasks` CHANGELOG (`-v0` 제거, `IsaacContrib-Lift-Cube-Franka` 이동) — https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab_tasks/docs/CHANGELOG.rst
10. Isaac Lab v3.0.0-beta2 릴리스 (Isaac Sim 6.0) — https://github.com/isaac-sim/IsaacLab/releases/tag/v3.0.0-beta2
11. Isaac Sim 6.1.0 Requirements — https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html
12. Omniverse Technical Requirements (드라이버 표, 2026-09-21 갱신) — https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html
13. Isaac Sim 6.1.0 Python(pip) Installation — https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_python.html
14. Isaac Sim 6.1.0 Download (standalone zip, WebRTC Streaming Client 2.0.0) — https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/download.html
15. Isaac Sim 6.1.0 Workstation Installation / Compatibility Checker — https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_workstation.html
16. Isaac Sim 6.1.0 Livestream Clients — https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/manual_livestream_clients.html
17. Isaac Sim 6.1.0 Known Issues — https://docs.isaacsim.omniverse.nvidia.com/6.1.0/overview/known_issues.html
18. Isaac Sim GitHub Releases (v6.1.0, 2026-09-10) — https://github.com/isaac-sim/IsaacSim/releases
19. Isaac Lab `isaaclab.app` API (HEADLESS, LIVESTREAM, PUBLIC_IP) — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/api/lab/isaaclab.app.html
20. `app_launcher.py` (CLI 인자, livestream 설정값) — https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab/isaaclab/app/app_launcher.py
21. Visualization — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/concepts/visualization.html
22. Recording Video — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/features/record_video.html
23. Migrating to Isaac Lab 3.0 (Visualizers, Cameras, and Recording; ViewerCfg deprecated) — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/migration/migrating_to_isaaclab_3-0.html
24. Hydra Configuration System — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/features/hydra.html
25. Isaac Lab Troubleshooting — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/refs/troubleshooting.html
26. Isaac Lab Known Issues — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/refs/issues.html
27. Isaac Lab Docker and Cloud (`docs/source/features/docker_cloud.rst`, `include/docker_details.inc`) — https://isaac-sim.github.io/IsaacLab/release/3.0.0/source/features/docker_cloud.html
28. GitHub Issue #6785 (RTX 5090 + driver 595.84 + Isaac Sim 5.1 segfault) — https://github.com/isaac-sim/IsaacLab/issues/6785
29. GitHub Issue #4951 (TiledCamera hang, RTX 5090, Isaac Sim 5.1) — https://github.com/isaac-sim/IsaacLab/issues/4951
30. GitHub Issue #5172 (macOS 클라이언트 + SSH 터널 livestream 실패) — https://github.com/isaac-sim/IsaacLab/issues/5172
31. NVIDIA Forum: TCP-only 환경에서 WebRTC 불가 (SRTP over UDP), noVNC 우회 — https://forums.developer.nvidia.com/t/running-isaac-sim-in-a-browser-on-tcp-only-clouds-runpod-webrtc-livestream-cant-work-heres-a-novnc-approach-that-does/376664
32. NVIDIA Forum: Isaac Sim via ssh and Remote Desktop — https://forums.developer.nvidia.com/t/isaac-sim-via-ssh-and-remote-desktop-connection-windows-and-linux-host/284090
33. `grdctl(1)` man page — https://man.archlinux.org/man/grdctl.1.en
34. 환경 설정 소스 (v3.0.0-EA):
    - https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab_tasks/isaaclab_tasks/contrib/lift/lift_env_cfg.py
    - https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab_tasks/isaaclab_tasks/contrib/lift/config/franka/joint_pos_env_cfg.py
    - https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab_tasks/isaaclab_tasks/contrib/lift/config/franka/__init__.py
    - https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab_tasks/isaaclab_tasks/core/reach/reach_env_cfg.py
    - https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_manager_env_cfg.py
    - https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab_assets/isaaclab_assets/robots/franka.py
    - https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab/isaaclab/sim/simulation_cfg.py
35. `isaaclab_rl/entrypoints/common.py` (`--video`, `--video_length`, `--video_interval`, `--num_envs`, 녹화 소스 결정 로직) 및 `envs/utils/video_recorder.py` (moviepy 필요) — https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/source/isaaclab_rl/isaaclab_rl/entrypoints/common.py
36. IsaacSim Issue #706 (Isaac Sim 5.1 + 595 드라이버 비호환, NVIDIA 답변) — https://github.com/isaac-sim/IsaacSim/issues/706
37. Isaac Sim 5.1.0 Requirements (Linux 580.65.06) — https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html
