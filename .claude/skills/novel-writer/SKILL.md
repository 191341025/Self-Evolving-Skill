---
name: novel-writer
description: |
  Self-evolving novel writing workflow for long-form fiction (web novels, serial novels).
  TRIGGER when conversation involves:
  - Planning or outlining a novel (chapter plans, volume structure, timeline)
  - Writing novel chapters (batch writing, expanding, polishing)
  - Logic review and continuity checking (age/timeline/item consistency)
  - Chapter title design and renaming
  - Exporting to publishing platform format (txt files for 番茄小说 etc.)
  - Any task related to long-form fiction creation or maintenance
  BEHAVIOR:
  - Follow the 6-stage pipeline: Planning → Writing → Expansion → Logic Review → Title Design → Export
  - Use delegate_task for parallel batch writing (3 agents × 5 chapters each)
  - Always maintain a canonical timeline with character ages and event years
  - Scan for AI-isms and fix them (下一刻/顿时/不禁/宛如/犹如/仿佛)
  - Directly modify the publishing-ready txt files, not just source files
  - After any fix, grep to verify no residual errors
  - Each chapter targets ~3000 Chinese characters
allowed-tools: Bash, Read, Write, Edit
---

## Novel Writing Pipeline

```
Stage 1: Planning → Stage 2: Batch Writing → Stage 3: Expansion
                                                      ↓
Stage 6: Export ← Stage 5: Title Design ← Stage 4: Logic Review
```

## Selective Loading Protocol

Before starting work, read `references/_index.md` to load relevant knowledge.
When discovering new writing patterns, pitfalls, or workflow improvements, update the appropriate references/ file.

## Tool Selection

| Need | Tool |
|------|------|
| Chapter planning | delegate_task with planning prompt |
| Batch writing | delegate_task × 3 parallel, 5 chapters each |
| Character counting | `len([c for c in text if '\u4e00' <= c <= '\u9fff'])` |
| Logic scanning | search_files with regex patterns |
| Bulk fixing | execute_code with patch() in loop |
| File renaming | os.rename() in execute_code |

## Stage 1: Planning

1. Read existing settings, establish **canonical timeline** (character ages, event years)
2. Generate `chapter-plan-vN.md` per volume with: chapter title (2-6 chars), one-sentence summary, 2+ sensory details, emotional tone, closing image
3. Structure in 5 acts: Arrival → Rooting → Conflict → Legacy → Departure

**Rules:**
- Timeline math must be consistent: character_age = birth_year + current_year
- Adjacent volumes must have different core desire layers
- Each volume ending needs a "hook" for the next volume

## Stage 2: Batch Writing

1. Write chapters in batches of 5 using delegate_task (max 3 parallel)
2. Each subagent gets: full character context, writing style rules, 5 chapter plans, output path
3. Target: 3000 Chinese characters per chapter

**Writing Style Rules (include in every task):**
```
- Short sentences, max 40 chars
- 2+ five-sense details per chapter
- Restrained emotion - show through actions, not words
- Dialogue has subtext, not direct statement
- Chapter endings: concrete image or action, NEVER summary
- Forbidden words: 下一刻/与此同时/紧接着/心头一震/瞳孔骤缩/空气凝固/不禁/顿时/宛如/犹如/仿佛
- Forbidden patterns: 不是…而是… stacking, dash explanations, author commentary
```

## Stage 3: Expansion

1. Scan all chapters for character count
2. Chapters under 2800 chars need expansion
3. Expand in batches of 3: read original → add sensory details and scene depth → overwrite
4. Keep same story and ending, only add depth
5. Loop until average ≥ 2900 chars/chapter

## Stage 4: Logic Review

1. Establish **canonical facts table** (write to CLAUDE.md or review doc):
   - Timeline: each key event at what year
   - Character ages: each character at each time point
   - Item inventory: key props with count, appearance, origin
   - Location specs: names, geography, features

2. Batch scan with search_files for contradiction patterns:
   ```
   Character ages: [name] + 岁/四十八/四十七/七十三
   Timing: 两年前/五年前/九年前 + 走了
   Items: needle count / fan description / badge
   Modern words: 神经传导/代偿/血液循环/压力/焦虑
   AI words: 下一刻/顿时/不禁/宛如/犹如/仿佛
   ```

3. Batch fix with execute_code + patch():
   ```python
   fix_rules = [(regex, replacement, description), ...]
   for pattern, replacement, desc in fix_rules:
       new = re.sub(pattern, replacement, content)
       if new != content: write_file(new)
   ```

4. Re-scan to verify no residuals

**Common Error Patterns:**
| Error | Example | Fix |
|-------|---------|-----|
| Age offset | Character 48 when should be 43 | Align to canonical timeline |
| Death timing | "2 years ago" vs "5 years ago" | Calculate from canonical |
| Item count | Needles 12 vs 36 | Unify to setting value |
| Item description | Fan "landscape" vs "ink plum" | Unify to setting value |
| Modern terms | "nerve conduction" in dialogue | Use period-appropriate language |
| English mixed in | "shrugged了一下" | "耸了耸肩" |

**Key principle:** Directly modify the publishing-ready txt files. After each fix, grep to verify no residuals.

## Stage 5: Title Design

1. Read each chapter's content (first 10 lines + title)
2. Design unified style per volume:
   - Volume 1: Warm daily life ("柴米药香", "腊月的雪")
   - Volume 2: Journey imagery ("炊烟", "那条黄狗")
   - Volume 3: Cultivation world ("东域界碑", "灵气浓雾")
   - Volume 4: Quiet poetry ("落笔写「周」", "灯花炸开")
3. Title requirements: 2-6 chars, evocative, no single-character titles
4. Update file first line AND filename

**Good title techniques:**
- Objects/images: "银针", "折扇", "灯花"
- Actions/states: "不回头", "一个人走"
- Key quotes from text: "就这点东西", "没有回头"

## Stage 6: Export

1. Generate txt from md if needed
2. Organize by volume:
   ```
   NovelName-番茄发布版/
   ├── 第一卷-卷名/ (001-标题.txt ~ 050-标题.txt)
   ├── 第二卷-卷名/ (001-标题.txt ~ 050-标题.txt)
   └── ...
   ```
3. txt format: plain text, no markdown, chapter title as first line
4. Filename: `NNN-章名.txt` (3-digit number)

## Knowledge Evolution Protocol

When discovering new patterns during writing:
1. Is this a reusable pattern? → Add to references/
2. Is this a pitfall to avoid? → Add to references/pitfalls.md
3. Is this a workflow improvement? → Update this SKILL.md

Update references/ with:
- New writing patterns that work well
- Common AI-isms to scan for
- Timeline/age calculation formulas
- Export format requirements
