"""
Property checking is performed by the same isolated Docker execution boundary
as ordinary tests. This module only builds a property-test specification.
"""

def identity_property_spec():
    return {
        "name": "identity",
        "description": "solve(x) returns x for representative generated strings",
        "inputs": ["", "x", "hello", "café", "hello\n", "x" * 128],
    }
