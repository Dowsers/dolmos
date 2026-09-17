# Dolmos

[![License](https://img.shields.io/github/license/HugoDowsers/dolmos)](LICENSE)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FHugoDowsers%2Fdolmos%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)](pyproject.toml)
[![upstream](https://img.shields.io/badge/fork%20of-a16z%2Fhalmos-blue)](https://github.com/a16z/halmos)

Dolmos is the [Dowsers](https://github.com/HugoDowsers) fork of
[a16z/halmos](https://github.com/a16z/halmos), a _symbolic testing_ tool for EVM
smart contracts driven by Foundry tests.

The fork exists to carry fixes and EVM coverage we need for audit work, ahead of
(or instead of) upstream. Everything upstream does, dolmos does; this README only
documents what differs. For the tool itself, read the upstream
[getting started guide](docs/getting-started.md) and the
[examples](examples/README.md) — they apply unchanged, modulo the command name.

The command is `dolmos`. The Python package is still named `halmos`, so
`import halmos` and rebases on upstream keep working.

## What this fork adds

**CREATE address derivation and account nonces.** Upstream assigns CREATE
addresses from a counter and does not model nonces at all, so a contract that
predicts its own deployment address disagrees with the executor. Every CREATE3
library breaks that way ([a16z/halmos#217](https://github.com/a16z/halmos/issues/217)):
all paths revert and the test reports `paths: 0`. Dolmos tracks nonces (1 for a
newly created account per EIP-161, incremented by CREATE and CREATE2 even when
the creation fails) and derives the address from `keccak256(rlp([sender, nonce]))`,
mapped to a magic address exactly as CREATE2 already was. Both sides of the
prediction then agree.

**Nonce cheatcodes.** `vm.getNonce`, `vm.setNonce`, `vm.setNonceUnsafe` and
`vm.resetNonce`, with foundry's semantics: `setNonce` only raises a nonce,
`resetNonce` gives 0 to EOAs and 1 to accounts with code.

**Fusaka / Cancun opcodes.** `CLZ` (EIP-7939), with a concrete fast path and a
logarithmic symbolic encoding, plus `BLOBHASH` and `BLOBBASEFEE` (EIP-4844).

**CLI.** The command is `dolmos`; `halmos` is no longer installed. A project
config file may be named `dolmos.toml` (read before `halmos.toml`), `--help` and
`--version` report the name the command was invoked with, and `-test` is a short
alias for `--match-test` (`dolmos -test setNonce`).

## Not available in this fork

These exist upstream and are **not** provided here yet:

| | status |
|---|---|
| PyPI package (`pip install dolmos`) | not published — install from source |
| `uv tool install dolmos` | not available — depends on the PyPI package |
| Docker image (`ghcr.io/...`) | not built — no published image |
| Prebuilt release binaries | none |
| CI workflows | inherited from upstream and currently broken on this fork, since they invoke the `halmos` command and the a16z docker image |

Until then, install from source as described below. If you want the packaged
experience today, use upstream halmos instead — the two can coexist in the same
environment, they no longer share a command name.

## Installation

Requires Python ≥ 3.11 and [Foundry](https://getfoundry.sh).

```sh
git clone https://github.com/HugoDowsers/dolmos.git
cd dolmos
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
dolmos --version
```

Development install, with the test and lint dependencies:

```sh
pip install -e ".[dev]"
pre-commit install
```

If a `halmos` command lingers in your `PATH` after installing, it comes from a
separate installation (typically a `pip install --user` one). Check with
`type -a halmos`, and `python -c "import halmos, os; print(os.path.dirname(halmos.__file__))"`
to confirm which source tree is actually being imported.

## Usage

```sh
cd /path/to/foundry/project
forge build
dolmos
```

```sh
dolmos --help
dolmos -test <regex>          # alias for --match-test
dolmos --match-contract <regex>
```

Options can be set per project in `dolmos.toml` at the project root, with the
same format as upstream's `halmos.toml`:

```toml
[global]
solver-timeout-assertion = 10000
```

## Tests

The regression suite lives in `tests/regression` and runs with both forge (real
EVM) and dolmos (symbolic):

```sh
cd tests/regression
forge build
dolmos
```

Two notes on the toolchain. The suite sets `evm_version = 'osaka'` because of
the CLZ tests, and `test/OpCodesCLZ.sol` needs a solc recent enough to accept
`clz()` in assembly — an older compiler fails with `Function "clz" not found`.
And `test/Invalid.t.sol`, inherited from upstream, requires solc `^0.5.2`; if
that version is unavailable, `forge build` stops there.

## Contributing

Fixes that are not specific to Dowsers should go upstream: branch off
`upstream/main`, keep the branch free of any fork-specific change, and open the
pull request against
[a16z/halmos](https://github.com/a16z/halmos). The CREATE3 work above is written
that way and is meant to be proposed.

See the upstream [contributing guidelines](CONTRIBUTING.md) for style, tests and
commit conventions.

## Roadmap

Work in progress, not merged here yet:

- MODEXP precompile (EIP-198): concrete evaluation and a typed uninterpreted
  function instead of the current opaque one
- performance: skip the Z3 `substitute()` traversal when no free variable
  matches, bound the concurrency of solver subprocesses, memoize invariant
  target resolution
- support multiple `setUp()` states ([a16z/halmos#186](https://github.com/a16z/halmos/issues/186))
- docker image and a published package

## License

AGPL-3.0, inherited from upstream. See [LICENSE](LICENSE).

## Disclaimer

_These smart contracts and code are being provided as is. No guarantee,
representation or warranty is being made, express or implied, as to the safety
or correctness of the user interface or the smart contracts and code. They have
not been audited and as such there can be no assurance they will work as
intended, and users may experience delays, failures, errors, omissions or loss
of transmitted information. THE SMART CONTRACTS AND CODE CONTAINED HEREIN ARE
FURNISHED AS IS, WHERE IS, WITH ALL FAULTS AND WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING ANY WARRANTY OF MERCHANTABILITY, NON-INFRINGEMENT
OR FITNESS FOR ANY PARTICULAR PURPOSE._

This fork is maintained by Dowsers and is not affiliated with or endorsed by
a16z. The upstream disclaimer above applies to the original work; the same lack
of warranty applies to the changes made here.
