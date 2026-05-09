from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from workflow_config import WorkflowConfig, ensure_workspace_structure, reset_directory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the UE5 Zen localization workflow.")
    parser.add_argument("mode", choices=("prepare", "build"))
    parser.add_argument("config", nargs="?", default="config.json", help="Path to config.json")
    return parser.parse_args()


def validate_prepare_inputs(config: WorkflowConfig) -> None:
    if not config.retoc_cli_path.is_file():
        raise FileNotFoundError(f"retoc executable not found: {config.retoc_cli_path}")
    if not config.usmap_path.is_file():
        raise FileNotFoundError(f".usmap file not found: {config.usmap_path}")
    if not config.game_paks_dir.is_dir():
        raise NotADirectoryError(f"GamePaksDir not found: {config.game_paks_dir}")


def validate_build_inputs(config: WorkflowConfig) -> None:
    validate_prepare_inputs(config)
    if not config.exported_json_dir.is_dir():
        raise FileNotFoundError(f"Exported JSON directory not found: {config.exported_json_dir}")
    if not any(config.exported_json_dir.rglob("*.json")):
        raise FileNotFoundError(f"No exported JSON files found under: {config.exported_json_dir}")
    if not config.manual_trans_file.is_file():
        raise FileNotFoundError(f"Translation dictionary not found: {config.manual_trans_file}")


def build_retoc_command(config: WorkflowConfig, subcommand: str, *args: str) -> list[str]:
    command = [str(config.retoc_cli_path)]
    if config.aes_key:
        command.extend(["--aes-key", config.aes_key])
    command.append(subcommand)
    command.extend(args)
    return command


def run_command(command: list[str], cwd: Path) -> None:
    printable = subprocess.list2cmdline(command)
    print(f"> {printable}")
    subprocess.run(command, cwd=cwd, check=True)


def batch_uasset_packer_project(config: WorkflowConfig) -> Path:
    return config.tool_root_dir / "BatchUAssetPacker" / "BatchUAssetPacker.csproj"


def localize_tool_script(config: WorkflowConfig) -> Path:
    return config.tool_root_dir / "localize_tool.py"


def run_batch_uasset_packer(config: WorkflowConfig, mode: str) -> None:
    run_command(
        [
            "dotnet",
            "run",
            "--project",
            str(batch_uasset_packer_project(config)),
            "--",
            mode,
            str(config.config_path),
        ],
        cwd=config.tool_root_dir,
    )


def run_localize_tool(config: WorkflowConfig, mode: str) -> None:
    run_command(
        [
            sys.executable,
            str(localize_tool_script(config)),
            mode,
            str(config.config_path),
        ],
        cwd=config.tool_root_dir,
    )


def infer_patch_name(config: WorkflowConfig) -> str:
    paks_dir = config.game_paks_dir
    if paks_dir.name.lower() == "paks" and paks_dir.parent.name.lower() == "content" and paks_dir.parent.parent.name:
        game_name = paks_dir.parent.parent.name
    else:
        game_name = paks_dir.parent.name or "Game"
    return f"{game_name}-Windows_P.utoc"


def copy_scriptobjects_if_present(config: WorkflowConfig) -> None:
    source = config.unpacked_uasset_dir / "scriptobjects.bin"
    if not source.is_file():
        return

    destination = config.repacked_uasset_dir / "scriptobjects.bin"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    print(f"Copied scriptobjects.bin to {destination}")


def run_prepare(config: WorkflowConfig) -> int:
    validate_prepare_inputs(config)
    ensure_workspace_structure(config)

    reset_directory(config.unpacked_uasset_dir)
    reset_directory(config.exported_json_dir)
    reset_directory(config.modified_json_dir)
    reset_directory(config.repacked_uasset_dir)
    reset_directory(config.output_patch_dir)

    run_command(
        build_retoc_command(
            config,
            "to-legacy",
            "--version",
            config.retoc_version,
            str(config.game_paks_dir),
            str(config.unpacked_uasset_dir),
        ),
        cwd=config.tool_root_dir,
    )
    run_batch_uasset_packer(config, "extract")
    run_localize_tool(config, "extract")

    print("Prepare phase complete.")
    print(f"Translate this file before running build: {config.manual_trans_file}")
    return 0


def run_build(config: WorkflowConfig) -> int:
    validate_build_inputs(config)
    ensure_workspace_structure(config)

    reset_directory(config.modified_json_dir)
    reset_directory(config.repacked_uasset_dir)
    reset_directory(config.output_patch_dir)

    run_localize_tool(config, "inject")

    modified_json_files = sorted(config.modified_json_dir.rglob("*.json"))
    if not modified_json_files:
        raise RuntimeError("No translated JSON files were generated. Fill ManualTransFile.json with actual translated text before running build.")

    run_batch_uasset_packer(config, "pack")
    copy_scriptobjects_if_present(config)

    output_utoc = config.output_patch_dir / infer_patch_name(config)
    run_command(
        build_retoc_command(
            config,
            "to-zen",
            "--version",
            config.retoc_version,
            str(config.repacked_uasset_dir),
            str(output_utoc),
        ),
        cwd=config.tool_root_dir,
    )

    print("Build phase complete.")
    print(f"Patch output: {output_utoc}")
    return 0


def main() -> int:
    args = parse_args()
    config = WorkflowConfig.load(args.config)

    if args.mode == "prepare":
        return run_prepare(config)
    return run_build(config)


if __name__ == "__main__":
    raise SystemExit(main())
