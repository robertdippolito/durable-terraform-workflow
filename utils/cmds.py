from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Union


async def run_tf_init_command(directory: Union[str, Path]) -> str:
    proc = await asyncio.create_subprocess_exec(
        "terraform",
        "init",
        "-input=false",
        cwd=str(directory),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout, _ = await proc.communicate()
    if proc.returncode:
        raise RuntimeError(
            f"Error running terraform init -input=false : {stdout.decode().strip()}"
        )
    return stdout.decode()

async def run_tf_plan_command(directory: Union[str, Path], vpc_cidr: str) -> str:
    proc = await asyncio.create_subprocess_exec(
        "terraform",
        "plan",
        "-input=false",
        "-var",
        f"vpc_cidr={vpc_cidr}",
        cwd=str(directory),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    if proc.returncode:
        raise RuntimeError(
            f"Error running terraform plan -input=false -var vpc_cidr={vpc_cidr}: {stdout.decode().strip()}"
        )
    return stdout.decode()


async def run_tf_output_command(directory: Union[str, Path]) -> str:
    proc = await asyncio.create_subprocess_exec(
        "terraform",
        "output",
        "-json",
        cwd=str(directory),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout, _ = await proc.communicate()
    if proc.returncode:
        raise RuntimeError(
            f"Error running terraform output -json: {stdout.decode().strip()}"
        )
    return stdout.decode()
