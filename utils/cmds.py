from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Mapping, Union


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

async def run_tf_plan_with_tfvars(
    directory: Union[str, Path],
    vars_mapping: Mapping[str, object] | None = None,
    tfvars_path: Union[str, Path] | None = None,
) -> str:
    cleanup_path: str | None = None
    if tfvars_path is not None:
        var_file = str(tfvars_path)
    elif vars_mapping:
        with NamedTemporaryFile("w+", suffix=".auto.tfvars.json", delete=False) as tmp:
            json.dump(vars_mapping, tmp)
            tmp.flush()
            cleanup_path = tmp.name
            var_file = tmp.name
    else:
        raise ValueError("Either vars_mapping or tfvars_path must be provided")

    args = ["terraform", "plan", "-input=false", f"-var-file={var_file}"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=str(directory),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode:
            raise RuntimeError(
                f"Error running {' '.join(args)}: {stdout.decode().strip()}"
            )
        return stdout.decode()
    finally:
        if cleanup_path and os.path.exists(cleanup_path):
            os.remove(cleanup_path)

async def run_tf_apply_with_tfvars(
    directory: Union[str, Path],
    vars_mapping: Mapping[str, object] | None = None,
    tfvars_path: Union[str, Path] | None = None,
) -> str:
    cleanup_path: str | None = None
    if tfvars_path is not None:
        var_file = str(tfvars_path)
    elif vars_mapping:
        with NamedTemporaryFile("w+", suffix=".auto.tfvars.json", delete=False) as tmp:
            json.dump(vars_mapping, tmp)
            tmp.flush()
            cleanup_path = tmp.name
            var_file = tmp.name
    else:
        raise ValueError("Either vars_mapping or tfvars_path must be provided")

    args = ["terraform", "apply", "-input=false", f"-var-file={var_file}", "-auto-approve=true"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=str(directory),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode:
            raise RuntimeError(
                f"Error running {' '.join(args)}: {stdout.decode().strip()}"
            )
        return stdout.decode()
    finally:
        if cleanup_path and os.path.exists(cleanup_path):
            os.remove(cleanup_path)


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
