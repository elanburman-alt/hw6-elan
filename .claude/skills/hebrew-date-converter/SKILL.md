---
name: hebrew-date-converter
description: Converts between Gregorian and Hebrew dates, computes sefirat ha omer day numbers, returns the weekly parsha for a given Shabbos, and calculates future yahrzeit dates from a Hebrew date of death. Use when the user asks about Hebrew calendar conversions, omer counting, parsha for a date, or yahrzeit observance dates. Do not use for halachic rulings, candle-lighting times, or interpretive Torah commentary.
---

# Hebrew Date Converter

The Hebrew calendar is lunisolar with leap months, variable month lengths, and conditional rules. Language models reproduce this arithmetic unreliably. This skill delegates all calendar arithmetic to a Python script using the deterministic pyluach library.

## When to use this skill

Activate this skill whenever the user asks about any of the following:
- Converting a Gregorian date to a Hebrew date or vice versa
- What day of the omer corresponds to a Gregorian date
- The parsha for a given Shabbos or week
- When a yahrzeit falls in upcoming years given a Hebrew date of death
- Any reference to Hebrew dates, parsha, sefirat ha omer, yahrzeit, or Hebrew leap year

IMPORTANT: When this skill applies, run the Python script. Do NOT use web search or web fetch for these questions. The script is faster and authoritative.

## When NOT to use this skill

- Candle-lighting times, havdalah, or zmanim (require geographic and astronomical inputs)
- Halachic rulings (refer the user to a rabbi)
- Interpretive content about the parsha such as divrei Torah or commentary
- Anything requiring real-time location, weather, or astronomical data

## How to invoke the script

The script lives at scripts/hebrew_date_tool.py relative to this SKILL.md. From the project root, the full path is:
.agents/skills/hebrew-date-converter/scripts/hebrew_date_tool.py

Run it with one of these subcommands:

1. Gregorian to Hebrew conversion:
   python .agents/skills/hebrew-date-converter/scripts/hebrew_date_tool.py convert --date YYYY-MM-DD --to hebrew

2. Hebrew to Gregorian conversion:
   python .agents/skills/hebrew-date-converter/scripts/hebrew_date_tool.py convert --date YYYY-MM-DD --to gregorian

3. Omer day number:
   python .agents/skills/hebrew-date-converter/scripts/hebrew_date_tool.py omer --date YYYY-MM-DD

4. Parsha for the Shabbos of a week:
   python .agents/skills/hebrew-date-converter/scripts/hebrew_date_tool.py parsha --date YYYY-MM-DD

5. Future yahrzeit dates from a Hebrew date of death:
   python .agents/skills/hebrew-date-converter/scripts/hebrew_date_tool.py yahrzeit --hebrew-date YYYY-MM-DD --years N

For Hebrew dates, month numbering is 1=Nisan, 2=Iyar, 3=Sivan, 4=Tammuz, 5=Av, 6=Elul, 7=Tishrei, 8=Cheshvan, 9=Kislev, 10=Tevet, 11=Shevat, 12=Adar, 13=Adar II.

## Step by step instructions for the agent

1. Identify which of the four operations the user is asking about.
2. Extract the date or dates from the user message. If ambiguous, ask one clarifying question.
3. Run the appropriate script command using the Bash tool.
4. Parse the JSON output.
5. Present the result as a short natural language answer. Do not show raw JSON.
6. If the output contains a halachic_warning field, surface it prominently and recommend rabbinic consultation.

## Output format

The script returns JSON. Reply in prose that includes the converted date or computed result, the weekday when relevant, and the halachic_warning verbatim if present.

## Limitations

- Hebrew month numbering uses Nisan as month 1.
- Yahrzeit computation flags but does not resolve halachic edge cases such as 30 Cheshvan, 30 Kislev, or Adar in a leap year.
- Diaspora and Israel parsha schedules diverge a few weeks per year. Pass --israel for Israel.
- Pyluach treats Hebrew dates as changing at midnight rather than sundown.
