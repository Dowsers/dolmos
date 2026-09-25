import pytest
from eth_hash.auto import keccak

from dolmos.solve import (
    ModelVariable,
    keccak_fact,
    parse_model_str,
    parse_sha3_arg_values,
    sha3_arg_decls,
)


@pytest.mark.parametrize(
    "full_name",
    [
        "dolmos_y_uint256_043cfd7_01",
        "p_y_uint256_043cfd7_01",
    ],
)
def test_smtlib_z3_bv_output(full_name):
    smtlib_str = f"""
        (define-fun {full_name} () (_ BitVec 256)
        #x0000000000000000000000000000000000000000000000000000000000000000)
    """
    model = parse_model_str(smtlib_str)

    assert model[full_name] == ModelVariable(
        full_name=full_name,
        variable_name="y",
        solidity_type="uint256",
        smt_type="BitVec 256",
        size_bits=256,
        value=0,
    )


# note that yices only produces output like this with --smt2-model-format
# otherwise we get something like (= x #b00000100)
@pytest.mark.parametrize(
    "full_name",
    [
        "dolmos_z_uint256_cabf047_02",
        "p_z_uint256_cabf047_02",
    ],
)
def test_smtlib_yices_binary_output(full_name):
    smtlib_str = f"""
    (define-fun
        {full_name}
        ()
        (_ BitVec 256)
        #b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
    """
    model = parse_model_str(smtlib_str)
    assert model[full_name] == ModelVariable(
        full_name=full_name,
        variable_name="z",
        solidity_type="uint256",
        smt_type="BitVec 256",
        size_bits=256,
        value=1 << 255,
    )


@pytest.mark.parametrize(
    "full_name",
    [
        "dolmos_z_uint256_11ce021_08",
        "p_z_uint256_11ce021_08",
    ],
)
def test_smtlib_yices_decimal_output(full_name):
    val = 57896044618658097711785492504343953926634992332820282019728792003956564819968
    smtlib_str = f"""
        (define-fun {full_name} () (_ BitVec 256) (_ bv{val} 256))
    """
    model = parse_model_str(smtlib_str)
    assert model[full_name] == ModelVariable(
        full_name=full_name,
        variable_name="z",
        solidity_type="uint256",
        smt_type="BitVec 256",
        size_bits=256,
        value=val,
    )


@pytest.mark.parametrize(
    "full_name",
    [
        "dolmos_x_uint8_043cfd7_01",
        "p_x_uint8_043cfd7_01",
    ],
)
def test_smtlib_stp_output(full_name):
    # we should tolerate:
    # - the extra (model) command
    # - duplicate variable names
    # - the initial `sat` result
    # - the `|` around the variable name
    # - the space in `( define-fun ...)`
    smtlib_str = f"""
        sat
        (model
        ( define-fun |{full_name}| () (_ BitVec 8) #x04 )
        )
        (model
        ( define-fun |{full_name}| () (_ BitVec 8) #x04 )
        )
    """
    model = parse_model_str(smtlib_str)
    assert model[full_name] == ModelVariable(
        full_name=full_name,
        variable_name="x",
        solidity_type="uint8",
        smt_type="BitVec 8",
        size_bits=8,
        value=4,
    )


@pytest.mark.parametrize(
    "smtlib_str",
    [
        # z3
        "(define-fun sha3arg_0 () (_ BitVec 256)\n  #x000000000000000000000000000000000000000000000000000000000000002a)"
        "(define-fun sha3arg_1 () (_ BitVec 16) #x0001)",
        # yices --smt2-model-format --bvconst-in-decimal
        "(define-fun sha3arg_0 () (_ BitVec 256) (_ bv42 256))"
        "(define-fun sha3arg_1 () (_ BitVec 16) (_ bv1 16))",
        # yices --smt2-model-format
        "(define-fun sha3arg_0 () (_ BitVec 256) #b" + "0" * 250 + "101010)"
        "(define-fun sha3arg_1 () (_ BitVec 16) #b0000000000000001)",
    ],
)
def test_parse_sha3_arg_values(smtlib_str):
    values = parse_sha3_arg_values(
        "sat\n(define-fun p_x_uint256_00 () (_ BitVec 256) (_ bv7 256))\n" + smtlib_str
    )
    assert values == {0: (256, 42), 1: (16, 1)}


def test_keccak_fact():
    fact, hash_value = keccak_fact(256, 42)
    expected = int.from_bytes(keccak((42).to_bytes(32, "big")), "big")
    assert hash_value == expected
    assert fact == f"(assert (= (f_sha3_256 (_ bv42 256)) (_ bv{expected} 256)))\n"


def test_sha3_arg_decls():
    decls = sha3_arg_decls(((256, "p_x_uint256_00"), (512, "(concat a b)")))
    assert decls == (
        "(declare-fun sha3arg_0 () (_ BitVec 256))\n"
        "(assert (= sha3arg_0 p_x_uint256_00))\n"
        "(declare-fun sha3arg_1 () (_ BitVec 512))\n"
        "(assert (= sha3arg_1 (concat a b)))\n"
    )
