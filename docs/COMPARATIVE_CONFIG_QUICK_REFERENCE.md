# 🚀 COMPARATIVE ANALYSIS CONFIG - QUICK REFERENCE

## 📍 Location
`config/parameters.yaml` → `analysis:` → `comparative_analysis:`

---

## ⚙️ Settings at a Glance

### Comparison Limits
```yaml
min_countries: 2              # Minimum required
max_countries: 100            # Maximum allowed
recommended_countries: 10     # Sweet spot
```

### Gap Thresholds
```yaml
gap_thresholds:
  highly_competitive: 1.0     # < 1.0 pts
  moderately_competitive: 2.0 # 1-2 pts
  uncompetitive: 2.0          # > 2.0 pts
```

### Display Options
```yaml
display:
  show_scores: true
  show_strengths_weaknesses: true
  show_subcategory_details: true
  decimal_places: 2
```

### Summary Control
```yaml
summary:
  include_top_performers: 3
  include_bottom_performers: 1
  highlight_competitive_subcategories: 2
  highlight_gap_subcategories: 2
```

---

## 🎯 What Each Setting Controls

| Setting | Controls | Example Impact |
|---------|----------|----------------|
| `min_countries` | Minimum countries for comparison | Rejects single-country requests |
| `max_countries` | Maximum countries per analysis | Prevents system overload |
| `highly_competitive` | "Minimal variation" threshold | Gap < 1.0 = minimal |
| `moderately_competitive` | "Moderate variation" threshold | Gap 1-2 = moderate |
| `show_scores` | Display numerical scores | Show/hide score values |
| `decimal_places` | Score precision | 2 = 7.35, 1 = 7.4 |
| `include_top_performers` | # of leaders to mention | Summary highlights top 3 |

---

## 🧪 Quick Test

```bash
python scripts/test_comparative_config.py
```

**Should see**: ✅ ALL CONFIG TESTS PASSED!

---

## 💡 Common Customizations

### Tighten Limits (Faster Processing)
```yaml
max_countries: 50
recommended_countries: 8
```

### More Competitive Thresholds
```yaml
gap_thresholds:
  highly_competitive: 0.5
  moderately_competitive: 1.0
```

### Detailed Summaries
```yaml
summary:
  include_top_performers: 5
  include_bottom_performers: 2
```

---

## 🔧 Code Usage

```python
import yaml
from src.agents.analysis_agents import ComparativeAnalysisAgent

# Load config
with open('../config/parameters.yaml') as f:
    config = yaml.safe_load(f)

# Initialize with config
agent = ComparativeAnalysisAgent(
    mode=AgentMode.MOCK,
    config=config['analysis']  # Pass analysis section
)

# Use normally
result = agent.compare(["Germany", "USA", "Brazil"])
```

---

## ⚠️ Validation Rules

| Rule | Min | Max | Default |
|------|-----|-----|---------|
| Countries per comparison | 2 | 100 | N/A |
| Gap threshold (competitive) | 0.1 | 5.0 | 1.0 |
| Decimal places | 0 | 4 | 2 |
| Top performers in summary | 1 | 10 | 3 |

---

## 📊 Impact on Output

### Before Config
```
"Overall scores span 1.5 points, indicating moderate variation"
```

### After Config (with highly_competitive: 2.0)
```
"Overall scores span 1.5 points, indicating minimal variation"
```

---

## 🆘 Troubleshooting

### Config not working?
1. Check YAML syntax: `yamllint config/parameters.yaml`
2. Verify agent receives config: `agent.config`
3. Check defaults in code: All `get()` calls have fallbacks

### Unexpected validation errors?
1. Review `min_countries` and `max_countries`
2. Check your input list length
3. Enable debug logging: `logger.setLevel(logging.DEBUG)`

---

## 📚 Full Documentation
See `COMPARATIVE_ANALYSIS_CONFIG_GUIDE.md` for complete details

---

*Quick Reference | Agent #20 | Version 1.0*
