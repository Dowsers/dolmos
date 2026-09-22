# Dolmos

[![License](https://img.shields.io/github/license/Dowsers/dolmos)](LICENSE)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FDowsers%2Fdolmos%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)](pyproject.toml)

Dolmos is a _symbolic testing_ tool for EVM smart contracts, driven by
Foundry-style tests, maintained by [Dowsers](https://github.com/Dowsers) for its
audit and formal verification work. Tests look like fuzz tests, but inputs are
symbolic: a passing test holds for every input, and a failing one comes with a
counterexample.

Start with the [getting started guide](docs/getting-started.md) and the
[examples](examples/README.md).

## Features

On top of symbolic execution of Solidity (and Vyper) tests with `check_*` and
`invariant_*` functions, dolmos provides the following.

**CREATE address derivation and account nonces.** Accounts carry nonces (1 for a
newly created account per EIP-161, incremented by CREATE and CREATE2 even when
the creation fails), and CREATE addresses are derived from
`keccak256(rlp([sender, nonce]))`, mapped to a magic address as for CREATE2. A
contract that predicts its own deployment address, as every CREATE3 library
does, therefore agrees with the executor.

**Nonce cheatcodes.** `vm.getNonce`, `vm.setNonce`, `vm.setNonceUnsafe` and
`vm.resetNonce`, with foundry's semantics: `setNonce` only raises a nonce,
`resetNonce` gives 0 to EOAs and 1 to accounts with code.

**Fusaka / Cancun opcodes.** `CLZ` (EIP-7939), with a concrete fast path and a
logarithmic symbolic encoding, plus `BLOBHASH` and `BLOBBASEFEE` (EIP-4844).

**Vyper.** Test contracts can be written in Vyper, and Solidity tests can target
Vyper contracts. forge's Vyper artifacts have no AST, no metadata and an empty
`methodIdentifiers`; dolmos reads `.vy`/`.vyi` artifacts, computes the selectors
from the ABI, takes the source path and compiler version from forge's cache, and
makes Vyper contracts visible to Solidity tests (deployed code, ABI for
invariant targets and traces, including contracts with immutables).
`vm.getCode` accepts `Foo.vy`, `src/Foo.vy` and `Foo.vy:Foo`.

A Vyper test looks like a Solidity one: `setUp()` and `check_*`/`invariant_*`
functions, with cheatcodes called through an interface at
`0x7109709ECfa91a80626fF3989D68f67F5b1DD12D`. Use `assert ..., UNREACHABLE` for
properties: it compiles to the INVALID opcode, which the `--invalid-as-failure`
option reports as a failure, even when it is hit in a nested call and bubbles up
as an empty revert. A plain `assert` is an empty revert, indistinguishable from
a `require`, so the path is silently discarded. The `vm.assert*` cheatcodes work
as well. `@custom:dolmos` annotations go in the module and function docstrings.

When the build contains Vyper contracts, `--storage-layout generic` (Vyper
computes `HashMap` slots as `keccak256(slot . key)`) and `--invalid-as-failure`
become the defaults; a value set in `dolmos.toml`, an annotation or on the
command line still wins. Coverage reports do not include Vyper code, since forge
emits no source maps for it. See `tests/vyper` for examples.

## Compatibility with halmos

Dolmos is derived from halmos (see [NOTICE](NOTICE)) and accepts the names used
by test suites written for it, so they should run without changes:

| halmos | dolmos | |
|---|---|---|
| `@custom:halmos` | `@custom:dolmos` | both accepted, in contracts and functions |
| `halmos.toml` | `dolmos.toml` | `dolmos.toml` is read first |
| `HALMOS_ALLOW_DOWNLOAD` | `DOLMOS_ALLOW_DOWNLOAD` | both honored |
| `halmos-cheatcodes` | unchanged | the `svm.*` cheatcodes of this library are supported |

Some things do change: the command and the Python package are named `dolmos`
(`import dolmos`), symbolic variables in counterexamples are prefixed with
`dolmos_`, and solvers downloaded on demand are cached in `~/.dolmos/solvers`.

## Installation

Requires Python ≥ 3.11 and [Foundry](https://getfoundry.sh). Dolmos is not
published on PyPI and has no prebuilt binaries or published Docker image yet, so
install it from source:

```sh
git clone https://github.com/Dowsers/dolmos.git
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

The Docker images are built by the `publish-solvers-package`,
`publish-dolmos-builder-package` and `publish-dolmos-package` workflows, in that
order, and pushed to `ghcr.io/<owner>/`. The workflows that run tests inside
those images (`test-ffi`, `test-long`, `test-external`) need them to be
published first.

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

Options can be set per project in `dolmos.toml` at the project root:

```toml
[global]
solver-timeout-assertion = 10000
```

`python -m dolmos.config` prints every option with its default value, in that
format. Warnings link to their explanation in [docs/warnings.md](docs/warnings.md).

## Tests

```sh
pytest                                   # unit tests and integration tests
pytest tests/test_dolmos.py -k "not long"
```

The regression suite lives in `tests/regression` and runs with both forge (real
EVM) and dolmos (symbolic):

```sh
cd tests/regression
forge build
dolmos
```

A few notes on the toolchain:

- The suite sets `evm_version = 'osaka'` because of the CLZ tests, and
  `test/OpCodesCLZ.sol` needs a solc recent enough to accept `clz()` in assembly
  (0.8.31 or later); an older compiler fails with `Function "clz" not found`.
- `test/Invalid.t.sol` requires solc `^0.5.2`; if that version is unavailable,
  `forge build` stops there.
- `test/Arith.t.sol` uses the `bitwuzla-abs` solver; set
  `DOLMOS_ALLOW_DOWNLOAD=1` to let dolmos download it.
- The Vyper tests live in `tests/vyper` and need the `vyper` compiler in `PATH`
  (`pip install vyper`); pytest skips them otherwise.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Roadmap

- MODEXP precompile (EIP-198): concrete evaluation and a typed uninterpreted
  function instead of the current opaque one
- performance: skip the Z3 `substitute()` traversal when no free variable
  matches, bound the concurrency of solver subprocesses, memoize invariant
  target resolution
- support multiple `setUp()` states
- a published package and Docker image

## License

AGPL-3.0, see [LICENSE](LICENSE). Dolmos is a modified version of another
AGPL-3.0 program; [NOTICE](NOTICE) gives its origin and the notices that come
with it.

## Disclaimer

_This software and the smart contracts in this repository are provided as is,
without warranty of any kind, express or implied, including any warranty of
merchantability, non-infringement or fitness for a particular purpose. They have
not been audited. Passing symbolic tests is not a proof that a contract is free
of bugs. Nothing in this repository is investment or legal advice. See
[NOTICE](NOTICE) for the disclaimers attached to the original work this code is
derived from._
