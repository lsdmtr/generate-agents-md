#!/usr/bin/env python3
"""Validate AGENTS.md-style instruction files with profile-aware checks.

This is a deterministic smoke test. It catches missing guidance and obvious
ticket-specific wording, but it does not replace human review of project facts.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class Check:
    name: str
    needles: tuple[str, ...]
    help: str


CHECKS: dict[str, Check] = {
    "project purpose": Check(
        "project purpose",
        ("项目说明", "project purpose", "project overview", "project description"),
        "project identity, audience, owned runtime/business surface",
    ),
    "work boundaries": Check(
        "work boundaries",
        ("工作边界", "work boundaries", "scope", "boundaries", "ownership"),
        "editable scope, read-only references, sibling/external boundaries",
    ),
    "development order": Check(
        "development order",
        ("每轮开发顺序", "development order", "development workflow", "workflow", "开发流程"),
        "per-task order from requirements through verification",
    ),
    "requirements entry": Check(
        "requirements entry",
        ("需求入口", "requirements entry", "requirements", "spec entry", "需求文档", "specification"),
        "where requirements/specs live and what to do when missing",
    ),
    "design document rules": Check(
        "design document rules",
        ("设计文档规范", "design document", "design doc", "design.md", "architecture decision", "adr"),
        "design docs, ADRs, plans, or decision records for behavior changes",
    ),
    "interface document rules": Check(
        "interface document rules",
        ("接口文档规范", "interface document", "api document", "interface.md", "contract", "public api"),
        "public API, UI, CLI, schema, config, telemetry, or command contracts",
    ),
    "directory responsibilities": Check(
        "directory responsibilities",
        ("目录和职责", "directory", "module responsibilities", "source layout", "模块职责"),
        "where new code/docs/tests belong",
    ),
    "development standards": Check(
        "development standards",
        ("开发规范", "development standards", "coding standards", "implementation standards"),
        "stack-specific coding and architecture rules",
    ),
    "import/export standards": Check(
        "import/export standards",
        ("import 和 export", "import/export", "import and export", "public surface", "exports"),
        "language-specific imports, exports, package surface, or equivalent public surface",
    ),
    "external boundaries": Check(
        "external boundaries",
        ("外部能力", "external dependency", "external dependencies", "sdk", "service boundary", "vendor"),
        "SDK, service, generated client, platform, infra, or legacy boundaries",
    ),
    "documentation and comments": Check(
        "documentation and comments",
        ("文档和注释", "documentation", "comments", "jsdoc", "docstring", "注释规范"),
        "comments/docs expectations with structured examples",
    ),
    "testing and verification": Check(
        "testing and verification",
        ("测试和验证", "testing", "verification", "test plan", "build", "lint"),
        "install/lint/test/build/manual proof commands",
    ),
    "git and delivery": Check(
        "git and delivery",
        ("git", "交付", "delivery", "pull request", "commit"),
        "status checks, preserving user changes, final proof reporting",
    ),
    "good example": Check(
        "good example",
        ("合格示例", "good example", "valid example", "acceptable example"),
        "at least one concrete example of acceptable guidance",
    ),
    "bad example": Check(
        "bad example",
        ("不合格示例", "bad example", "invalid example", "unacceptable example"),
        "at least one concrete counterexample",
    ),
    "sdk public surface": Check(
        "sdk public surface",
        ("public exports", "package surface", "公开导出", "公开 api", "semantic version", "adapter"),
        "library/SDK package exports, adapters, examples, and contract tests",
    ),
    "app workflow": Check(
        "app workflow",
        ("user flow", "screen", "route", "component", "ui state", "用户流程", "页面", "组件"),
        "app screens, flows, UI states, platform checks, assets, and accessibility",
    ),
    "backend contract": Check(
        "backend contract",
        ("endpoint", "handler", "schema", "migration", "database", "status code", "接口", "数据库"),
        "API endpoints, schemas, migrations, jobs, and observability",
    ),
    "cli contract": Check(
        "cli contract",
        ("cli", "command", "flag", "stdin", "stdout", "stderr", "exit code", "命令行"),
        "commands, flags, stdio, exit codes, config, and shell portability",
    ),
    "data reproducibility": Check(
        "data reproducibility",
        ("reproducibility", "deterministic", "dataset", "notebook", "input", "output", "可复现"),
        "inputs, outputs, schemas, seeds, artifacts, and deterministic reruns",
    ),
    "infra safety": Check(
        "infra safety",
        ("terraform", "kubernetes", "plan", "apply", "state", "secret", "rollback", "基础设施"),
        "IaC state, secrets, plan/apply, environment targeting, and rollback",
    ),
}


COMMON_CHECKS: tuple[str, ...] = (
    "project purpose",
    "work boundaries",
    "development order",
    "requirements entry",
    "directory responsibilities",
    "development standards",
    "documentation and comments",
    "testing and verification",
    "git and delivery",
    "good example",
    "bad example",
)


PROFILES: dict[str, tuple[str, ...]] = {
    "full": COMMON_CHECKS
    + (
        "design document rules",
        "interface document rules",
        "import/export standards",
        "external boundaries",
    ),
    "sdk": COMMON_CHECKS
    + (
        "design document rules",
        "interface document rules",
        "import/export standards",
        "external boundaries",
        "sdk public surface",
    ),
    "app": COMMON_CHECKS
    + (
        "design document rules",
        "interface document rules",
        "external boundaries",
        "app workflow",
    ),
    "backend": COMMON_CHECKS
    + (
        "design document rules",
        "interface document rules",
        "external boundaries",
        "backend contract",
    ),
    "cli": COMMON_CHECKS + ("cli contract",),
    "data": COMMON_CHECKS + ("data reproducibility",),
    "infra": COMMON_CHECKS + ("infra safety",),
    "light": (
        "project purpose",
        "work boundaries",
        "development order",
        "directory responsibilities",
        "development standards",
        "documentation and comments",
        "testing and verification",
        "git and delivery",
        "good example",
        "bad example",
    ),
}


DEFAULT_MIN_UNITS: dict[str, int] = {
    "full": 700,
    "sdk": 700,
    "app": 600,
    "backend": 600,
    "cli": 420,
    "data": 420,
    "infra": 420,
    "light": 150,
}


TRANSIENT_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\b(this|current)\s+(ticket|issue|sprint|milestone|branch)\b", "current ticket/issue/sprint/branch wording"),
    (r"\bone[- ]off\s+(ticket|change|migration|plan|rollout)\b", "one-off work described as policy"),
    (r"\btemporary\s+(migration|rollout|bridge|plan|workaround)\b", "temporary plan described as policy"),
    (
        r"本次[^。\n]{0,40}(\d+\.\d+|v\d|#[0-9]+|[A-Z]+-[0-9]+|专(?:项))[^。\n]{0,40}(需求|开发|迭代|改造)[^。\n]{0,40}(为准|只|临时|口径)",
        "Chinese one-off version/issue requirement wording",
    ),
    (
        r"本次[^。\n]{0,30}(需求|开发|迭代|改造)[^。\n]{0,30}以\s*`[^`]+`\s*为准",
        "Chinese one-off requirement path treated as project policy",
    ),
    (r"当前[^。\n]{0,30}(分支|迭代|sprint|ticket|issue)[^。\n]{0,40}(为准|范围|临时)", "Chinese current branch/sprint wording"),
)


PLACEHOLDER_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"<path/to/[^>]+>", "unresolved path placeholder"),
    (r"\bTODO\b(?![:：]?\s*(禁止|forbid|avoid|不要|不得))", "unresolved TODO placeholder"),
    (r"\bTBD\b", "unresolved TBD placeholder"),
    (r"\byour project\b", "generic 'your project' placeholder"),
    (r"\bproject name\b", "generic 'project name' placeholder"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an AGENTS.md or equivalent project instruction file.",
    )
    parser.add_argument("path", nargs="?", help="Path to AGENTS.md or equivalent instruction file.")
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        default="full",
        help="Validation profile. Use light/cli/data/infra for smaller or non-API repos.",
    )
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        help="Additional required literal substring. May be repeated.",
    )
    parser.add_argument(
        "--require-regex",
        action="append",
        default=[],
        help="Additional required regular expression. May be repeated.",
    )
    parser.add_argument(
        "--forbid",
        action="append",
        default=[],
        help="Forbidden literal substring. May be repeated.",
    )
    parser.add_argument(
        "--forbid-regex",
        action="append",
        default=[],
        help="Forbidden regular expression. May be repeated.",
    )
    parser.add_argument(
        "--forbid-transient",
        action="store_true",
        help="Fail on common ticket/sprint/version/temporary-plan wording.",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Allow TODO/TBD/path placeholders. Off by default.",
    )
    parser.add_argument(
        "--allow-missing",
        action="append",
        default=[],
        help="Check name to allow missing, for intentionally smaller repos. May be repeated.",
    )
    parser.add_argument(
        "--alias",
        action="append",
        default=[],
        metavar="CHECK=PHRASE",
        help="Add a language-specific phrase for a check, e.g. --alias 'project purpose=Descripcion'.",
    )
    parser.add_argument(
        "--min-units",
        type=int,
        default=None,
        help="Override profile minimum content units. Use 0 to disable.",
    )
    parser.add_argument(
        "--list-checks",
        action="store_true",
        help="Print available check names and exit.",
    )
    return parser.parse_args()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def count_content_units(text: str) -> int:
    # Count Latin-like tokens and individual CJK characters so Chinese files are
    # not treated as tiny documents by whitespace-based word counts.
    return len(re.findall(r"[A-Za-z0-9_./:@#-]+|[\u3400-\u9fff]", text))


def parse_aliases(alias_args: list[str]) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = {}
    for raw in alias_args:
        if "=" not in raw:
            raise ValueError(f"invalid --alias value {raw!r}; expected CHECK=PHRASE")
        check_name, phrase = raw.split("=", 1)
        check_name = check_name.strip().lower()
        phrase = phrase.strip()
        if check_name not in CHECKS:
            raise ValueError(f"unknown check in --alias: {check_name}")
        if not phrase:
            raise ValueError(f"empty alias phrase for check: {check_name}")
        aliases.setdefault(check_name, []).append(phrase)
    return aliases


def compile_user_regex(pattern: str) -> re.Pattern[str]:
    try:
        return re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    except re.error as exc:
        raise ValueError(f"invalid regex {pattern!r}: {exc}") from exc


def has_any(normalized: str, check: Check, aliases: dict[str, list[str]]) -> bool:
    needles = list(check.needles) + aliases.get(check.name, [])
    return any(needle.lower() in normalized for needle in needles)


def main() -> int:
    args = parse_args()

    if args.list_checks:
        for name in sorted(CHECKS):
            print(f"{name}: {CHECKS[name].help}")
        return 0

    if not args.path:
        print("[ERROR] path is required unless --list-checks is used", file=sys.stderr)
        return 2

    try:
        aliases = parse_aliases(args.alias)
        require_regexes = [compile_user_regex(pattern) for pattern in args.require_regex]
        forbid_regexes = [compile_user_regex(pattern) for pattern in args.forbid_regex]
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    path = Path(args.path)
    if not path.is_file():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        return 2

    content = path.read_text(encoding="utf-8")
    normalized = normalize(content)
    failures: list[str] = []
    warnings: list[str] = []
    allowed_missing = {item.lower() for item in args.allow_missing}

    for check_name in PROFILES[args.profile]:
        if check_name.lower() in allowed_missing:
            continue
        check = CHECKS[check_name]
        if not has_any(normalized, check, aliases):
            expected = ", ".join(check.needles)
            failures.append(f"missing {check_name}: expected one of {expected}")

    for required in args.require:
        if required.lower() not in normalized:
            failures.append(f"missing required text: {required}")

    for regex in require_regexes:
        if not regex.search(content):
            failures.append(f"missing required regex: {regex.pattern}")

    for forbidden in args.forbid:
        if forbidden.lower() in normalized:
            failures.append(f"forbidden text present: {forbidden}")

    for regex in forbid_regexes:
        if regex.search(content):
            failures.append(f"forbidden regex matched: {regex.pattern}")

    if args.forbid_transient:
        for pattern, label in TRANSIENT_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                failures.append(f"transient wording present: {label} ({pattern})")

    if not args.allow_placeholders:
        for pattern, label in PLACEHOLDER_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                failures.append(f"placeholder present: {label} ({pattern})")

    min_units = DEFAULT_MIN_UNITS[args.profile] if args.min_units is None else args.min_units
    if min_units > 0:
        units = count_content_units(content)
        if units < min_units:
            failures.append(
                f"content is too shallow for profile {args.profile}: {units} units < {min_units}",
            )

    headings = re.findall(r"(?m)^\s{0,3}#{1,6}\s+\S+", content)
    if len(headings) < 5 and args.profile != "light":
        warnings.append("few markdown headings found; verify the file is structured enough for future agents")

    code_fences = len(re.findall(r"```", content))
    if code_fences < 2 and args.profile not in {"light", "infra"}:
        warnings.append("few fenced examples found; verify good/bad examples are concrete")

    if failures:
        print(f"[FAIL] {path} failed AGENTS.md validation for profile {args.profile}:")
        for failure in failures:
            print(f"- {failure}")
        if warnings:
            print("[WARN]")
            for warning in warnings:
                print(f"- {warning}")
        return 1

    print(f"[OK] {path} passed AGENTS.md validation for profile {args.profile}.")
    if warnings:
        print("[WARN]")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
