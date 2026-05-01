\# hebrew-date-converter — Week 5 Reusable Skill



\*\*Author:\*\* Elan Burman

\*\*Course:\*\* Generative AI (BU.330.760), Johns Hopkins Carey Business School

\*\*Video walkthrough:\*\* \[(https://youtu.be/yDkXvoTF4HA)]



\## TL;DR for the grader



This skill performs four operations on the Hebrew (Jewish) calendar: date conversion, omer-day counting, weekly Torah portion lookup, and yahrzeit (death anniversary) calculation. The Hebrew calendar is lunisolar with leap months and conditional rules — exactly the kind of multi-step rule-based arithmetic that LLMs reproduce unreliably. A deterministic Python library called `pyluach` handles the math correctly. The script is genuinely load-bearing: without it, the agent gets dates wrong. With it, the agent orchestrates and formats while the script computes.



\## What the Hebrew calendar is and why it's hard for LLMs



The Hebrew calendar is the calendar used in Judaism for religious observance. Unlike the Gregorian calendar (which is purely solar), the Hebrew calendar is \*\*lunisolar\*\*: months follow the moon (29 or 30 days each) but the year is periodically corrected to stay aligned with the solar year. The corrections are non-trivial:



\- \*\*Leap years\*\* add an entire extra month (called Adar II) in 7 of every 19 years on a fixed cycle.

\- \*\*Month lengths vary\*\*: two months (Cheshvan and Kislev) can each be either 29 or 30 days depending on rules tied to which day of the week Rosh Hashanah (the Hebrew new year) falls on. So the same Hebrew "date" — say, "30 Cheshvan" — exists in some years and not in others.

\- \*\*The year starts twice\*\*: religiously the year begins in Nisan (around March/April), but the year \*number\* increments in Tishrei (around September/October). So Hebrew year 5786 contains parts of Gregorian 2025 and 2026.



LLMs trained on text reproduce some of this correctly some of the time, but they hallucinate confidently when the rules interact. I have personally watched both ChatGPT and Claude miscount day-of-omer numbers and assign the wrong weekly Torah portion to known dates. The `pyluach` Python library, by contrast, implements the calendar arithmetic deterministically (it's based on a formal algorithm published by Dr. Irv Bromberg of the University of Toronto), so its answers are reproducible and verifiable.



\## What this skill does



Four operations, each backed by a Python subcommand:



1\. \*\*Convert\*\* — translates a Gregorian date (e.g., April 30, 2026) to a Hebrew date (e.g., 13 Iyar 5786) or vice versa.

2\. \*\*Omer\*\* — \*Sefirat Ha'omer\* ("counting the omer") is a Jewish ritual of counting 49 consecutive days from the second night of Passover to the holiday of Shavuot. Day 1 is 16 Nisan; day 49 is 5 Sivan. The skill returns which day-of-the-omer (1 through 49) corresponds to a given Gregorian date, or notes that the date is outside the counting period.

3\. \*\*Parsha\*\* — the Torah is divided into 54 weekly portions called \*parshiot\*. One is read publicly each Sabbath (\*Shabbos\*). Given a date, the skill returns the parsha for the Sabbath of that week. Diaspora and Israel schedules diverge a few weeks per year because of differences in how the Passover holiday is observed.

4\. \*\*Yahrzeit\*\* — a \*yahrzeit\* is the anniversary of a death, observed annually on the Hebrew date the death occurred. The skill takes a Hebrew date of death and returns the Gregorian dates for upcoming yahrzeit anniversaries — useful because the family needs to know which Gregorian date to attend synagogue, light a memorial candle, etc.



\## Why the script is genuinely load-bearing (the rubric question)



The Week 5 rubric specifically asks: \*"choose a task where the script is genuinely load-bearing, not decorative."\* Three concrete things the script does that an LLM cannot reliably do alone:



\*\*1. Detect when a Hebrew date does not exist in a given year.\*\*

Cheshvan can be 29 or 30 days depending on the year. If someone died on 30 Cheshvan 5780, then in years where Cheshvan only has 29 days, that date \*literally does not exist\*. An LLM asked to "compute the next 5 yahrzeits" will typically just generate 5 plausible-looking dates without realizing the input date is undefined in some of those years. The script catches this case via `pyluach`'s `replace()` method, which raises a `ValueError` for non-existent dates, and returns a structured `halachic\_warning` flagging the case for rabbinic consultation rather than guessing.



\*\*2. Compute day-of-omer correctly.\*\*

The omer count starts on 16 Nisan and runs 49 days. Computing day-N requires knowing the precise number of days between two Hebrew dates, which depends on month-length rules. LLMs frequently miscount by 1–7 days. The script computes this via deterministic Hebrew-to-Gregorian conversion of both anchor and target, then a date subtraction.



\*\*3. Look up the weekly Torah portion authoritatively.\*\*

The annual cycle of 54 parshiot maps to \~52 Sabbaths, with some weeks combined and some split depending on whether the year is a leap year and where holidays fall. The mapping is fixed by halakha (Jewish religious law) but its computation has multiple branches. `pyluach.parshios.getparsha\_string()` implements the canonical algorithm.



In all three cases, the model orchestrates (parses the user's request, asks clarifying questions if dates are ambiguous, formats the JSON output as readable prose, surfaces warnings) — but the script does the math.



\## How to use the skill



The skill activates automatically when running Claude Code from a project containing `.agents/skills/hebrew-date-converter/` or `.claude/skills/hebrew-date-converter/`. Example prompts:



\- "What's today's Hebrew date?"

\- "What day of the omer is May 12, 2026?"

\- "What's the parsha for the week of April 18, 2026?"

\- "My grandfather died on 15 Tishrei 5780. When are his next 5 yahrzeit dates?"



The agent recognizes the skill is relevant, invokes the script, and returns a prose answer.



You can also run the script directly:



&#x20;   pip install pyluach

&#x20;   python .agents/skills/hebrew-date-converter/scripts/hebrew\_date\_tool.py convert --date 2026-04-30 --to hebrew



\## Repository structure



&#x20;   hw6-elan/

&#x20;   +-- .agents/skills/hebrew-date-converter/    (assignment-required location)

&#x20;   |   +-- SKILL.md

&#x20;   |   +-- scripts/

&#x20;   |       +-- hebrew\_date\_tool.py

&#x20;   +-- .claude/skills/hebrew-date-converter/    (location Claude Code reads from)

&#x20;   |   +-- SKILL.md

&#x20;   |   +-- scripts/

&#x20;   |       +-- hebrew\_date\_tool.py

&#x20;   +-- README.md

&#x20;   +-- .gitignore



The skill is duplicated in both `.agents/` (the path the assignment specifies) and `.claude/` (the path the Claude Code agent actually loads skills from). Both copies are identical.



\## What worked well



\- The skill activated correctly on every test prompt — the agent recognized references to "Hebrew date," "omer," "parsha," and "yahrzeit" without needing explicit invocation.

\- Returning JSON from the script and letting the agent format the prose kept the script clean and the output flexible.

\- The `halachic\_warning` field is a high-value scope-respecting pattern: when the script detects a date that has religious-legal ambiguity (e.g., 30 Cheshvan in a short year), it flags the case rather than silently picking an answer. The agent then surfaces the warning and refers the user to a rabbi. This is a clean way to express the boundary between deterministic computation and judgment that requires a human authority.



\## Test cases used



I tested three prompts in Claude Code:



1\. \*\*Normal case\*\*: "What's today's Hebrew date and the parsha for this coming Shabbos?" — agent activated the skill, ran the script for both `convert` and `parsha` subcommands, returned: today is 13 Iyar 5786, this Shabbos is parsha Emor.



2\. \*\*Edge case\*\*: "My great-grandmother died on 30 Cheshvan 5780. When are her next 5 yahrzeits in Gregorian dates?" — script returned 5 dates plus a halachic warning that 30 Cheshvan does not exist in some upcoming Hebrew years and rabbinic consultation is required for those. The agent surfaced the warning prominently.



3\. \*\*Cautious / partial-decline case\*\*: "Can you write me a dvar Torah on this week's parsha?" (a \*dvar Torah\* is an interpretive Torah talk) — the agent correctly identified that the SKILL.md explicitly excludes interpretive content, said so up front, and offered general-knowledge content with a clear caveat that it was not coming from the skill.



\## Limitations



\- Yahrzeit computation flags but does not resolve halachic edge cases (which Adar to observe in a leap year, or which day to substitute when the original date doesn't exist in a given year). These are religious-legal questions that vary by community.

\- No zmanim (the religiously significant times of day, like sunrise, sunset, and candle-lighting) — those require geographic and astronomical input.

\- Diaspora vs. Israel parsha schedules differ a few weeks per year; the agent passes `--israel` if the user is asking about an Israeli reading.

\- Hebrew month numbering uses Nisan as month 1 (the religious ordering, since the Torah designates Nisan as "the first of months" — Exodus 12:2) rather than Tishrei as month 1 (the civil ordering). The choice doesn't affect correctness; it's just a numbering convention.

