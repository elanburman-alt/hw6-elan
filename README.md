\# hebrew-date-converter — Week 6 Reusable Skill



\*\*Author:\*\* Elan Burman

\*\*Course:\*\* Generative AI (BU.330.760), Johns Hopkins Carey Business School

\*\*Video walkthrough:\*\* \[paste your video link here before submitting]



\## What this skill does



hebrew-date-converter is a reusable agent skill that performs four deterministic operations on the Hebrew calendar:



1\. \*\*Convert\*\* - Gregorian to Hebrew date or vice versa.

2\. \*\*Omer\*\* - returns the day number of sefirat ha'omer for a Gregorian date.

3\. \*\*Parsha\*\* - returns the Torah portion for the Shabbos on or after a given date.

4\. \*\*Yahrzeit\*\* - given a Hebrew date of death, returns the Gregorian dates for upcoming yahrzeit anniversaries.



\## Why I chose this task



The Hebrew calendar is lunisolar with seven leap years out of every nineteen, two possible months of Adar in leap years, and variable month lengths driven by rules that depend on the day Rosh Hashanah falls on. Language models reproduce this arithmetic unreliably - I have personally watched both ChatGPT and Claude miscount the omer and hallucinate parshiot for known weeks. The pyluach library, by contrast, is deterministic and battle-tested.



This is a textbook case where a script is genuinely load-bearing: prose alone cannot do the job. The model orchestrates (parses the user request, formats the answer, surfaces halachic warnings) while the script does the calendar math.



The skill is also genuinely useful to me: I track sefirat ha'omer annually, recently navigated parsha planning for my son's bar mitzvah, and regularly compute family yahrzeit observance dates.



\## How to use it



From a project that contains the .agents/skills/hebrew-date-converter/ folder, ask Claude Code (or any agent that respects the skill structure) any of:



\- "What's today's Hebrew date?"

\- "What day of the omer is May 12, 2026?"

\- "What's the parsha for the Shabbos of April 18, 2026?"

\- "My grandfather died on 15 Tishrei 5780. When are his next five yahrzeits?"



The agent activates the skill, invokes scripts/hebrew\_date\_tool.py, and returns prose.



You can also run the script directly:



&#x20;   pip install pyluach

&#x20;   python .agents/skills/hebrew-date-converter/scripts/hebrew\_date\_tool.py convert --date 2026-04-18 --to hebrew



\## What the script does



scripts/hebrew\_date\_tool.py is a Python CLI built on argparse with four subcommands (convert, omer, parsha, yahrzeit). It accepts dates as ISO-format strings, delegates all calendar arithmetic to pyluach, and returns clean JSON. It also detects halachic edge cases - yahrzeit dates falling on 30 Cheshvan, 30 Kislev, or in Adar of a leap year - and surfaces a halachic\_warning field rather than silently making a halachic ruling.



\## What worked well



\- The agent activated the skill correctly on prompts referencing Hebrew dates, omer, parsha, or yahrzeit, even without explicit skill names.

\- Returning JSON and letting the agent format the prose kept the script clean and the output flexible.

\- The halachic\_warning pattern is a high-value way to express the boundary between deterministic computation and rabbinic judgment, which is exactly the kind of scope question Week 5 asks us to think about.



\## Limitations



\- Yahrzeit computation flags but does not resolve which Adar to observe in a leap year.

\- No zmanim (candle-lighting, havdalah) - that requires geographic and astronomical input.

\- Diaspora vs. Israel parsha schedules differ a few weeks per year; pass --israel for Israel.

\- Hebrew year input uses Nisan-as-month-1 (halachic ordering) rather than Tishrei-as-month-1 (civil ordering used in some sources).



\## Repository structure



&#x20;   hw6-elan/

&#x20;   +-- .agents/

&#x20;   |   +-- skills/

&#x20;   |       +-- hebrew-date-converter/

&#x20;   |           +-- SKILL.md

&#x20;   |           +-- scripts/

&#x20;   |               +-- hebrew\_date\_tool.py

&#x20;   +-- README.md

&#x20;   +-- .gitignore

