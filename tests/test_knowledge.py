"""Regression tests for the structure/lint boundary and bundle navigation."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from scripts.check_knowledge import check_bundle, frontmatter


CONCEPT = """---
type: Reference
title: Example
description: A small example concept.
tags: [example]
---

# Example
"""
INDEX = '---\nokf_version: "0.2"\n---\n\n# Bundle\n\n- [Example](example.md)\n'


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "bundle"
        self.root.mkdir()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def complete_bundle(self, extra=""):
        self.write("example.md", CONCEPT + extra)
        self.write("index.md", INDEX)

    def test_type_only_is_conformant_without_indexes(self):
        self.write("example.md", "---\ntype: An Unknown Type\n---\n\n# Example\n")
        self.assertTrue(check_bundle(self.root).ok)
        result = check_bundle(self.root, lint=True)
        self.assertFalse(result.ok)
        self.assertFalse(result.errors)
        self.assertTrue(result.lint_errors)

    def test_unknown_fields_and_optional_families_are_allowed(self):
        self.write(
            "example.md",
            """---
type: Custom Type
custom_extension: {anything: [one, two]}
verified: {by: 'process:example', at: '2026-09-17T12:00:00Z'}
---
# Example
""",
        )
        self.assertTrue(check_bundle(self.root).ok)

    def test_yaml_strings_and_timestamps_are_preserved(self):
        metadata, _ = frontmatter("---\ntype: off\nupdated: 2026-09-17\n---\n")
        self.assertEqual(metadata, {"type": "off", "updated": "2026-09-17"})
        self.write("example.md", "---\ntype: off\n---\n# Example\n")
        self.assertTrue(check_bundle(self.root).ok)

    def test_type_must_be_a_nonempty_string(self):
        for value in ('""', '"  "', "null", "123", "false", "[]", "{}"):
            with self.subTest(value=value):
                self.write("example.md", f"---\ntype: {value}\n---\n# Example\n")
                self.assertFalse(check_bundle(self.root).ok)

    def test_missing_type_and_frontmatter_fail(self):
        for text in ("# Example\n", "---\ntitle: Example\n---\n# Example\n"):
            with self.subTest(text=text):
                self.write("example.md", text)
                self.assertFalse(check_bundle(self.root).ok)

    def test_malformed_or_nonmapping_frontmatter_fails(self):
        for text in (
            "---\ntype: [unclosed\n---\n",
            "---\ntype: Reference\n",
            "---\n- item\n---\n",
            "---\nnull\n---\n",
            "---\n---\n",
        ):
            with self.subTest(text=text):
                self.write("example.md", text)
                self.assertFalse(check_bundle(self.root).ok)

    def test_invalid_utf8_is_reported(self):
        (self.root / "example.md").write_bytes(b"\xff\xfe")
        self.assertFalse(check_bundle(self.root).ok)

    def test_root_index_version_is_optional(self):
        self.complete_bundle()
        for text in (INDEX, "# Bundle\n\n- [Example](example.md)\n"):
            with self.subTest(text=text):
                self.write("index.md", text)
                self.assertTrue(check_bundle(self.root).ok)

    def test_unknown_version_is_not_rejected_by_structure_check(self):
        self.complete_bundle()
        self.write("index.md", INDEX.replace('"0.2"', '"99.0"'))
        self.assertTrue(check_bundle(self.root).ok)
        self.assertFalse(check_bundle(self.root, lint=True).ok)

    def test_index_cannot_carry_concept_metadata(self):
        self.write("index.md", CONCEPT)
        self.assertFalse(check_bundle(self.root).ok)
        self.write(
            "index.md",
            INDEX.replace('okf_version: "0.2"', 'okf_version: "0.2"\ntitle: Bundle'),
        )
        self.assertFalse(check_bundle(self.root).ok)

    def test_nested_index_cannot_carry_frontmatter(self):
        self.write("section/index.md", INDEX)
        self.assertFalse(check_bundle(self.root).ok)
        self.write("section/index.md", "# Section\n\n- [Example](example.md)\n")
        self.assertTrue(check_bundle(self.root).ok)

    def test_index_requires_headings(self):
        self.write("index.md", "- [Example](example.md)\n")
        self.assertFalse(check_bundle(self.root).ok)

    def test_uppercase_index_is_a_concept_not_reserved(self):
        self.write("INDEX.md", CONCEPT)
        self.assertTrue(check_bundle(self.root).ok)
        self.assertFalse(check_bundle(self.root, lint=True).ok)
        self.write("INDEX.md", "# Not an OKF index\n")
        self.assertFalse(check_bundle(self.root).ok)

    def test_valid_log(self):
        self.write(
            "log.md",
            "# History\n\n## 2026-09-17\n- Update.\n\n## 2026-09-16\n- Creation.\n",
        )
        self.assertTrue(check_bundle(self.root).ok)

    def test_log_rejects_frontmatter(self):
        self.write(
            "log.md", "---\ntype: Log\n---\n# History\n\n## 2026-09-17\n- Update.\n"
        )
        self.assertFalse(check_bundle(self.root).ok)

    def test_log_requires_valid_dates_in_descending_order(self):
        for content in (
            "## September 17, 2026\n- Update.\n",
            "## 2026-02-30\n- Update.\n",
            "## 2026-9-7\n- Update.\n",
            "## 2026-09-16\n- Creation.\n\n## 2026-09-17\n- Update.\n",
            "## 2026-09-17\nNot a list.\n",
        ):
            with self.subTest(content=content):
                self.write("log.md", "# History\n\n" + content)
                self.assertFalse(check_bundle(self.root).ok)

    def test_log_entries_are_flat_and_belong_to_date_groups(self):
        for text in (
            "# History\n\n- Undated entry.\n\n## 2026-09-17\n- Update.\n",
            "# History\n\n## 2026-09-17\n\n## 2026-09-16\n- Update.\n",
            "# History\n\n## 2026-09-17\n- Update.\n  - Nested entry.\n",
            "# History\n\n## 2026-09-17\n- Update.\n\nUngrouped prose.\n",
        ):
            with self.subTest(text=text):
                self.write("log.md", text)
                self.assertFalse(check_bundle(self.root).ok)

    def test_log_ignores_example_headings_inside_list_entry_code(self):
        self.write(
            "log.md",
            "# History\n\n## 2026-09-17\n- Example:\n\n  ```md\n  ## Not a date\n  ```\n",
        )
        self.assertTrue(check_bundle(self.root).ok)

    def test_complete_bundle_passes_lint(self):
        self.complete_bundle()
        result = check_bundle(self.root, lint=True)
        self.assertTrue(result.ok, result)
        self.assertEqual(
            (result.files, result.concepts, result.indexes, result.logs), (2, 1, 1, 0)
        )

    def test_lint_checks_recommended_metadata(self):
        for replacement in ("title: null", "description: 7", "tags: [1]", "tags: []"):
            with self.subTest(replacement=replacement):
                self.complete_bundle()
                key = replacement.split(":")[0]
                lines = [
                    replacement if line.startswith(key + ":") else line
                    for line in CONCEPT.splitlines()
                ]
                self.write("example.md", "\n".join(lines))
                result = check_bundle(self.root, lint=True)
                self.assertFalse(result.ok)
                self.assertFalse(result.errors)

    def test_lint_rejects_legacy_relations_but_not_other_extensions(self):
        self.complete_bundle()
        self.write(
            "example.md",
            CONCEPT.replace("type: Reference", "type: Reference\ncustom: [one]"),
        )
        self.assertTrue(check_bundle(self.root, lint=True).ok)
        self.write(
            "example.md",
            CONCEPT.replace(
                "type: Reference", "type: Reference\nrelates_to: [example]"
            ),
        )
        self.assertTrue(check_bundle(self.root).ok)
        self.assertFalse(check_bundle(self.root, lint=True).ok)

    def test_broken_links_are_only_lint_errors(self):
        self.complete_bundle("\n[Unwritten](missing.md)\n")
        self.assertTrue(check_bundle(self.root).ok)
        result = check_bundle(self.root, lint=True)
        self.assertFalse(result.ok)
        self.assertFalse(result.errors)
        self.assertIn("broken local link", "\n".join(result.lint_errors))

    def test_root_relative_reference_and_directory_links(self):
        self.complete_bundle(
            '\n[Root](/section/other.md#heading)\n[Ref][other]\n\n[other]: section/other.md "Title"\n'
        )
        self.write("section/other.md", CONCEPT + "\n[Parent](../example.md)\n")
        self.write("section/index.md", "# Section\n\n- [Other](other.md)\n")
        self.write("index.md", INDEX + "- [Section](section/)\n")
        self.assertTrue(check_bundle(self.root, lint=True).ok)

    def test_code_and_external_links_do_not_trigger_lint(self):
        self.complete_bundle("""
`[Not a link](missing.md)`

```markdown
[Example](unwritten.md)
## Not a log heading
```

    [Also code](not-real.md)

[Web](https://example.invalid/missing)
[Mail](mailto:example@example.invalid)
[Network](//example.invalid/missing)
[Anchor](#example)
""")
        self.assertTrue(check_bundle(self.root, lint=True).ok)

    def test_images_and_encoded_paths_are_checked(self):
        self.complete_bundle(
            '\n![Image](image.png)\n[Encoded](with%20spaces.md)\n[Parentheses](with(paren).md "Title")\n'
        )
        self.write("image.png", "placeholder asset")
        self.write("with spaces.md", CONCEPT)
        self.write("with(paren).md", CONCEPT)
        self.write(
            "index.md",
            INDEX + "- [Spaces](with%20spaces.md)\n- [Parens](with(paren).md)\n",
        )
        self.assertTrue(check_bundle(self.root, lint=True).ok)
        (self.root / "image.png").unlink()
        self.assertFalse(check_bundle(self.root, lint=True).ok)

    def test_links_cannot_escape_bundle_under_lint(self):
        for href in ("../outside.md", "%2e%2e/outside.md", "/../outside.md"):
            with self.subTest(href=href):
                self.complete_bundle(f"\n[Outside]({href})\n")
                self.assertTrue(check_bundle(self.root).ok)
                self.assertIn(
                    "escapes the bundle",
                    "\n".join(check_bundle(self.root, lint=True).lint_errors),
                )

    def test_indexes_list_contexts_logs_and_child_sections(self):
        self.complete_bundle()
        self.write("CONTEXT.md", CONCEPT)
        self.write("log.md", "# History\n\n## 2026-09-17\n- Creation.\n")
        self.write("nested/deep/example.md", CONCEPT)
        result = check_bundle(self.root, lint=True)
        self.assertFalse(result.ok)
        messages = "\n".join(result.lint_errors)
        for expected in (
            "CONTEXT.md",
            "log.md",
            "nested/index.md",
            "nested/deep/index.md",
        ):
            self.assertIn(expected, messages)
        self.assertTrue(check_bundle(self.root).ok)

    def test_missing_and_empty_bundle_fail(self):
        self.assertFalse(check_bundle(self.root / "absent").ok)
        self.assertFalse(check_bundle(self.root).ok)

    def test_cli_exit_codes(self):
        self.complete_bundle()
        script = Path(__file__).resolve().parents[1] / "scripts/check_knowledge.py"
        command = [sys.executable, str(script), str(self.root), "--lint"]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.write("example.md", "# Missing metadata\n")
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)


if __name__ == "__main__":
    unittest.main()
