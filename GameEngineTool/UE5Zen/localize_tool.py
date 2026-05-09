from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from workflow_config import WorkflowConfig, ensure_workspace_structure

JAPANESE_TEXT_PATTERN = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\uff66-\uff9f\u3400-\u4dbf\u4e00-\u9fff々〆ヶ]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract or inject CultureInvariantString translations.")
    parser.add_argument("mode", choices=("extract", "inject"))
    parser.add_argument("config", help="Path to config.json")
    return parser.parse_args()


def is_target_text_node(node: object) -> bool:
    if not isinstance(node, dict):
        return False

    culture_invariant_string = node.get("CultureInvariantString")
    if not isinstance(culture_invariant_string, str):
        return False

    node_type = str(node.get("$type", ""))
    return "TextPropertyData" in node_type


def iter_text_nodes(root: object):
    stack = [root]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if is_target_text_node(current):
                yield current
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)


def contains_japanese_text(value: str) -> bool:
    return bool(value.strip()) and bool(JAPANESE_TEXT_PATTERN.search(value))


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_translation_dict(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Translation file must contain a JSON object: {path}")

    result: dict[str, str] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            continue
        result[key] = value if isinstance(value, str) else ""
    return result


def extract_strings(config: WorkflowConfig) -> int:
    ensure_workspace_structure(config)

    translation_map = load_translation_dict(config.manual_trans_file)
    json_paths = sorted(config.exported_json_dir.rglob("*.json"))
    if not json_paths:
        raise FileNotFoundError(f"No exported JSON files found under '{config.exported_json_dir}'.")

    new_entries = 0
    scanned_nodes = 0

    for json_path in json_paths:
        payload = load_json(json_path)
        for node in iter_text_nodes(payload):
            scanned_nodes += 1
            source_text = node["CultureInvariantString"]
            if not contains_japanese_text(source_text):
                continue
            if source_text not in translation_map:
                translation_map[source_text] = source_text
                new_entries += 1

    sorted_map = dict(sorted(translation_map.items(), key=lambda item: item[0]))
    write_json(config.manual_trans_file, sorted_map)
    print(f"Scanned {len(json_paths)} JSON file(s), {scanned_nodes} text node(s), added {new_entries} new translation entries.")
    print(f"Translation dictionary updated: {config.manual_trans_file}")
    return 0


def inject_strings(config: WorkflowConfig) -> int:
    ensure_workspace_structure(config)

    translation_map = load_translation_dict(config.manual_trans_file)
    json_paths = sorted(config.exported_json_dir.rglob("*.json"))
    if not json_paths:
        raise FileNotFoundError(f"No exported JSON files found under '{config.exported_json_dir}'.")

    modified_files = 0
    total_replacements = 0

    for json_path in json_paths:
        payload = load_json(json_path)
        replacements_in_file = 0

        for node in iter_text_nodes(payload):
            source_text = node["CultureInvariantString"]
            translated_text = translation_map.get(source_text)
            if not translated_text or translated_text == source_text:
                continue

            node["CultureInvariantString"] = translated_text
            replacements_in_file += 1

        if replacements_in_file == 0:
            continue

        relative_path = json_path.relative_to(config.exported_json_dir)
        output_path = config.modified_json_dir / relative_path
        write_json(output_path, payload)
        modified_files += 1
        total_replacements += replacements_in_file

    print(f"Injected {total_replacements} translated string(s) into {modified_files} JSON file(s).")
    print(f"Modified JSON output: {config.modified_json_dir}")
    return 0


def main() -> int:
    args = parse_args()
    config = WorkflowConfig.load(args.config)

    if args.mode == "extract":
        return extract_strings(config)
    return inject_strings(config)


if __name__ == "__main__":
    raise SystemExit(main())
