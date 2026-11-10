# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Francisco Angulo de Lafuente
# ORCID: 0009-0001-1634-7063
"""Additive strict-JSON export; no imputation or scientific recomputation."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

class NonFinite:
    def __init__(self, token):
        self.token = token

def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key')
        result[key] = value
    return result

def reject_constant(token):
    raise ValueError('Non-RFC8259 numeric literal: ' + token)

def parse(text, strict):
    return json.loads(text, parse_float=Decimal, object_pairs_hook=no_duplicates,
                      parse_constant=reject_constant if strict else NonFinite)

def convert(text):
    source = parse(text, False)
    tokens = re.compile(r'"(?:\\.|[^"\\])*"|NaN|-Infinity|Infinity')
    exported = tokens.sub(lambda m: m.group(0) if m.group(0).startswith('"') else 'null', text)
    target = parse(exported, True)
    changes = []
    def walk(a, b, pointer=''):
        if isinstance(a, NonFinite):
            if b is not None:
                raise ValueError('Non-finite token was not converted to null')
            changes.append({'pointer': pointer, 'original_literal': a.token, 'replacement': None})
        elif isinstance(a, dict):
            if not isinstance(b, dict) or list(a) != list(b):
                raise ValueError('Object structure changed')
            for key in a:
                part = key.replace('~', '~0').replace('/', '~1')
                walk(a[key], b[key], pointer + '/' + part)
        elif isinstance(a, list):
            if not isinstance(b, list) or len(a) != len(b):
                raise ValueError('Array structure changed')
            for i, value in enumerate(a):
                walk(value, b[i], pointer + '/' + str(i))
        elif type(a) is not type(b) or a != b:
            raise ValueError('Finite value changed at ' + pointer)
    walk(source, target)
    return exported, changes

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    paths = [p.resolve() for p in [args.source, args.output, args.manifest]]
    if len(set(paths)) != 3 or args.output.exists() or args.manifest.exists():
        parser.error('Use three distinct paths and two nonexistent output paths')
    original = args.source.read_bytes()
    exported, changes = convert(original.decode('utf-8'))
    data = exported.encode('utf-8')
    info = {
        'source_bytes': len(original), 'source_sha256': hashlib.sha256(original).hexdigest(),
        'derived_bytes': len(data), 'derived_sha256': hashlib.sha256(data).hexdigest(),
        'changed_values': len(changes), 'changes': changes,
        'null_semantics': 'Original non-finite value; not zero or an imputed estimate',
        'scope': 'Serialization only; no scientific recomputation',
    }
    # Validate every value before writing either output. Exclusive creation prevents overwrite.
    manifest_data = (json.dumps(info, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    with args.output.open('xb') as f:
        f.write(data)
    with args.manifest.open('xb') as f:
        f.write(manifest_data)
    print(json.dumps({'derived_sha256': info['derived_sha256'], 'changed_values': len(changes)}))

if __name__ == '__main__':
    main()
