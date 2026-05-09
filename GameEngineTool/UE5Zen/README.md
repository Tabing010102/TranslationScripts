# ZenLocalizationWorkflow

# :warning: Code under this folder was all vibe coded

UE5 Zen/IoStore localization workflow for `TsunSis`, implemented from the finalized `implementation_plan.md`.

This workflow has been validated end-to-end with:
- `prepare` run from a standalone production directory that only stores `config.json` and `workspace/`
- `build` run with an external translated dictionary path via `ManualTransFilePath`
- successful patch output as `TsunSis-Windows_P.pak`, `TsunSis-Windows_P.ucas`, and `TsunSis-Windows_P.utoc`

## Files

- `config.json`: central configuration file.
- `config.external.example.json`: validated external config/workspace layout example.
- `BatchUAssetPacker/`: C# console app for `extract` and `pack`.
- `localize_tool.py`: extracts and injects `CultureInvariantString` translations.
- `run_pipeline.py`: orchestrates `retoc`, the C# packer, and the localization tool.
- `workspace/`: isolated generated files.

## Config fields

- `ToolRootDir`: path to the `ZenLocalizationWorkflow` code directory. Optional when `config.json` lives inside the code folder. Required when `config.json` lives outside the code folder.
- `RetocCliPath`: path to `retoc.exe`.
- `UsmapPath`: path to the game's `.usmap` file.
- `GamePaksDir`: path to the game's `Content/Paks` directory.
- `WorkspaceDir`: isolated working directory for unpacked assets, exported JSON, repacked assets, and patch output.
- `ManualTransFilePath`: optional path to a translated dictionary file. If omitted or `null`, the workflow uses `<WorkspaceDir>/ManualTransFile.json`.
- `RetocVersion`: Unreal version string passed to `retoc`. For `TsunSis`, use `UE5_3`.
- `AesKey`: optional AES key for encrypted IoStore containers.

## Config modes

### In-place config

Put `config.json` inside `ZenLocalizationWorkflow/`. In that layout, `ToolRootDir` can point to the same folder or be omitted entirely.

### External production config

Put `config.json` in a separate directory that only contains configuration and generated files, then point `ToolRootDir` back to `ZenLocalizationWorkflow/`.

This external layout is the currently validated setup.

Validated directory shape:

```text
/path/to/Output/Exports/
  ZenLocalizationWorkflow/
  retoc_cli/
  TsunSis260503Prod/
    config.json
    workspace/
```

Validated external example:

```json
{
  "ToolRootDir": "/path/to/Output/Exports/ZenLocalizationWorkflow",
  "RetocCliPath": "/path/to/Output/Exports/retoc_cli/retoc.exe",
  "UsmapPath": "/path/to/TsunSis-5.3.2-29314046+++UE5+Release-5.3-0196ef29.usmap",
  "GamePaksDir": "/path/to/TsunSis/TsunSis/Content/Paks",
  "WorkspaceDir": "/path/to/Output/Exports/TsunSis260503Prod/workspace",
  "ManualTransFilePath": "/path/to/Output/Exports/TsunSis260503Prod/workspace/ManualTransFile_YYYYMMDD_HHMMSS_translated_YYYYMMDD_HHMMSS/ManualTransFile.json",
  "RetocVersion": "UE5_3",
  "AesKey": null
}
```

## Usage

1. Fill in either `config.json` or your own external config file.
2. Run `prepare` to unpack assets, export JSON, and generate a translation dictionary.
3. Translate `ManualTransFile.json`, or point `ManualTransFilePath` at an external translated copy.
4. Run `build` to inject translations, repack assets, and generate the final patch.

## Commands

Prepare exported JSONs and generate or update the translation dictionary:

```powershell
py -3 /path/to/ZenLocalizationWorkflow/run_pipeline.py prepare /path/to/config.json
```

Build the patch after translation:

```powershell
py -3 /path/to/ZenLocalizationWorkflow/run_pipeline.py build /path/to/config.json
```

When `ManualTransFilePath` is unset or `null`, the default dictionary path is:

```text
<WorkspaceDir>/ManualTransFile.json
```

When `ManualTransFilePath` is set, `build` uses that external translated file instead.

Validated output path example:

```text
/path/to/Output/Exports/TsunSis260503Prod/workspace/5_OutputPatch/TsunSis-Windows_P.utoc
```

Direct component commands:

```powershell
dotnet run --project /path/to/ZenLocalizationWorkflow/BatchUAssetPacker/BatchUAssetPacker.csproj -- extract /path/to/config.json
dotnet run --project /path/to/ZenLocalizationWorkflow/BatchUAssetPacker/BatchUAssetPacker.csproj -- pack /path/to/config.json
py -3 /path/to/ZenLocalizationWorkflow/localize_tool.py extract /path/to/config.json
py -3 /path/to/ZenLocalizationWorkflow/localize_tool.py inject /path/to/config.json
```
