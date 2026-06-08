# Timeline & Age Formulas

## Canonical Timeline Template

| Event | Year | Character Age | Notes |
|-------|------|---------------|-------|
| Story start | 0 | - | Protagonist arrives |
| Key event 1 | X | Age = birth_year + X | |
| Key event 2 | Y | Age = birth_year + Y | |
| Story end | Z | Age = birth_year + Z | |

## Age Calculation Rules

```
character_age_at_event = birth_year + event_year
years_between_events = event_year_B - event_year_A
years_since_event = current_year - event_year
```

## Common Mistakes

1. **Round number drift**: "三十年" used when actual is 32 years → always calculate exact
2. **Death timing**: "X年前" must equal (current_year - death_year), not estimated
3. **Adoption age**: adopted_age + years_since_adoption = current_age
4. **Two lifetimes**: current_life_age + previous_life_age = total_lived_years

## Validation Formula

For each character reference in text:
```python
assert stated_age == (birth_year + chapter_year), f"Age mismatch: stated={stated_age}, calculated={birth_year + chapter_year}"
```

## Timeline Integrity Check

```python
# For each chapter, verify all age references
for chapter in chapters:
    for name, stated_age in extract_ages(chapter):
        expected = BIRTH_YEAR[name] + CHAPTER_YEAR[chapter]
        if stated_age != expected:
            flag_error(chapter, name, stated_age, expected)
```
