#!/usr/bin/env python3

import subprocess
import difflib
import os
import argparse
import sys
import AiDocGenerator
import Filters
from pathlib import Path
from clang.cindex import Index, CursorKind, Config
from typing import Dict, Optional
from collections import defaultdict
from DeclarationInfo import DeclarationInfo, DefinitionInfo


def find_headers(root_dir):
    return list(Path(root_dir).rglob("*.h"))


def find_source_files(root_dir):
    return list(Path(root_dir).rglob("*.c")) + list(Path(root_dir).rglob("*.h"))


def extract_doc(cursor):
    if cursor.raw_comment:
        return cursor.raw_comment
    if cursor.brief_comment:
        return cursor.brief_comment
    else:
        return None


def process_declaration(cursor, lines, filepath):
    doc = extract_doc(cursor)
    line_num = cursor.extent.start.line - 1

    if doc:
        print(f"✅ Docstring found for {cursor.kind.name} '{
              cursor.spelling}' at {filepath}:{line_num + 1}")
        return doc
    else:
        placeholder = f"/**\n * TODO: Document {
            cursor.kind.name.lower()} {cursor.spelling}\n */\n"
        print(f"➕ Inserting docstring for {cursor.kind.name} '{
              cursor.spelling}' at {filepath}:{line_num + 1}")
        lines.insert(line_num, placeholder)
        return None


def parse_header_file(filepath: Path, filter: Filters.DocstringFilter) -> Dict[str, DeclarationInfo]:
    index = Index.create()
    tu = index.parse(str(filepath), args=["-std=c11"])
    declarations = {}

    for cursor in tu.cursor.walk_preorder():
        # Skip declarations from other files (e.g. #includes)
        if not cursor.location.file or Path(cursor.location.file.name) != filepath:
            continue

        # We're interested in these declaration kinds
        if cursor.kind in {
            CursorKind.FUNCTION_DECL,
            CursorKind.STRUCT_DECL,
            CursorKind.UNION_DECL,
            CursorKind.TYPEDEF_DECL,
            CursorKind.ENUM_DECL,
            CursorKind.ENUM_CONSTANT_DECL,
        }:
            name = cursor.spelling
            if not name:  # Skip anonymous structs/enums
                continue

            decl_type = cursor.kind.name.lower()
            docstring = cursor.raw_comment
            is_typedef = cursor.kind == CursorKind.TYPEDEF_DECL

            if len(filter.rules) > 0 and not filter.should_include(name, decl_type):
                continue

            declarations[name] = DeclarationInfo(
                name=name,
                decl_type=decl_type,
                is_typedef=is_typedef,
                file=str(filepath),
                line=cursor.location.line,
                docstring=docstring
            )

    return declarations


def find_definitions(all_decls: Dict[str, DeclarationInfo], root_dir: str):
    files = find_source_files(root_dir)
    index = Index.create()

    for path in files:
        tu = index.parse(str(path), args=["-std=c11"])
        for cursor in tu.cursor.walk_preorder():
            if not cursor.location.file or Path(cursor.location.file.name) != path:
                continue

            name = cursor.spelling
            if name in all_decls and cursor.is_definition():
                decl_info = all_decls[name]
                if decl_info.definition is None:  # Don't overwrite first match
                    decl_info.definition = DefinitionInfo(
                        file=str(path),
                        line=cursor.location.line,
                        is_definition=True,
                        docstring=cursor.raw_comment,
                        start_line=cursor.extent.start.line if cursor.extent else -1,
                        start_column=cursor.extent.start.column if cursor.extent else -1,
                        end_line=cursor.extent.end.line if cursor.extent else -1,
                        end_column=cursor.extent.end.column if cursor.extent else -1,
                    )


def process_folder(folder, filter: Filters.DocstringFilter):
    all_declarations = {}
    for header_path in find_headers(folder):
        print(f"🔍 Processing {header_path}")
        decls = parse_header_file(header_path, filter)
        all_declarations.update(decls)

    find_definitions(all_declarations, folder)
    return all_declarations


def print_stats(decls: Dict[str, DeclarationInfo]):
    type_stats = defaultdict(lambda: {
        "declarations": 0,
        "definitions": 0,
        "documented": 0,
        "undocumented": 0,
    })

    total_decls = 0
    total_defs = 0
    total_docs = 0

    for decl in decls.values():
        t = decl.decl_type
        type_stats[t]["declarations"] += 1
        total_decls += 1

        if decl.definition:
            type_stats[t]["definitions"] += 1
            total_defs += 1

        if decl.docstring:
            type_stats[t]["documented"] += 1
            total_docs += 1
        else:
            type_stats[t]["undocumented"] += 1

    print("\n📊 Declaration Statistics:")
    print("-" * 40)
    for decl_type, stats in type_stats.items():
        print(f"🔹 {decl_type}")
        print(f"   Declarations : {stats['declarations']}")
        print(f"   Definitions  : {stats['definitions']}")
        print(f"   Documented   : {stats['documented']}")
        print(f"   Undocumented : {stats['undocumented']}\n")

    print("🧮 Overall Totals:")
    print(f"   Total Declarations : {total_decls}")
    print(f"   Total Definitions  : {total_defs}")
    print(f"   Documented         : {total_docs}")
    print(f"   Undocumented       : {total_decls - total_docs}")
    print(f"   Missing Definitions: {total_decls - total_defs}")


def generate_dummy_docstring(decl: DeclarationInfo) -> str:
    doc_gen = AiDocGenerator.AiDocGenerator()
    return doc_gen.generateFor(decl)


def insert_docstrings(decls: Dict[str, DeclarationInfo], dry_run=False):
    for decl in decls.values():
        if decl.docstring or not decl.file.endswith(".h"):
            continue  # skip documented or non-header files

        docstring = generate_dummy_docstring(decl)
        file_path = Path(decl.file)
        lines = file_path.read_text().splitlines()

        insert_index = decl.line - 1  # insert above declaration
        if insert_index < 0 or insert_index >= len(lines):
            continue

        print(f"\n📝 Adding docstring to {
              decl.name} in {decl.file}:{decl.line}")
        print(docstring)

        if not dry_run:
            lines.insert(insert_index, docstring)
            file_path.write_text("\n".join(lines))


def generate_patch(file_path: Path, original_lines: list[str], modified_lines: list[str]) -> str:
    return ''.join(
        difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=str(file_path),
            tofile=str(file_path),
            lineterm='\n'
        )
    )


def insert_docstrings_with_patches(decls: Dict[str, DeclarationInfo], output_dir="patches", dry_run=False):
    patch_dir = Path(output_dir)
    patch_dir.mkdir(parents=True, exist_ok=True)

    # Group declarations by file
    decls_by_file = defaultdict(list)
    for decl in decls.values():
        if decl.docstring or not decl.file.endswith((".h", ".c", ".hpp", ".cpp")):
            continue
        decls_by_file[Path(decl.file)].append(decl)

    for file_path, decl_list in decls_by_file.items():
        # Sort by line number (earliest first)
        decl_list.sort(key=lambda d: d.line)

        original_lines = file_path.read_text().splitlines(keepends=True)
        modified_lines = original_lines.copy()
        shift = 0

        for decl in decl_list:
            docstring = generate_dummy_docstring(decl)
            doc_lines = (docstring + "\n").splitlines(keepends=True)
            insert_at = decl.line - 1 + shift

            if 0 <= insert_at <= len(modified_lines):
                modified_lines[insert_at:insert_at] = doc_lines
                shift += len(doc_lines)

        patch = generate_patch(file_path, original_lines, modified_lines)
        if not patch.strip():
            continue

        patch_file = patch_dir / (file_path.name + ".patch")
        print(f"\n📄 Writing patch: {patch_file}")
        if dry_run:
            print(patch)
        else:
            patch_file.write_text(patch)


def apply_patches(patch_dir="patches"):
    patch_dir = Path(patch_dir)
    if not patch_dir.exists():
        print(f"❌ Patch directory {patch_dir} not found.")
        return

    patch_files = list(patch_dir.glob("*.patch"))
    if not patch_files:
        print(f"⚠️ No patch files found in {patch_dir}")
        return

    for patch_file in patch_files:
        print(f"\n📌 Applying patch: {patch_file}")
        try:
            result = subprocess.run(
                ["patch", "-p0", "--forward", "-i", str(patch_file)],
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to apply patch {patch_file.name}")
            print(e.stderr)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze C/C++ headers and source files for declarations and definitions."
    )
    parser.add_argument(
        "path",
        help="Path to the source directory (e.g., ./src)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print summary statistics of declarations and definitions"
    )
    parser.add_argument("--generate-docs", action="store_true",
                        help="Generate and insert missing docstrings")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate docstring insertion without writing changes")

    parser.add_argument(
        "--apply-patches",
        action="store_true",
        help="Apply generated patch files to source"
    )
    parser.add_argument(
        "--patch-dir",
        default="patches",
        help="Directory containing .patch files (default: patches/)"
    )
    parser.add_argument(
        "--include-function-name",
        action="append",
        help="Only include functions with this exact name (can be used multiple times).",
    )
    return parser.parse_args()


def setup_filter_from_args(args) -> Filters.DocstringFilter:
    filt = Filters.DocstringFilter()

    print(f"{args.include_function_name}")
    if args.include_function_name:
        for name in args.include_function_name:
            filt.add_rule(Filters.FilterRule(
                "include", "function_decl", "name", name))

    return filt


def main():
    args = parse_args()
    filter = setup_filter_from_args(args)
    decls = process_folder(args.path, filter)

    if args.stats:
        print_stats(decls)

    if args.generate_docs:
        # insert_docstrings(decls, dry_run=args.dry_run)
        insert_docstrings_with_patches(decls, dry_run=args.dry_run)

    if args.apply_patches:
        apply_patches(args.patch_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
