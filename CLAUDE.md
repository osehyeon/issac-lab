# CLAUDE.md

Isaac Sim + Isaac Lab on a remote RTX 5090 server. Facts below were checked on 2026-09-25, not assumed.
Machine-specific details live in `CLAUDE.local.md`.

## Version choice: Isaac Lab 3.0 EA + Isaac Sim 6.1

- Isaac Sim 5.1 (used by the stable Isaac Lab 2.3.2) is not compatible with 595 drivers:
  it segfaults in `librtx.scenedb.plugin.so` on RTX 5090 + 595.84, even with `--no-window`.
  NVIDIA's answer is to use driver 580 or Isaac Sim 6.x / Isaac Lab 3.0
  (isaac-sim/IsaacLab#6785, isaac-sim/IsaacSim#706).
- Isaac Lab 3.0 EA (`release/3.0.0`, tag `v3.0.0-EA`) targets Isaac Sim 6.1, Python 3.12.
  EA to GA (end of Oct 2026) is bug fixes only; upgrade with `git pull` + `uv sync`.
- Install with `uv run` (no sudo). Add `--extra isaacsim` for Kit, PhysX, RTX.
  Set `OMNI_KIT_ACCEPT_EULA=YES` for SSH runs.

## 3.0 differences from older docs

- Task IDs lost `-v0`: `Isaac-Cartpole`, `Isaac-Reach-Franka`.
  `Isaac-Lift-Cube-Franka-v0` is now `IsaacContrib-Lift-Cube-Franka` (not `Isaac-Lift-Franka`).
- `--headless` and `--enable_cameras` are gone. No `--viz` means headless.
- Renderer presets were renamed to `isaacsim_rtx`, `ovrtx`; the old `*_renderer` names are aliases.
- Quaternions are `(x, y, z, w)`.

## Remote GUI

- X11 forwarding (`ssh -Y`, XQuartz) works for simple apps. Do not use it for Kit.
  Start XQuartz first, or windows close immediately.
- Kit GUI: WebRTC livestream to the macOS Streaming Client at the server's Tailscale IP.
  Works (Streaming Client 2.0.0 on macOS aarch64, signal 49100, stream 47998, 1920x1080):
  `LIVESTREAM=1 PUBLIC_IP=<tailscale-ip> uv run --extra isaacsim isaaclab zero_agent --task IsaacContrib-Lift-Cube-Franka --num_envs 4 --viz kit`
  One client at a time. SSH tunnels cannot carry it (media is UDP).
- Report images: `--video` records mp4 headlessly (needs the `video` extra).

## Verified on the server (RTX 5090, driver 595.84)

- `uv sync`: ~7 min, `.venv` 8.1 GB; Python 3.12.14, torch 2.12.0+cu130 sees the GPU as sm_120.
- `uv sync --extra isaacsim`: ~17 min, `.venv` 27 GB, `isaacsim` 6.1.0.0.
- Kit-less Cartpole (`physics=newton_mjwarp`) and Kit Cartpole (`physics=isaacsim_physx`) both train headless.
- `--video` renders through RTX without crashing (needs `--extra video`). The first frame is black.
  `--video_interval 1` makes one-frame clips; keep the default or use a large interval.

- Isaac Sim 5.1 (pip, via LeIsaac 0.4.0) was re-checked on 2026-09-26: `isaacsim isaacsim.exp.full --no-window`
  reaches `app ready`, then segfaults (exit 139). No Linux workaround short of a 580 driver is known.

## Repo layout

- `patches/`: minimal diffs against upstream Isaac Lab scripts; `scripts/apply_patches.sh` writes patched copies.
- `scripts/capture.sh`, `scripts/burst.sh`: Streaming Client screenshots; `captures/README.md` logs each one with its command.
- `leisaac/`: submodule, `osehyeon/leisaac` branch `isaaclab-3.0`, a port of LightwheelAI/leisaac (Isaac Lab 2.3)
  to Isaac Lab 3.0. Upstream has no plans for Isaac Sim 6 (LightwheelAI/leisaac#167). Commit and push inside the
  submodule first, then commit the new pointer here. Keep changes minimal; commit messages follow the global rules.

## LeIsaac on Isaac Lab 3.0

- Install into the Isaac Lab venv at run time: `uv run --extra isaacsim --with-editable source/isaaclab_teleop --with-editable <leisaac>/source/leisaac ...`.
  LeIsaac registers its tasks through the `isaaclab.tasks` entry point. Assets come from LeIsaac releases
  (`so101_follower.usd` v0.1.0, `table_with_cube.zip` v0.1.2) into `$LEISAAC_ASSETS_ROOT`, not committed.
- `LeIsaac-SO101-LiftCube-v0` steps with its front RGB camera. `scripts/evaluation/policy_inference.py --policy_type random`
  runs full episodes. Nothing may load `pxr` before Kit starts, and the script forces `enable_cameras`.
- The LeRobot policy server runs in its own venv: Python 3.10, `lerobot[smolvla,async]==0.3.3`, torch 2.7.1+cu128.
  Do not install `leisaac[lerobot-async]` into the Isaac Lab venv: its grpc/protobuf pins would downgrade Isaac Lab's.
  The Isaac Lab venv's grpcio 1.83 / protobuf 7.36rc1 talk to the 0.3.3 server fine.
- `--policy_type lerobot-smolvla` works end to end (verified 2026-09-27): 50-step chunks of 6 joints,
  ~100 ms per GetActions on the RTX 5090. The client sends `must_go=True`; without it the server's
  similarity filter can stall a synchronous client forever.
- Checkpoints must be in the lerobot 0.3.x layout (`config.json` + `model.safetensors` with unprefixed
  normalization buffers) and expect `observation.images.front` + 6-dim `observation.state`. Stock
  `lerobot/smolvla_base` needs its features and stats rewritten first.
- Official GR00T N1.5 PickOrange works (2026-09-28): unmodified `LightwheelAI/leisaac-pick-orange-v0` weights,
  `LeIsaac-SO101-PickOrange-v0`, 5/10 successful 60 s episodes. Server: Isaac-GR00T @ 4af2b62 in its own
  Python 3.10 venv with torch 2.7.1+cu128 and the flash-attn 2.8.3 cu12/torch2.7 wheel (the pinned torch 2.5.1
  has no sm_120 kernels); `scripts/inference_service.py --server --embodiment-tag new_embodiment --data-config so100_dualcam --denoising-steps 4`.
  Client adds `--with pyzmq --with msgpack` at run time. ~46 ms median per call (16-step chunks).
- The server binds 0.0.0.0:5555 even with `--host 127.0.0.1`; stop it when done.
- Some scene USDs hide objects with scale (0, 0, 0) but keep a dynamic rigid body with SDF collision (e.g. four
  wall fixtures in kitchen_with_orange). Isaac Sim 6.1 cannot cook them; `assets/scenes/common.py` deactivates
  every zero-scale rigid body at spawn, otherwise
  every RTX camera image is garbage after the first physics step.
- Not ported yet: teleop devices, cloth, mimic, other tasks.

## Known risks

- isaac-sim/IsaacSim#729: `update()` can stall 20-270 s on Blackwell (seen on 6.0.1).
- isaac-sim/IsaacLab#7616: WebRTC black screen; workaround passes stream ports via `--kit_args`.
