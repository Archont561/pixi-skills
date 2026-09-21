# Offline sandbox (orphan branch)

Built 2026-09-21T20:51:31Z from commit `af11418` for platform `linux-64`.
`pixi.lock` sha256 `75ac1f455258a0f6510fbbcf8c17bac1e8056ed3e8050911d1d6a315b9bd9d68`.

The branch root includes `pixi-sandbox`; it is a convenience copy of the verified self-bootstrap binary. The manifest copy remains under `.pixi-sandbox/tools/linux-64/pixi-sandbox` for compatibility with older launchers.

| env | platform | packed | unpacked | files |
| --- | --- | ---: | ---: | ---: |
| `dev` | linux-64 | 471.8 MiB | 1948.3 MiB | 61 |
| `docs` | linux-64 | 85.4 MiB | 333.6 MiB | 40 |

Cargo dependencies: **249 crates**, 216.0 MiB (loose) from `Cargo.lock` sha256 `cd6b0a09b5d5…`; restore materialises them to `.pixi-sandbox/vendor/`. Built with cargo 1.98.1 (797e8a9bc 2026-08-05); rustc 1.98.1 (48a229cea 2026-09-01).

## Restore on the disconnected machine

```bash
./pixi-sandbox doctor --branch-location . --verify
./pixi-sandbox restore --branch-location . --output-path <project> --force
# or: ./restore.sh <project>
# then, with no network:
.pixi/tools/linux-64/pixi install --frozen --offline
source .pixi/sandbox-env.sh
```

Every manifest blob is verified before it is written into the working tree.
