"""Rebuild fictional fixture hashes and artifacts without network access."""
import argparse
import json
from pathlib import Path
from writing_session import prepare, run_session

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for stem in ('revision', 'agency', 'outline', 'inspiration'):
        data = json.loads((ROOT / f'examples/{stem}-input.json').read_text(encoding='utf-8'))
        path = ROOT / f'examples/{stem}-proposal.json'
        proposal = json.loads(path.read_text(encoding='utf-8'))
        proposal['input_hash'] = prepare(data)['input_hash']
        result = run_session({**data, 'proposal': proposal})
        artifacts = {path: json.dumps(proposal, ensure_ascii=False, indent=2) + '\n',
                     ROOT / f'examples/{stem}-review.md': result['markdown']}
        for file, content in artifacts.items():
            if args.check:
                if file.read_text(encoding='utf-8') != content:
                    raise SystemExit(f'Example drift: {file.name}')
            else:
                file.write_text(content,encoding='utf-8',newline='')
    print('Four fictional examples match their inputs and contracts.')


if __name__ == '__main__': main()
