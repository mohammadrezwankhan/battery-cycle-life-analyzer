"""Build and validate reproducible release distributions."""

import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def normalize_source_archive(archive: Path, epoch: int) -> None:
    # Setuptools honors SOURCE_DATE_EPOCH for wheels, while its sdist
    # still records the time of the build in tar members and the gzip header.
    with tempfile.TemporaryDirectory(dir=archive.parent) as temporary:
        replacement = Path(temporary) / archive.name
        with (
            tarfile.open(archive, "r:gz") as source,
            replacement.open("wb") as raw,
            gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=epoch) as compressed,
            tarfile.open(fileobj=compressed, mode="w|") as output,
        ):
            for member in sorted(source.getmembers(), key=lambda item: item.name):
                if not (member.isfile() or member.isdir()):
                    raise ValueError(f"Unexpected source archive member type: {member.name}")
                normalized = member.replace(mtime=epoch, uid=0, gid=0, uname="", gname="")
                for field in ("atime", "ctime", "mtime"):
                    normalized.pax_headers.pop(field, None)
                if member.isfile():
                    with source.extractfile(member) as payload:
                        output.addfile(normalized, payload)
                else:
                    output.addfile(normalized)
        replacement.replace(archive)


def build_distributions(output: Path, environment: dict[str, str], epoch: int) -> dict[str, str]:
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation", "--outdir", str(output.resolve())],
        env=environment,
        check=True,
    )
    archives = sorted(output.glob("*.tar.gz"))
    wheels = sorted(output.glob("*.whl"))
    if len(archives) != 1 or len(wheels) != 1:
        raise RuntimeError("Expected exactly one source distribution and one wheel.")
    archive, wheel = archives[0], wheels[0]
    normalize_source_archive(archive, epoch)
    # Both paths come from the distributions just built in this output directory.
    subprocess.run(  # noqa: S603
        [sys.executable, "-m", "twine", "check", "--strict", str(archive), str(wheel)],
        check=True,
    )
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (archive, wheel)
    }


def main() -> None:
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("Git is required to resolve the release timestamp.")
    source_commit = subprocess.check_output(  # noqa: S603
        [git, "rev-parse", "HEAD"], text=True
    ).strip()
    workflow_commit = os.environ.get("GITHUB_SHA")
    if workflow_commit and workflow_commit.lower() != source_commit.lower():
        raise RuntimeError(
            "Checked-out source commit "
            f"{source_commit} does not match workflow commit {workflow_commit}."
        )
    epoch = int(
        subprocess.check_output(  # noqa: S603
            [git, "show", "-s", "--format=%ct", "HEAD"], text=True
        ).strip()
    )
    environment = {**os.environ, "SOURCE_DATE_EPOCH": str(epoch)}
    output = Path("dist")
    first_hashes = build_distributions(output, environment, epoch)
    with tempfile.TemporaryDirectory(prefix="bcla-release-repeat-") as temporary:
        repeated_hashes = build_distributions(Path(temporary) / "dist", environment, epoch)
    if first_hashes != repeated_hashes:
        raise RuntimeError(
            "Repeated release builds from the same source commit differ: "
            f"first={first_hashes!r}, repeated={repeated_hashes!r}"
        )

    provenance = {
        "source_commit": source_commit,
        "source_date_epoch": epoch,
        "repeat_build_byte_identical": True,
        "distribution_sha256": first_hashes,
    }
    encoded = json.dumps(provenance, sort_keys=True)
    print(f"Release provenance: {encoded}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as report:
            report.write("## Release distribution provenance\n\n")
            report.write(f"- Source commit: `{source_commit}`\n")
            report.write(f"- `SOURCE_DATE_EPOCH`: `{epoch}`\n")
            report.write("- Repeated build bytes: identical\n")
            for name, digest in sorted(first_hashes.items()):
                report.write(f"- SHA-256 `{name}`: `{digest}`\n")


if __name__ == "__main__":
    main()
