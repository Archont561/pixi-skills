"""Check OKF v0.2 structure, with opt-in repository authoring lint.

The default checks follow SPEC sections 4, 8, 9, and 11. Missing optional
metadata/indexes and broken links are NOT conformance errors. --lint adds
this repository's stricter metadata, navigation, and local-link policy.
This is not a fact checker or an attestation/optional-family validator.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
import yaml


RESERVED = {"index.md", "log.md"}
MARKDOWN = MarkdownIt("commonmark")


class FrontmatterLoader(yaml.SafeLoader):
    """Keep authored timestamps as strings and avoid YAML 1.1 yes/no booleans."""


FrontmatterLoader.yaml_implicit_resolvers = {
    key: [
        (tag, pattern)
        for tag, pattern in resolvers
        if tag not in {"tag:yaml.org,2002:timestamp", "tag:yaml.org,2002:bool"}
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
FrontmatterLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"),
    list("tTfF"),
)


@dataclass
class Result:
    files: int = 0
    concepts: int = 0
    indexes: int = 0
    logs: int = 0
    errors: list[str] = field(default_factory=list)
    lint_errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.errors or self.lint_errors)


def frontmatter(text: str) -> tuple[dict | None, str]:
    """Read only the leading --- block; never interpret examples as metadata."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return None, text
    for end in range(1, len(lines)):
        if lines[end].rstrip("\r\n") == "---":
            value = yaml.load("".join(lines[1:end]), Loader=FrontmatterLoader)
            if not isinstance(value, dict):
                raise ValueError("frontmatter must be a YAML mapping")
            return value, "".join(lines[end + 1 :])
    raise ValueError("frontmatter has no closing --- delimiter")


def headings(tokens: list) -> list[str]:
    return [
        tokens[i + 1].content
        for i, token in enumerate(tokens)
        if token.type == "heading_open"
    ]


def links(tokens: list) -> list[str]:
    # CommonMark handles reference-style links, titles, escaped parentheses,
    # inline code, and fenced/indented code blocks without regex false positives.
    return [
        child.attrGet("href" if child.type == "link_open" else "src")
        for token in tokens
        for child in token.children or []
        if child.type in {"link_open", "image"}
    ]


def local_target(root: Path, source: Path, href: str) -> Path | None:
    url = urlsplit(href)
    if url.scheme or url.netloc:
        return None
    path = unquote(url.path)
    if not path:
        return source
    target = (
        root / path.lstrip("/") if path.startswith("/") else source.parent / path
    ).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"link escapes the bundle: {href}")
    if target.is_dir() and (target / "index.md").is_file():
        target = target / "index.md"
    return target


def check_log(tokens: list) -> list[str]:
    problems = []
    dates = []
    entry_counts = []
    seen_heading = False
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.level == 0:
            title = tokens[i + 1].content
            is_date = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", title))
            # An optional document title may precede the date groups.
            if not seen_heading and not is_date:
                seen_heading = True
                continue
            seen_heading = True
            entry_counts.append(0)
            try:
                if not is_date:
                    raise ValueError
                dates.append(date.fromisoformat(title))
            except ValueError:
                problems.append(f"log date heading must be a valid YYYY-MM-DD: {title}")
        elif token.type == "list_item_open":
            if token.level != 1:
                problems.append("log entries must be a flat list")
            elif not entry_counts:
                problems.append("log entries must follow a date heading")
            else:
                entry_counts[-1] += 1
        elif token.level == 0 and token.type in {
            "paragraph_open",
            "fence",
            "code_block",
            "blockquote_open",
            "html_block",
            "hr",
        }:
            problems.append("log prose must be inside a date-grouped list entry")
    if not dates:
        problems.append("log must contain date-grouped entries")
    if dates != sorted(dates, reverse=True):
        problems.append("log dates must be newest first")
    if not entry_counts or any(count == 0 for count in entry_counts):
        problems.append("each log date group must contain list entries")
    return problems


def check_bundle(bundle: Path, *, lint: bool = False) -> Result:
    result = Result()
    root = bundle.resolve()
    if not root.is_dir():
        result.errors.append(f"{bundle}: bundle directory does not exist")
        return result
    paths = sorted(root.rglob("*.md"))
    result.files = len(paths)
    if not paths:
        result.errors.append(f"{bundle}: no Markdown documents found")
        return result
    targets: dict[Path, set[Path]] = {}

    for path in paths:
        label = path.relative_to(root).as_posix()
        if path.name == "index.md":
            result.indexes += 1
        elif path.name == "log.md":
            result.logs += 1
        else:
            result.concepts += 1
        if not path.resolve().is_relative_to(root):
            result.errors.append(f"{label}: document resolves outside the bundle")
            continue
        try:
            metadata, body = frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
            result.errors.append(f"{label}: {exc}")
            continue
        tokens = MARKDOWN.parse(body)
        if path.name == "index.md":
            if metadata is not None and (
                path.parent != root or set(metadata) != {"okf_version"}
            ):
                result.errors.append(
                    f"{label}: index frontmatter is forbidden except for root okf_version"
                )
            if not headings(tokens):
                result.errors.append(
                    f"{label}: index must group entries under headings"
                )
        elif path.name == "log.md":
            if metadata is not None:
                result.errors.append(f"{label}: log must not contain frontmatter")
            result.errors.extend(f"{label}: {problem}" for problem in check_log(tokens))
        elif metadata is None:
            result.errors.append(f"{label}: concept is missing YAML frontmatter")
        elif not isinstance(metadata.get("type"), str) or not metadata["type"].strip():
            result.errors.append(f"{label}: concept needs a non-empty string type")

        if not lint:
            continue
        if path.name.lower() in RESERVED and path.name not in RESERVED:
            result.lint_errors.append(f"{label}: use the lowercase reserved filename")
        if path.name not in RESERVED and metadata is not None:
            for key in ("title", "description"):
                value = metadata.get(key)
                if not isinstance(value, str) or not value.strip():
                    result.lint_errors.append(f"{label}: add a non-empty {key}")
            if (
                isinstance(metadata.get("description"), str)
                and "\n" in metadata["description"].strip()
            ):
                result.lint_errors.append(f"{label}: description must be a single line")
            tags = metadata.get("tags")
            if (
                not isinstance(tags, list)
                or not tags
                or any(not isinstance(tag, str) or not tag.strip() for tag in tags)
            ):
                result.lint_errors.append(
                    f"{label}: tags must be a non-empty list of strings"
                )
            if "relates_to" in metadata:
                result.lint_errors.append(
                    f"{label}: replace relates_to with Markdown links"
                )
        if path == root / "index.md" and metadata != {"okf_version": "0.2"}:
            result.lint_errors.append(f'{label}: declare okf_version: "0.2"')
        targets[path] = set()
        for href in links(tokens):
            try:
                target = local_target(root, path, href)
            except ValueError as exc:
                result.lint_errors.append(f"{label}: {exc}")
                continue
            if target is not None:
                targets[path].add(target)
                if not target.exists():
                    result.lint_errors.append(f"{label}: broken local link: {href}")

    if lint:
        directories = {root}
        for path in paths:
            directories.update(
                parent for parent in path.parents if parent.is_relative_to(root)
            )
        for directory in sorted(directories):
            index = directory / "index.md"
            label = index.relative_to(root).as_posix()
            if not index.is_file():
                result.lint_errors.append(f"{label}: add an index for this directory")
                continue
            expected = {p for p in paths if p.parent == directory and p != index}
            expected.update(
                d / "index.md" for d in directories if d.parent == directory
            )
            for missing in sorted(expected - targets.get(index, set())):
                result.lint_errors.append(
                    f"{label}: index does not list {missing.relative_to(root).as_posix()}"
                )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", nargs="?", type=Path, default=Path(".knowledge"))
    parser.add_argument(
        "--lint", action="store_true", help="enforce repository authoring policy too"
    )
    args = parser.parse_args()
    result = check_bundle(args.bundle, lint=args.lint)
    print(
        f"Checked {result.files} Markdown files: {result.concepts} concepts, "
        f"{result.indexes} indexes, {result.logs} log{'s' if result.logs != 1 else ''}."
    )
    for error in result.errors:
        print(f"ERROR [structure] {error}")
    for error in result.lint_errors:
        print(f"ERROR [lint] {error}")
    if result.ok:
        print(
            "OKF v0.2 structure checks passed."
            + (" Repository lint passed." if args.lint else "")
        )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
