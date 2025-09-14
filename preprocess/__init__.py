"""Preprocess package exports.

Re-export selected modules so consumers can import from
`preprocess` directly, e.g. `from preprocess import punkt_tokenize`.
"""

# Ensure project root is on sys.path when executed directly
# This allows `import punkt_tokenize` to work even if Python's CWD
# is the `preprocess/` directory (e.g., running this file directly).
import os
import sys

_repo_root = os.path.dirname(os.path.dirname(__file__))
print(_repo_root)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
print(sys.path)

# Re-export the punkt_tokenize package (sibling top-level package)
import punkt_tokenize as punkt_tokenize  # noqa: F401

# Optionally expose text_normalizer here as well (already present in this pkg)
import text_normalizer as text_normalizer  # noqa: F401

__all__ = [
    "punkt_tokenize",
    "text_normalizer",
]
