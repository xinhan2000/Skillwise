"""Skillwise 8-point security lint.

Static, regex-level checks over every text file in a skill package.
Cheap and imperfect on purpose — production adds sandboxed dynamic testing.

Levels:
  fail — blocks publication
  warn — publishes, but displayed on the listing and in pre-install summaries
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

BINARY_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".pkl", ".pickle", ".pyc",
    ".class", ".jar", ".wasm", ".o", ".a",
}

# (check_id, level, compiled_pattern, human_reason)
_PATTERNS: list[tuple[str, str, re.Pattern, str]] = [
    # 1. Dangerous shell patterns
    ("dangerous_shell", "fail", re.compile(r"\brm\s+-[rf]{2}\b"), "recursive force delete (rm -rf)"),
    ("dangerous_shell", "fail", re.compile(r"(curl|wget)[^\n|]*\|\s*(ba|z|da)?sh\b"), "piping downloaded content into a shell"),
    ("dangerous_shell", "warn", re.compile(r"\bsudo\b"), "requests elevated privileges (sudo)"),
    ("dangerous_shell", "warn", re.compile(r"\bchmod\s+\+x\b"), "marks files executable (chmod +x)"),
    # 2. Network access
    ("network", "warn", re.compile(r"\b(import\s+requests|import\s+httpx|import\s+urllib|from\s+urllib|import\s+socket)\b"), "Python network library"),
    ("network", "warn", re.compile(r"\bfetch\s*\(\s*['\"]https?://"), "JavaScript fetch call"),
    ("network", "warn", re.compile(r"\b(curl|wget)\s+https?://"), "shell network call"),
    # 3. Secret / credential harvesting
    ("secret_harvest", "fail", re.compile(r"(~|\$HOME|os\.path\.expanduser)[^\n]{0,40}(\.aws|\.ssh|id_rsa|id_ed25519)"), "reads SSH/AWS credential paths"),
    ("secret_harvest", "warn", re.compile(r"\bos\.environ\b(?!\s*(\.get)?\s*[\[(]\s*['\"](SKILLWISE|PATH|HOME|LANG))"), "reads environment variables"),
    ("secret_harvest", "warn", re.compile(r"\bdotenv|\.env\b"), "reads .env files"),
    # 4. Hardcoded secrets
    ("hardcoded_secret", "fail", re.compile(r"\b(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{10,})\b"), "API key/token pattern found"),
    ("hardcoded_secret", "fail", re.compile(r"(api[_-]?key|secret|password)\s*[:=]\s*['\"][A-Za-z0-9+/_-]{16,}['\"]", re.IGNORECASE), "hardcoded credential assignment"),
    # 5. Obfuscation
    ("obfuscation", "fail", re.compile(r"[A-Za-z0-9+/]{200,}={0,2}"), "large base64-like blob"),
    ("obfuscation", "fail", re.compile(r"\b(exec|eval)\s*\(\s*(b?['\"]|base64|bytes\.fromhex|compile\()"), "executes decoded/constructed strings"),
    # 6. Prompt injection
    ("prompt_injection", "fail", re.compile(r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+instructions", re.IGNORECASE), "instruction-override attempt"),
    ("prompt_injection", "fail", re.compile(r"(do\s+not|don't|never)\s+(tell|show|reveal|mention)[^\n]{0,30}(the\s+)?user", re.IGNORECASE), "conceal-from-user instruction"),
    ("prompt_injection", "fail", re.compile(r"(send|post|include|append)[^\n]{0,60}(conversation|chat\s+history|context)[^\n]{0,60}https?://", re.IGNORECASE), "conversation exfiltration attempt"),
    # 7. Filesystem escape
    ("fs_escape", "warn", re.compile(r"\.\./\.\."), "path traversal (../..)"),
    ("fs_escape", "fail", re.compile(r"(>>?|open\(|write[^\n]{0,20})[^\n]{0,20}(~/\.(bashrc|zshrc|profile|bash_profile)|/etc/)"), "writes to shell rc files or /etc"),
    # 8. Executable payloads — handled by extension/null-byte check below
]

_SHELL_HINT = re.compile(r"\b(subprocess|os\.system|os\.popen|sh\s+-c|bash\s+-c)\b")
_WRITE_HINT = re.compile(r"(open\([^\n]*['\"][wax]b?['\"]|write_text|write_bytes|shutil\.copy|json\.dump\()")


@dataclass
class Finding:
    check: str
    level: str  # "fail" | "warn"
    file: str
    line: int
    evidence: str
    reason: str


@dataclass
class ScanReport:
    status: str = "pass"  # pass | warn | fail
    points_checked: int = 8
    findings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "points_checked": self.points_checked,
            "findings": [asdict(f) for f in self.findings],
        }


def _iter_files(package_dir: Path):
    for p in sorted(package_dir.rglob("*")):
        if p.is_file() and "_meta" not in p.parts:
            yield p


def scan_package(package_dir: Path) -> tuple[ScanReport, dict]:
    """Run the 8-point lint. Returns (report, derived_capabilities)."""
    report = ScanReport()
    caps = {"network": False, "shell": False, "file_write": False}

    for path in _iter_files(package_dir):
        rel = str(path.relative_to(package_dir))

        # Check 8: executable/binary payloads
        if path.suffix.lower() in BINARY_EXTENSIONS:
            report.findings.append(Finding(
                "binary_payload", "fail", rel, 0, path.suffix, "binary/executable file in package"))
            continue
        raw = path.read_bytes()
        if b"\x00" in raw[:8192]:
            report.findings.append(Finding(
                "binary_payload", "fail", rel, 0, "<null bytes>", "binary content in package"))
            continue

        text = raw.decode("utf-8", errors="replace")
        lines = text.splitlines()

        for check, level, pattern, reason in _PATTERNS:
            for m in pattern.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                snippet = lines[line_no - 1].strip()[:120] if line_no <= len(lines) else ""
                report.findings.append(Finding(check, level, rel, line_no, snippet, reason))

        if _PATTERNS and any(f.check == "network" and f.file == rel for f in report.findings):
            caps["network"] = True
        if _SHELL_HINT.search(text) or path.suffix in {".sh", ".bash"}:
            caps["shell"] = True
        if _WRITE_HINT.search(text):
            caps["file_write"] = True

    if any(f.level == "fail" for f in report.findings):
        report.status = "fail"
    elif report.findings:
        report.status = "warn"
    return report, caps
