# Logic Contradiction Patterns

## Scan Patterns (regex)

### Character Ages
```python
patterns = {
    'character_age': r'谷雨(四十八|四十七|七十三|五十)岁?',
    'mentor_age': r'(七十岁|七十一岁|七十四岁|七十九)的人了',
    'practice_years': r'行医三十年(?!二)',
    'death_timing': r'(两年前|九年前)走了',
    'side_char_age': r'(五十三)了吧',
}
```

### Items
```python
patterns = {
    'needle_count': r'(二十四根|三十六根|十四根针|一套九根)',
    'fan_desc': r'扇面.*(山水|竹林)',  # Should be 墨梅
    'infant_error': r'襁褓里的婴儿',
    'wrong_age_start': r'(十五岁|十六岁).*学医',
}
```

### AI-isms
```python
patterns = {
    'ai_words': r'(下一刻|与此同时|紧接着|心头一震|瞳孔骤缩|空气凝固|不禁|顿时|宛如|犹如)',
    'ai_仿佛': r'仿佛',  # Max 1 per chapter
    'author_commentary': r'(他意识到|显然|毫无疑问|这意味着|由此可见)',
}
```

### Modern Language
```python
patterns = {
    'medical_terms': r'(神经传导|生理功能|代偿|肩袖损伤|血液循环|退行性病变)',
    'psychological': r'(焦虑|压力大|抑郁)',
    'english_mix': r'[a-zA-Z]+',  # Check context, may be false positive
}
```

## Fix Template
```python
fix_rules = [
    # (regex_pattern, replacement, description)
    (r'谷雨四十八', '谷雨四十三', 'Guyu age at departure: 48→43'),
    (r'行医三十年', '行医三十二年', 'Practice years: 30→32'),
    (r'两年前走了', '五年前走了', 'Death timing: 2→5 years ago'),
    (r'五十三了吧', '三十七了吧', 'Ma Sanjin reunion age: 53→37'),
    (r'享年七十三岁', '享年五十岁', 'Guyu death age: 73→50'),
    (r'二十四根银针', '十二根银针', 'Needle count: 24→12'),
    (r'扇面.*山水', '扇面画着一枝墨梅', 'Fan: landscape→ink plum'),
    (r'襁褓里的婴儿', '瘦弱的小丫头', 'A-Luo: infant→thin girl'),
    (r'从九岁长到', '从七岁长到', 'A-Luo start age: 9→7'),
    (r'二十年下来', '三十年下来', 'Valley duration: 20→30 years'),
]

import re
for path, content in files:
    original = content
    for pattern, replacement, desc in fix_rules:
        content = re.sub(pattern, replacement, content)
    if content != original:
        write(path, content)
```

## False Positive Filters
- "七十三岁" + "中风" in same file → patient record, NOT character age
- "山水" + "墙上挂" → wall painting, NOT folding fan
- "行医三十年" in early chapters (year 0) → round number, acceptable
