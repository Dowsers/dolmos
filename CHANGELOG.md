# Changelog

All notable changes to dolmos are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow
[Semantic Versioning](https://semver.org/). Dolmos is derived from halmos; see
[NOTICE](NOTICE) for the upstream commit it is based on.

## [Unreleased]

### Added

- `vm.expectRevert` (all overloads, including the reverter address and `count`
  variants), `vm.expectPartialRevert`, `vm.expectEmit` and
  `vm.expectEmitAnonymous` (including the emitter address and `count` variants),
  with foundry's semantics; symbolic revert data and event fields are matched
  symbolically and a counterexample is reported when an expectation can be
  violated (halmos#409)
- multiple setup states: when `setUp()` has several feasible successful paths,
  each test and each invariant test sequence is run from every one of them,
  instead of failing with "Multiple paths were found in setUp()" (halmos#186)
- experimental: `--dump-lassos DIR` exports each loop that reaches the unrolling
  bound as a lasso program, and `--pasttel BINARY` analyses it with PaSTTeL
  (termination proof with a ranking function, or non-termination). Lassos use
  a small-constants encoding by default, because PaSTTeL computes with doubles
  and is unsound on 2^256 constants; `--lasso-exact-constants` gives the exact
  encoding. See docs/loop-termination.md
- `SELFDESTRUCT` opcode, with the EIP-6780 (Cancun) semantics: the balance is sent to
  the beneficiary and the frame halts; the account (code, storage, balance, nonce) is
  deleted at the end of the transaction only if it was created in that transaction;
  forbidden in static contexts (halmos#411)

### Fixed

- SHA256, RIPEMD160 and MODEXP precompiles with symbolic input no longer crash
  with a z3 sort mismatch (input sizes were given in bytes instead of bits).
  Concrete inputs are now evaluated exactly; MODEXP follows EIP-198 (zero-padded
  input, output on `len(M)` bytes) and EIP-7823 (lengths above 1024 bytes make
  the call fail), and its symbolic model guarantees `result < M` (halmos#402)
- storage slots written as precomputed keccak256 literals (e.g. constant-folded by the
  via-IR optimizer in a constructor) and read through SHA3 at runtime now hit the same
  storage cell, instead of reading zero and reporting a false counterexample; applies to
  both storage layouts (halmos#579)
- counterexamples relying on keccak256 values that differ from the real hash function
  (keccak256 is uninterpreted, so the solver could pick e.g. `x = 0` and assume that its
  hash is the key of a storage entry) are no longer reported as valid. The real hashes of
  the preimages chosen by the model are added to the query, which is solved again, up to
  `--keccak-refinement-rounds` times (default 3, 0 disables the check); a counterexample
  that still disagrees is reported as potentially invalid (halmos#562)

## [0.1.0] - 2026-09-22

First release of dolmos.

### Added

- CREATE address derivation from `keccak256(rlp([sender, nonce]))` and account
  nonces (EIP-161), so that CREATE3-style address prediction matches execution
- nonce cheatcodes: `vm.getNonce`, `vm.setNonce`, `vm.setNonceUnsafe`,
  `vm.resetNonce`
- opcodes `CLZ` (EIP-7939), `BLOBHASH` and `BLOBBASEFEE` (EIP-4844)
- experimental Vyper support: Vyper test contracts, Solidity tests targeting
  Vyper contracts, `@custom:dolmos` annotations in docstrings,
  `--invalid-as-failure`
- `dolmos.toml` configuration file and `@custom:dolmos` annotations
  (`halmos.toml`, `@custom:halmos` and `HALMOS_ALLOW_DOWNLOAD` remain accepted)
- PyPI package and Docker image `ghcr.io/dowsers/dolmos`

### Changed

- command, Python package and symbolic variable prefix renamed from `halmos` to
  `dolmos`; downloaded solvers are cached in `~/.dolmos/solvers`

### Fixed

- Vyper artifact lookup in the forge cache on Windows
- builds with forge ≥ 1.8: `dynamic_test_linking` is disabled when dolmos runs
  `forge build`, since it rewrites `new C()` into unsupported `vm.deployCode`
  calls

[Unreleased]: https://github.com/Dowsers/dolmos/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Dowsers/dolmos/releases/tag/v0.1.0
