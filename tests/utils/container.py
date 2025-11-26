import logging
import os
import shlex
import subprocess
from pathlib import Path
from typing import Self, Sequence

log = logging.getLogger(__name__)


class Container:
    def __init__(self, image_name: str) -> None:
        self._image_name = image_name

    @property
    def image_name(self) -> str:
        return self._image_name

    @classmethod
    def build_image(cls, context_dir: Path, image_name: str) -> Self:
        subprocess.run(
            ["podman", "build", "--tag", image_name, context_dir],
            check=True,
        )
        return cls(image_name)

    def run_cmd(
        self,
        cmd: Sequence[str | os.PathLike[str]],
        check: bool = True,
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        podman_cmd = ["podman", "run", "--rm", self.image_name, *cmd]

        log.debug("%s", shlex.join(map(str, podman_cmd)))
        proc = subprocess.run(podman_cmd, capture_output=capture_output, text=True)

        if capture_output:
            if stdout := proc.stdout.rstrip("\n"):
                log.debug("stdout>\n%s", stdout)
            if stderr := proc.stderr.rstrip("\n"):
                log.error("stderr>\n%s", stderr)

        if check:
            proc.check_returncode()

        return proc
