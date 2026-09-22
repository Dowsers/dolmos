# Changelog

All notable changes to dolmos are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow
[Semantic Versioning](https://semver.org/). Dolmos is derived from halmos; see
[NOTICE](NOTICE) for the upstream commit it is based on.

## [Unreleased]

## [0.1.0] - YYYY-MM-DD

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
