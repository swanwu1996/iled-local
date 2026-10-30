"""Report the installed integration and upstream versions."""
import importlib.metadata
import json
import platform
import sys


def main():
    print(json.dumps({
        'integration': importlib.metadata.version('iled-local'),
        'upstream': importlib.metadata.version('iLED'),
        'python': platform.python_version(),
        'platform': platform.platform(),
        'environment': sys.prefix,
    }, indent=2))
