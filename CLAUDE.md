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
  TCP 49100 and UDP 47998 pass over Tailscale in both directions. Kit streaming itself is untested.
  SSH tunnels cannot carry it (media is UDP).
- Report images: `--video` records mp4 headlessly (needs the `video` extra).

## Known risks

- isaac-sim/IsaacSim#729: `update()` can stall 20-270 s on Blackwell (seen on 6.0.1).
- isaac-sim/IsaacLab#7616: WebRTC black screen; workaround passes stream ports via `--kit_args`.
