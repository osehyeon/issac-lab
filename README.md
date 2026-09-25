# issac-lab

Notes and small experiments with Isaac Lab 3.0 (EA) and Isaac Sim 6.1 on an RTX 5090.

| Path | Contents |
|---|---|
| `docs/` | Install guide, tutorial notes, literature notes |
| `patches/` | Minimal diffs against upstream Isaac Lab scripts |
| `scripts/` | `apply_patches.sh` (build patched scripts), capture helpers |
| `captures/` | Screenshots with the commands that produced them |

Apply the patches to an Isaac Lab checkout:

```bash
ISAACLAB=~/IsaacLab scripts/apply_patches.sh ~/patched
```
