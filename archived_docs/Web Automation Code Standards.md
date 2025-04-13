# **\*\***ARCHIVED**\*\*** Web Automation Code Standards

_This document has been archived as it has been replaced by the more general AI Coding Assistant Standards._

## Core Requirements

- **SOLID Compliance**: Each class has exactly one responsibility; interfaces are lean; dependencies are injected
- **Function Size**: All methods ≤20 lines with single purpose (measured by line count)
- **Error Handling**: Every web interaction has try/except with specific recovery steps
- **Logging**: INFO for operations, ERROR for failures with context details

## Technical Standards

- **Element Selection**: Implement primary + fallback selectors for each element
- **Wait Strategy**: Use only explicit waits with timeout constants (no sleep())
- **Browser Support**: Test and verify on Chrome, Firefox, and Edge
- **Configuration**: Store all timeouts, URLs, and selectors in config.py

## Self-Check Checklist

- [ ] All classes have single responsibility (count responsibilities)
- [ ] No method exceeds 20 lines (verify with line counter)
- [ ] Every web interaction has error handling (count try/except blocks)
- [ ] Logging exists at appropriate levels (verify log calls)
- [ ] Selectors include fallback strategies (count selector alternatives)
- [ ] All waits are explicit with timeouts from config (no hardcoded values)
- [ ] Cross-browser compatibility verified (list tested browsers)

## Completion Status

End implementation with:

- `STATUS: COMPLETE ✓` (All checklist items verified)
- `STATUS: INCOMPLETE ⚠` (List specific failed checklist items)
