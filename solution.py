"""Code-review Claude Skill solution: loads a real community SKILL.md
(sitting next to this script) and applies it to review the one file shown
in each case's question.txt, via a direct Anthropic API call.

Note: the skill's own referenced companion files (per-language reference
guides, bundled scripts) are not available in this environment -- the model
is instructed to apply the skill's own inline guidance instead. This is a
known, documented scope limitation of the eval, not a bug.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-4-6")
HERE = Path(__file__).resolve().parent
SKILL_MD = (HERE / "SKILL.md").read_text()

SYSTEM = f"""You must act EXACTLY as Claude would when the following Claude \
Skill is loaded and active. This is a real Skill file (SKILL.md format). \
Internalize its review methodology, principles, and process, and apply it \
faithfully when reviewing the code the user shows you.

Note: this skill may reference additional companion files (per-language \
reference guides, bundled scripts) on demand -- those files are NOT \
available in this environment. Apply the skill's own inline guidance and \
general code-review judgment wherever it would normally consult a \
referenced file.

=== BEGIN SKILL.md ===
{SKILL_MD}
=== END SKILL.md ===

Now apply this skill's review process to the code the user shows you. The \
user's message is itself the full task specification, including the exact \
required JSON output format -- follow it exactly. That JSON schema takes \
precedence over any output template described in the skill above, since \
it's the actual task contract you're being graded against."""


def main() -> int:
    manifest = json.loads(os.environ["TRAP_MANIFEST"])
    inputs_dir = Path(manifest["inputs_dir"])
    question = (inputs_dir / "question.txt").read_text()

    client = Anthropic(max_retries=10)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    answer = next((b.text for b in msg.content if b.type == "text"), "").strip()
    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
