"""Build and validate release distributions with a stable source timestamp."""

import gzip
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


def main() -> None:
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("Git is required to resolve the release timestamp.")
    epoch = int(subprocess.check_output([git, "show", "-s", "--format=%ct", "HEAD"]))  # noqa: S603
    environment = {**os.environ, "SOURCE_DATE_EPOCH": str(epoch)}
    subprocess.run([sys.executable, "-m", "build", "--no-isolation"], env=environment, check=True)
    archive, = Path("dist").glob("*.tar.gz")
    wheel, = Path("dist").glob("*.whl")
    normalize_source_archive(archive, epoch)
    # Both paths come from the distributions just built in dist/.
    subprocess.run(  # noqa: S603
        [sys.executable, "-m", "twine", "check", "--strict", str(archive), str(wheel)],
        check=True,
    )


if __name__ == "__main__":
    main()
