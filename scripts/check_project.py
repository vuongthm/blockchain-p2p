#!/usr/bin/env python3
"""Check package structure, Python syntax, and document signatures offline."""
from pathlib import Path
import ast
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
required = [
    'README.md', 'SHA256SUMS', '.gitignore',
    'reports/Blockchain_P2P_Report_VI.docx',
    'reports/Blockchain_P2P_Report_EN.docx',
    'source/README.md', 'source/app.py',
    'source/blockchain.py', 'source/wallet.py', 'source/storage.py',
    'source/templates/index.html', 'source/requirements.txt',
    'docs/installation.md', 'docs/usage.md', 'docs/architecture.md',
    'docs/api.md', 'docs/testing.md', 'docs/security-and-limitations.md',
]
errors = []
for name in required:
    if not (root / name).is_file():
        errors.append(f'Missing required file: {name}')
for path in sorted((root / 'source').rglob('*.py')):
    try:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    except (SyntaxError, UnicodeError) as exc:
        errors.append(f'{path.relative_to(root)}: {exc}')
for name in ('Blockchain_P2P_Report_VI.docx', 'Blockchain_P2P_Report_EN.docx'):
    path = root / 'reports' / name
    if path.is_file():
        try:
            with zipfile.ZipFile(path) as archive:
                if archive.testzip() is not None or 'word/document.xml' not in archive.namelist():
                    errors.append(f'Invalid Word document: {name}')
        except zipfile.BadZipFile:
            errors.append(f'Invalid Word document: {name}')
if (root / 'docs' / 'vi').exists() or (root / 'README.en.md').exists():
    errors.append('Unexpected localized documentation outside reports/')
if errors:
    print('Package check FAILED:')
    for issue in errors:
        print(' -', issue)
    sys.exit(1)
print('Package structure, Python syntax, and Word file integrity: OK')
print('Note: This static check is not functional, security, or performance testing.')
