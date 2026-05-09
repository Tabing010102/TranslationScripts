from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

UNPACKED_DIR_NAME = "1_UnpackedUAsset"
EXPORTED_DIR_NAME = "2_ExportedJson"
MODIFIED_DIR_NAME = "3_ModifiedJson"
REPACKED_DIR_NAME = "4_RepackedUAsset"
OUTPUT_PATCH_DIR_NAME = "5_OutputPatch"
MANUAL_TRANS_FILE_NAME = "ManualTransFile.json"
DEFAULT_RETOC_VERSION = "UE5_3"


def resolve_path(value: str, base_dir: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


@dataclass(frozen=True)
class WorkflowConfig:
    config_path: Path
    tool_root_dir: Path
    retoc_cli_path: Path
    usmap_path: Path
    game_paks_dir: Path
    workspace_dir: Path
    manual_trans_file_path: Path | None
    retoc_version: str
    aes_key: str | None

    @property
    def unpacked_uasset_dir(self) -> Path:
        return self.workspace_dir / UNPACKED_DIR_NAME

    @property
    def exported_json_dir(self) -> Path:
        return self.workspace_dir / EXPORTED_DIR_NAME

    @property
    def modified_json_dir(self) -> Path:
        return self.workspace_dir / MODIFIED_DIR_NAME

    @property
    def repacked_uasset_dir(self) -> Path:
        return self.workspace_dir / REPACKED_DIR_NAME

    @property
    def output_patch_dir(self) -> Path:
        return self.workspace_dir / OUTPUT_PATCH_DIR_NAME

    @property
    def manual_trans_file(self) -> Path:
        return self.manual_trans_file_path or (self.workspace_dir / MANUAL_TRANS_FILE_NAME)

    @classmethod
    def load(cls, config_path: str | Path) -> "WorkflowConfig":
        full_config_path = Path(config_path).resolve()
        payload = json.loads(full_config_path.read_text(encoding="utf-8"))
        base_dir = full_config_path.parent

        required_fields = ("RetocCliPath", "UsmapPath", "GamePaksDir", "WorkspaceDir")
        missing = [field for field in required_fields if not payload.get(field)]
        if missing:
            raise ValueError(f"Missing required config fields: {', '.join(missing)}")

        return cls(
            config_path=full_config_path,
            tool_root_dir=resolve_path(payload.get("ToolRootDir", str(base_dir)), base_dir),
            retoc_cli_path=resolve_path(payload["RetocCliPath"], base_dir),
            usmap_path=resolve_path(payload["UsmapPath"], base_dir),
            game_paks_dir=resolve_path(payload["GamePaksDir"], base_dir),
            workspace_dir=resolve_path(payload["WorkspaceDir"], base_dir),
            manual_trans_file_path=(
                resolve_path(payload["ManualTransFilePath"], base_dir)
                if payload.get("ManualTransFilePath")
                else None
            ),
            retoc_version=payload.get("RetocVersion", DEFAULT_RETOC_VERSION),
            aes_key=payload.get("AesKey"),
        )


def ensure_workspace_structure(config: WorkflowConfig) -> None:
    config.workspace_dir.mkdir(parents=True, exist_ok=True)
    config.unpacked_uasset_dir.mkdir(parents=True, exist_ok=True)
    config.exported_json_dir.mkdir(parents=True, exist_ok=True)
    config.modified_json_dir.mkdir(parents=True, exist_ok=True)
    config.repacked_uasset_dir.mkdir(parents=True, exist_ok=True)
    config.output_patch_dir.mkdir(parents=True, exist_ok=True)

    config.manual_trans_file.parent.mkdir(parents=True, exist_ok=True)

    if not config.manual_trans_file.exists():
        config.manual_trans_file.write_text("{}\n", encoding="utf-8")


def reset_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
