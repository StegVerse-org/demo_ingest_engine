import argparse
from pathlib import Path
from .extract import extract_if_zip
from .install import install_bundle

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    i = sub.add_parser("install")
    i.add_argument("source")
    i.add_argument("--target", required=True)
    i.add_argument("--archive", action="store_true")

    args = parser.parse_args()

    if args.cmd == "install":
        source = Path(args.source).resolve()
        target = Path(args.target).resolve()
        src = extract_if_zip(source)
        install_bundle(src, target, args.archive)

if __name__ == "__main__":
    main()
