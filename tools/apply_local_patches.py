"""Apply/restore the two captured local patches to an iLED Python 3.10 env."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'iled_main.cpython-310-x86_64-linux-gnu.so': '63ad00e866c69c74f304a6917cefa63eeb075a1dec04e1c968f26db0151c1798',
    'runtime_guard.cpython-310-x86_64-linux-gnu.so': 'e7eccfa3aa6160f49c3d711bb4396c3be584380e72607f5c854760389e0c5427',
    'CDLE/AutoRun.cpython-310-x86_64-linux-gnu.so': 'b89dbc8ebf6dbd82960dcb18c4d8460aa0e161a886c044c2b75d35bf7cdc3156',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, data, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.iled-local-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run(prefix, restore):
    site = prefix / 'lib/python3.10/site-packages'
    for name, expected in EXPECTED.items():
        if sha((site / name).read_bytes()) != expected:
            raise RuntimeError('Native module differs from the captured iLED version: ' + name)
    state = prefix / '.iled-local-snapshot'
    manifest = state / 'manifest.json'
    if restore:
        records = json.loads(manifest.read_text())
        # Validate every target before restoring any of them.
        for record in records:
            if sha(Path(record['path']).read_bytes()) != record['patched_sha256']:
                raise RuntimeError('Target changed after patching: ' + record['path'])
        for record in reversed(records):
            target = Path(record['path'])
            if record['backup']:
                original = (state / record['backup']).read_bytes()
                if sha(original) != record['original_sha256']:
                    raise RuntimeError('Backup checksum mismatch')
                write(target, original, record['mode'])
            else:
                target.unlink()
        manifest.rename(state / 'restored-manifest.json')
        print('Restored original launcher and removed the two patch modules.')
        return
    launcher = prefix / 'bin/iLED'
    original = launcher.read_bytes()
    old, new = b'from iled_main import main', b'from iled_local_launcher import main'
    if manifest.exists():
        records = json.loads(manifest.read_text())
        if all(sha(Path(r['path']).read_bytes()) == r['patched_sha256'] for r in records):
            print('Both local patches are already installed.')
            return
        raise RuntimeError('An existing patch installation has changed')
    if original.count(old) != 1:
        raise RuntimeError('Unexpected iLED launcher; refusing to overwrite it')
    targets = [
        (launcher, original.replace(old, new, 1)),
        (site / 'iled_local_launcher.py', (ROOT / 'patches/iled_local_launcher.py').read_bytes()),
        (site / 'CDLE/AutoRun/__init__.py', (ROOT / 'patches/AutoRun/__init__.py').read_bytes()),
    ]
    if any(target.exists() for target, _ in targets[1:]):
        raise RuntimeError('A patch module already exists; refusing to overwrite it')
    state.mkdir(exist_ok=True)
    records = []
    for index, (target, data) in enumerate(targets):
        previous = target.read_bytes() if target.exists() else None
        mode = target.stat().st_mode & 0o777 if target.exists() else 0o644
        backup = str(index) + '.original' if previous is not None else None
        if previous is not None:
            write(state / backup, previous, mode)
        records.append({'path': str(target), 'backup': backup, 'mode': mode,
                        'original_sha256': sha(previous) if previous is not None else None,
                        'patched_sha256': sha(data)})
    write(manifest, (json.dumps(records, indent=2) + '\n').encode(), 0o600)
    for (target, data), record in zip(targets, records):
        write(target, data, record['mode'])
    print('Installed both local patches in ' + str(prefix))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=Path(sys.prefix))
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    run(args.prefix.resolve(), args.restore)
