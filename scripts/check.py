#!/usr/bin/env python3
"""Validate the generated codelab pages in docs/.

Checks every docs/*.html file for these things (rules: CLAUDE.md and
session-guidelines.md in this repository):

  1. Emoji characters anywhere in the file (forbidden by CLAUDE.md).
  2. Anchor links (href="#...") whose target id does not exist in the same
     file — i.e. a sidebar/step link pointing nowhere.
  3. A placeholder "..." inside a <code> element, which means the code sample
     is incomplete instead of the full, copy-paste-ready snippet CLAUDE.md
     requires. Allowed: spread/rest syntax ("...rest", "...(a)", "[...xs]",
     "{...props}") and a word directly followed by "..." at the end of a line
     or before a quote or "<" (comments and literal text like 'Chargement...').
  4. Patterns that do not run in Expo Go (rn-conventions.md, sections 2 and
     13) inside a <pre><code> block: react-native-mmkv, @react-native-firebase,
     expo prebuild, getExpoPushTokenAsync, mqtt:// .
  5. Session pages only (docs/session-*.html): the quiz CSS rules and the
     quiz script are byte-identical to templates/codelab-template.html.
  6. Quiz questions: unique id, a data-answer matching exactly one of its
     data-option values, three options, one .quiz-feedback with
     aria-live="polite", one non-empty .quiz-explain, no display utility
     class on the feedback/explain paragraphs, and at least one
     [data-quiz-score] in a page that has questions.
  7. Guided steps (panels whose data-title starts with "Étape"): cards
     Objectif, Commandes, Code complet, À retenir, plus either "Résultat
     attendu" and "Vérification", or the merged "Résultat et vérification".
  8. Step titles written "Etape" without the accent (data-title or any
     element text), which would bypass check 7.
  9. docs/session-01.html to docs/session-07.html: the sidebar has the
     sections data-nav-section="cours" then "atelier", and one panel's
     data-title starts with "Défi". session-00.html (homework) is exempt.

No third-party dependencies: only the Python 3 standard library is used.

Exit code: 0 if every file passes, 1 if any file has a problem.
"""

import glob
import os
import re
import sys
from html.parser import HTMLParser

# Patterns that need a development build or a raw TCP socket, so they never
# run in Expo Go (rn-conventions.md, sections 2 and 13). Checked in
# <pre><code> blocks only: S7 may name them in prose as theory.
FORBIDDEN_CODE_PATTERNS = [
    "react-native-mmkv",
    "@react-native-firebase",
    "expo prebuild",
    "getExpoPushTokenAsync",
    "mqtt://",
]

# Emoji ranges called out in CLAUDE.md: misc symbols/pictographs + emoticons
# (U+1F300-U+1FAFF) and the older "misc symbols" / dingbats block
# (U+2600-U+27BF) that also carries common emoji such as checkmarks, stars,
# and weather symbols.
EMOJI_PATTERN = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

# A step title without the accent ("Etape 1 - ...") escapes check 7.
UNACCENTED_STEP_PATTERN = re.compile(r'(data-title="|>)\s*Etape\b')

# Session pages that must have the Cours/Atelier split and a Défi panel.
STRUCTURED_SESSION_PATTERN = re.compile(r"^session-0[1-7]\.html$")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
TEMPLATE_PATH = os.path.join(REPO_ROOT, "templates", "codelab-template.html")

# Tailwind display utilities that would override the hidden attribute.
DISPLAY_CLASSES = {"block", "inline", "inline-block", "flex", "inline-flex",
                   "grid", "inline-grid", "table", "contents", "flow-root"}

GUIDED_CARDS = ["Objectif", "Commandes", "Code complet", "À retenir"]
MERGED_RESULT_CARD = "Résultat et vérification"
SPLIT_RESULT_CARDS = ["Résultat attendu", "Vérification"]


def quiz_skeleton(template_text):
    """Return (css, script): the quiz parts of the template skeleton."""
    css_start = template_text.index("  /* Quiz */")
    css = template_text[css_start:template_text.index("</style>", css_start)]
    js_start = template_text.index("<!-- Quiz JavaScript")
    js_end = template_text.index("</script>", js_start) + len("</script>")
    return css, template_text[js_start:js_end]


# "..." followed by an identifier, "(", "[" or "{" is spread/rest syntax.
SPREAD_FOLLOWER = re.compile(r"[A-Za-z_$(\[{]")
# A word directly before "..." that ends the line, a string or a JSX text:
# a comment such as "// Loading data..." or UI text such as 'Chargement...'.
TEXT_FOLLOWER = re.compile(r"""\s*$|['"`<]""")


def is_allowed_ellipsis(code_line):
    """True when every '...' in the line is spread syntax or literal text.

    CLAUDE.md (Code blocks): code is complete, never truncated with "...",
    but spread syntax is code, and text that ends with "..." (comments, UI
    strings) is reproduced literally.
    A bare placeholder such as '// ...', '{ ... }' or 'foo(...)' is flagged.
    """
    start = 0
    while True:
        i = code_line.find("...", start)
        if i == -1:
            return True
        after = code_line[i + 3:]
        before = code_line[:i]
        is_spread = bool(after) and SPREAD_FOLLOWER.match(after) is not None
        # A letter (accented letters included) directly before the "...".
        is_text = (re.search(r"[^\W\d_]$", before) is not None
                   and TEXT_FOLLOWER.match(after) is not None)
        if not (is_spread or is_text):
            return False
        start = i + 3


class PageChecker(HTMLParser):
    """Collects ids, internal '#...' links, and <code> block text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.hash_links = []  # list of (target_id, line_number)
        self._code_depth = 0
        self._code_line_stack = []
        self._code_text_stack = []
        self._code_in_pre_stack = []
        self._pre_depth = 0
        self.code_issues = []  # list of (line_number, snippet)
        self.forbidden_issues = []  # list of (line_number, pattern)

    def _register_common(self, tag, attrs):
        attrs_dict = dict(attrs)
        el_id = attrs_dict.get("id")
        if el_id:
            self.ids.add(el_id)
        if tag == "a":
            href = attrs_dict.get("href", "")
            if href.startswith("#") and len(href) > 1:
                self.hash_links.append((href[1:], self.getpos()[0]))
        if tag == "pre":
            self._pre_depth += 1
        if tag == "code":
            self._code_depth += 1
            self._code_line_stack.append(self.getpos()[0])
            self._code_text_stack.append([])
            self._code_in_pre_stack.append(self._pre_depth > 0)

    def handle_starttag(self, tag, attrs):
        self._register_common(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        # Self-closing tag: still may carry an id/href, never opens <code>.
        attrs_dict = dict(attrs)
        el_id = attrs_dict.get("id")
        if el_id:
            self.ids.add(el_id)
        if tag == "a":
            href = attrs_dict.get("href", "")
            if href.startswith("#") and len(href) > 1:
                self.hash_links.append((href[1:], self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag == "pre" and self._pre_depth > 0:
            self._pre_depth -= 1
        if tag == "code" and self._code_depth > 0:
            self._code_depth -= 1
            line = self._code_line_stack.pop()
            text = "".join(self._code_text_stack.pop())
            in_pre = self._code_in_pre_stack.pop()
            for offset, code_line in enumerate(text.split("\n")):
                if "..." in code_line and not is_allowed_ellipsis(code_line):
                    snippet = " ".join(code_line.strip().split())[:80]
                    self.code_issues.append((line + offset, snippet))
                if in_pre:
                    for pattern in FORBIDDEN_CODE_PATTERNS:
                        if pattern in code_line:
                            self.forbidden_issues.append((line + offset, pattern))

    def handle_data(self, data):
        if self._code_depth > 0:
            self._code_text_stack[-1].append(data)


class QuizCardChecker(HTMLParser):
    """Collects quiz questions, score spans and guided-step card titles."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.questions = []
        self.score_count = 0
        self.steps = []  # [data-title, [h3 titles], line]
        self.nav_sections = []  # data-nav-section values, in page order
        self._div_depth = 0
        self._question = None
        self._question_depth = None
        self._explain = None  # text chunks while inside a .quiz-explain
        self._h3 = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if "data-quiz-score" in a:
            self.score_count += 1
        if a.get("data-nav-section"):
            self.nav_sections.append(a["data-nav-section"])
        if tag == "section" and "step-panel" in classes:
            self.steps.append([a.get("data-title", ""), [], self.getpos()[0]])
        if tag == "h3" and self.steps:
            self._h3 = []
        if tag == "div":
            self._div_depth += 1
            if "quiz-question" in classes:
                self._question = {
                    "id": a.get("id"), "answer": a.get("data-answer"),
                    "line": self.getpos()[0], "options": [],
                    "feedback": [], "explain": [], "display": [],
                }
                self._question_depth = self._div_depth
                self.questions.append(self._question)
        q = self._question
        if q is None:
            return
        if "quiz-option" in classes:
            q["options"].append(a.get("data-option"))
        for kind in ("quiz-feedback", "quiz-explain"):
            if kind in classes:
                bad = DISPLAY_CLASSES.intersection(classes)
                if bad:
                    q["display"].append("%s has %s" % (kind, ", ".join(sorted(bad))))
        if "quiz-feedback" in classes:
            q["feedback"].append(a.get("aria-live"))
        if "quiz-explain" in classes:
            self._explain = []

    def handle_endtag(self, tag):
        if tag == "h3" and self._h3 is not None:
            self.steps[-1][1].append(" ".join("".join(self._h3).split()))
            self._h3 = None
        if tag == "p" and self._explain is not None:
            self._question["explain"].append("".join(self._explain).strip())
            self._explain = None
        if tag == "div":
            if self._question is not None and self._div_depth == self._question_depth:
                self._question = None
                self._question_depth = None
            self._div_depth -= 1

    def handle_data(self, data):
        if self._h3 is not None:
            self._h3.append(data)
        if self._explain is not None:
            self._explain.append(data)


def check_quiz_and_cards(path, content, template_text):
    problems = []
    name = os.path.basename(path)

    # 5. Quiz skeleton identical to the template (session pages only).
    if name.startswith("session-") and template_text is not None:
        css, script = quiz_skeleton(template_text)
        if css not in content:
            problems.append("quiz CSS differs from templates/codelab-template.html")
        if script not in content:
            problems.append("quiz script differs from templates/codelab-template.html")

    parser = QuizCardChecker()
    parser.feed(content)
    parser.close()

    # 6. Quiz questions.
    seen = {}
    for q in parser.questions:
        where = "line %d: quiz question %s" % (q["line"], q["id"] or "(no id)")
        if not q["id"]:
            problems.append(where + " has no id")
        elif q["id"] in seen:
            problems.append(where + " duplicates the id of line %d" % seen[q["id"]])
        else:
            seen[q["id"]] = q["line"]
        if len(q["options"]) != 3:
            problems.append(where + " has %d options instead of 3" % len(q["options"]))
        if len(set(q["options"])) != len(q["options"]):
            problems.append(where + " repeats a data-option value")
        if q["options"].count(q["answer"]) != 1:
            problems.append(where + ' data-answer="%s" matches no single data-option' % q["answer"])
        if q["feedback"] != ["polite"]:
            problems.append(where + ' needs exactly one .quiz-feedback with aria-live="polite"')
        if len(q["explain"]) != 1 or not q["explain"][0]:
            problems.append(where + " needs exactly one non-empty .quiz-explain")
        for d in q["display"]:
            problems.append(where + ": " + d + " (defeats the hidden attribute)")
    if parser.questions and parser.score_count == 0:
        problems.append("page has quiz questions but no [data-quiz-score]")

    # 7. Required cards in guided steps.
    for title, cards, line in parser.steps:
        if not title.startswith("Étape"):
            continue
        def has(card):
            # A title may carry a duration badge after it ("Objectif 20 min").
            return any(t == card or t.startswith(card + " ") for t in cards)

        missing = [c for c in GUIDED_CARDS if not has(c)]
        if not has(MERGED_RESULT_CARD):
            missing += [c for c in SPLIT_RESULT_CARDS if not has(c)]
        if missing:
            problems.append('line %d: step "%s" is missing card(s): %s'
                            % (line, title, ", ".join(missing)))

    # 9. Cours/Atelier split and Défi panel (sessions 01-07; 00 is homework).
    if STRUCTURED_SESSION_PATTERN.match(name):
        sections = parser.nav_sections
        if "cours" not in sections or "atelier" not in sections:
            problems.append('sidebar needs data-nav-section="cours" and "atelier" '
                            '(found: %s)' % (", ".join(sections) or "none"))
        elif sections.index("cours") > sections.index("atelier"):
            problems.append('sidebar section "cours" must come before "atelier"')
        if not any(title.startswith("Défi") for title, _, _ in parser.steps):
            problems.append('no step panel with a data-title starting with "Défi"')
    return problems


def check_file(path, template_text=None):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    problems = []

    # 1. Emoji scan, line by line for a useful line number.
    for lineno, line in enumerate(content.splitlines(), start=1):
        for match in EMOJI_PATTERN.finditer(line):
            ch = match.group()
            problems.append(
                "line %d: forbidden emoji character %r (U+%04X)"
                % (lineno, ch, ord(ch))
            )

    # 8. Step titles without the accent, line by line.
    for lineno, line in enumerate(content.splitlines(), start=1):
        if UNACCENTED_STEP_PATTERN.search(line):
            problems.append(
                'line %d: step title starts with "Etape" instead of "Étape"' % lineno
            )

    # 2 & 3. Parse the markup for ids, internal links, and code blocks.
    parser = PageChecker()
    try:
        parser.feed(content)
        parser.close()
    except Exception as exc:  # malformed markup should not crash the check
        problems.append("HTML parse error: %s" % exc)
        return problems

    for target, lineno in parser.hash_links:
        if target not in parser.ids:
            problems.append(
                'line %d: link to "#%s" has no matching id="%s" in this file'
                % (lineno, target, target)
            )

    for lineno, snippet in parser.code_issues:
        problems.append(
            'line %d: incomplete code block contains "...": %r' % (lineno, snippet)
        )

    # 4. Patterns that do not run in Expo Go.
    for lineno, pattern in parser.forbidden_issues:
        problems.append(
            'line %d: code block uses "%s", which does not run in Expo Go'
            % (lineno, pattern)
        )

    # 5, 6, 7 & 9. Quiz skeleton, quiz questions and guided-step cards.
    problems.extend(check_quiz_and_cards(path, content, template_text))

    return problems


def main():
    files = sorted(glob.glob(os.path.join(DOCS_DIR, "*.html")))

    print("Codelab site check")
    print("=" * 60)

    if not files:
        print("No HTML files found in docs/ - nothing to check.")
        print("=" * 60)
        print("RESULT: PASS (nothing to check)")
        return 0

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_text = f.read()

    all_ok = True
    for path in files:
        rel = os.path.relpath(path, REPO_ROOT)
        problems = check_file(path, template_text)
        if problems:
            all_ok = False
            print("[FAIL] %s (%d issue(s))" % (rel, len(problems)))
            for p in problems:
                print("    - %s" % p)
        else:
            print("[PASS] %s" % rel)

    print("=" * 60)
    if all_ok:
        print("RESULT: PASS - all files clean")
        return 0
    else:
        print("RESULT: FAIL - fix the issues above")
        return 1


SELF_TEST_CASES = [
    # (code line, expected is_allowed_ellipsis result)
    ("// Load the products from the cache...", True),
    ("// Étape suivante détaillée en séance 05 : à créer...", True),
    ("const next = { ...prev, done: true }; // copy...", True),
    ("const { token, headers, ...rest } = options;", True),
    ("...(token ? { Authorization: `Bearer ${token}` } : {}),", True),
    ("const all = [...a, ...b];", True),
    ("<Text>Chargement...</Text>", True),
    ("{isLoading ? 'Chargement...' : null}", True),
    ("// ...", False),
    ("# ...", False),
    ("// TODO ...", False),
    ("* ...", False),
    ("...", False),
    ("const x = { ... };", False),
    ("return api(...);", False),
    ("const all = [...a, ...];", False),
]


def self_test():
    failures = 0
    for line, expected in SELF_TEST_CASES:
        got = is_allowed_ellipsis(line)
        if got != expected:
            failures += 1
            print("FAIL: %r -> %s (expected %s)" % (line, got, expected))
    total = len(SELF_TEST_CASES)
    print("Self-test: %d/%d passed" % (total - failures, total))
    return 1 if failures else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        sys.exit(self_test())
    sys.exit(main())
