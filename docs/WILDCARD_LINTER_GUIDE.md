# Wildcard Linter & Analyzer - Complete Guide

## 🎯 Overview

The **Wildcard Linter** is an enterprise-grade validation and analysis system for wildcard files. It extends the original encoding fix utility with comprehensive validation, cycle detection, weight analysis, and token frequency reports.

## ✨ Features

### Detection Capabilities

| Category | Detection | Severity | Auto-Fix |
|----------|-----------|----------|----------|
| **Empty Files** | Files with no content or only whitespace | Error | ❌ |
| **Encoding Issues** | Non-UTF-8 encoding (UTF-16, UTF-16-BE) | Error | ✅ |
| **Circular References** | Wildcards referencing each other in cycles | Error | ❌ |
| **Weight Validation** | Weight sums that don't equal 1.0 | Error/Warning | ❌ |
| **BOM Markers** | UTF-8 with BOM (unnecessary) | Warning | ✅ |
| **Mixed Line Endings** | Both CRLF and LF in same file | Warning | ✅ |
| **Duplicate Items** | Repeated entries in wildcard files | Warning | ❌ |
| **Windows Line Endings** | CRLF instead of LF | Info | ✅ |

### Analysis Features

- **Token Frequency Analysis**: Count how often each item appears
- **Diversity Metrics**: Ratio of unique items to total items
- **Health Score**: 0-100 score based on issues found
- **Category Breakdown**: Issues grouped by type
- **File Statistics**: Encoding, size, line count per file

## 🚀 Quick Start

### Basic Linting
```bash
python cli.py wildcards lint
```

### With Frequency Reports
```bash
python cli.py wildcards lint --verbose
```

### Auto-Fix Issues
```bash
python cli.py wildcards lint --fix
```

### Strict Mode (Warnings = Errors)
```bash
python cli.py wildcards lint --strict
```

### JSON Output (for CI/CD)
```bash
python cli.py wildcards lint --json
```

## 📊 Understanding Results

### Health Score Calculation

```
Max Score: 100
Deductions:
  - Errors: -10 points each
  - Warnings: -5 points each
  - Info: -1 point each
```

**Score Interpretation:**
- 🟢 **80-100**: Excellent - Production ready
- 🟡 **60-79**: Good - Minor improvements needed
- 🔴 **0-59**: Poor - Significant issues to address

### Issue Severity Levels

#### ❌ Errors (Must Fix)
These issues will cause problems in production:
- **Empty wildcards**: No options to randomize
- **Bad encoding**: May not load correctly
- **Circular references**: Infinite loops possible
- **Weight errors**: Incorrect probability distribution

#### ⚠️ Warnings (Should Fix)
These issues may cause unexpected behavior:
- **Duplicates**: Reduces randomization effectiveness
- **Mixed line endings**: Platform compatibility issues
- **BOM markers**: Unnecessary file cruft
- **Weight warnings**: Slightly off probability

#### ℹ️ Info (Optional)
These are style/convention issues:
- **Windows line endings**: Not wrong, just inconsistent

## 🔧 Auto-Fix Capabilities

The linter can automatically fix:

### ✅ Encoding Issues
- Converts UTF-16/UTF-16-BE to UTF-8
- Removes UTF-8 BOM markers
- Handles various encodings gracefully

### ✅ Line Ending Issues
- Normalizes to Unix (LF) line endings
- Fixes mixed line endings
- Handles Windows (CRLF) properly

### ❌ Cannot Auto-Fix
- Empty files (requires content)
- Circular references (requires manual redesign)
- Duplicate items (requires manual review)
- Weight sums (requires manual adjustment)

## 📈 Frequency Analysis

### What It Shows

**Per Wildcard File:**
- Total number of tokens
- Number of unique tokens
- Diversity ratio (unique/total)
- Most common items (top 10)
- Least common items (bottom 10)

**Diversity Ratio Interpretation:**
```
100%  = All unique items (perfect randomization)
90%+  = Very good diversity
75-90% = Good diversity
50-75% = Moderate diversity  
<50%  = Low diversity (many duplicates)
```

### Example Output

```
📈 Token Frequency Reports:
   📄 ACTIONS
      Total tokens: 156
      Unique tokens: 142
      Diversity: 91.03%
      Most common:
         • walking: 3x
         • running: 2x
         • jumping: 2x
```

## 🔄 Cycle Detection

### What Are Cycles?

Cycles occur when wildcards reference each other in a loop:

```
A.txt contains: __B__
B.txt contains: __C__
C.txt contains: __A__  ← Creates cycle A→B→C→A
```

### Why They're Bad

- Can cause infinite loops
- Unpredictable resolution
- May crash the wildcard engine

### Detection Method

Uses **Depth-First Search (DFS)** to find cycles:
1. Build dependency graph from all wildcards
2. Traverse graph looking for back-edges
3. Report complete cycle path when found

### Example Error

```
❌ [ERROR] cycle
   File: wildcards/A.txt
   Detected reference cycle: A → B → C → A
   💡 Suggestion: Remove circular references between wildcards
```

## ⚖️ Weight Validation

### Weight Syntax

Some wildcard systems support weighted entries:
```
option1:0.5
option2:0.3
option3:0.2
```

### Validation Rules

**Error** if weight sum differs by >0.1 from 1.0:
```
option1:0.4
option2:0.3  ← Sum = 0.7 (ERROR)
```

**Warning** if weight sum differs by 0.01-0.1 from 1.0:
```
option1:0.4
option2:0.3
option3:0.25  ← Sum = 0.95 (WARNING)
```

**OK** if weight sum is ~1.0 (±0.01):
```
option1:0.4
option2:0.3
option3:0.3  ← Sum = 1.0 (OK)
```

## 🎨 CLI Examples

### Check All Wildcards
```bash
python cli.py wildcards lint
```

### Custom Directory
```bash
python cli.py wildcards lint --wildcards-dir custom_wildcards
```

### Dry Run (Preview Only)
```bash
# Note: Linting is always dry-run unless --fix is specified
python cli.py wildcards lint
```

### Fix and Re-Check
```bash
# Fix issues
python cli.py wildcards lint --fix

# Re-check to confirm fixes
python cli.py wildcards lint
```

### CI/CD Integration
```bash
# Exit code 0 = success, 1 = errors found
python cli.py wildcards lint --strict --json > lint-results.json
```

### Detailed Analysis
```bash
# Show frequency reports and all details
python cli.py wildcards lint --verbose
```

## 🐍 Python API

### Basic Usage

```python
from core.wildcard_linter import WildcardLinter, print_lint_results

# Create linter
linter = WildcardLinter('wildcards', strict_mode=False)

# Run linting
results = linter.lint_all(dry_run=True)

# Print results
print_lint_results(results, verbose=True)
```

### Access Results Programmatically

```python
# Check health score
health_score = results['summary']['health_score']

# Get all issues
issues = results['issues']

# Get frequency reports
freq_reports = results['frequency_reports']

# Get file statistics
file_stats = results['stats']
```

### Auto-Fix Issues

```python
# Run linting
linter = WildcardLinter('wildcards')
results = linter.lint_all(dry_run=False)

# Apply fixes
if results['success']:
    fix_results = linter.fix_issues()
    print(f"Fixed {fix_results['fixed_count']} issues")
```

## 🔍 Comparison with fix-encoding

| Feature | fix-encoding | lint |
|---------|--------------|------|
| Encoding Detection | ✅ | ✅ |
| Encoding Fix | ✅ | ✅ |
| Empty File Detection | ❌ | ✅ |
| Cycle Detection | ❌ | ✅ |
| Weight Validation | ❌ | ✅ |
| Duplicate Detection | ❌ | ✅ |
| Frequency Analysis | ❌ | ✅ |
| Health Score | ❌ | ✅ |
| Line Ending Fix | ❌ | ✅ |
| JSON Output | ❌ | ✅ |

**Recommendation**: Use `wildcards lint` for comprehensive analysis, keep `wildcards fix-encoding` for quick encoding fixes only.

## 📝 Best Practices

### 1. Run Regularly
```bash
# Add to pre-commit hook
python cli.py wildcards lint --strict
```

### 2. Fix Issues Incrementally
```bash
# Fix auto-fixable issues first
python cli.py wildcards lint --fix

# Manually fix remaining issues
# Then re-run to verify
python cli.py wildcards lint
```

### 3. Monitor Health Score
```bash
# Target: >80 health score
python cli.py wildcards lint --json | grep health_score
```

### 4. Review Frequency Reports
```bash
# Check for diversity issues
python cli.py wildcards lint --verbose
```

### 5. Document Decisions
- If warnings are intentional, document why
- Keep a log of linting results over time
- Track health score trends

## 🤖 CI/CD Integration

### GitHub Actions Example
```yaml
name: Wildcard Linting

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run wildcard linter
        run: python cli.py wildcards lint --strict --json > lint-results.json
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: lint-results
          path: lint-results.json
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running wildcard linter..."
python cli.py wildcards lint --strict

if [ $? -ne 0 ]; then
    echo "❌ Wildcard linting failed! Fix issues before committing."
    exit 1
fi

echo "✅ Wildcard linting passed!"
```

## 🐛 Troubleshooting

### "No wildcard files found"
- Check the directory path
- Ensure `.txt` files exist
- Files starting with `.` are ignored

### "Unknown encoding"
- File may be binary or corrupted
- Try: `file wildcards/problem.txt` to check type
- May need manual investigation

### False Positive Weight Warnings
- Some wildcard systems don't require weights to sum to 1.0
- Use `--json` to filter out weight warnings programmatically

### High Number of Duplicates
- May be intentional for weighting
- Review if duplicates serve a purpose
- Consider using explicit weights instead

## 📚 Related Documentation

- [Wildcard System Overview](../README.md#wildcard-management)
- [Encoding Fix Utility](../README.md#wildcard-encoding-fix-utility)
- [CLI Reference](../README.md#cli-usage)
- [API Documentation](../README.md#python-api)

## 🎓 Advanced Topics

### Custom Validation Rules

You can extend the linter with custom rules:

```python
from core.wildcard_linter import WildcardLinter, WildcardIssue

class CustomLinter(WildcardLinter):
    def _analyze_file(self, file_path: str):
        super()._analyze_file(file_path)
        
        # Add custom validation
        if self._has_profanity(file_path):
            self.issues.append(WildcardIssue(
                severity='error',
                category='content',
                message='File contains inappropriate content',
                file_path=file_path
            ))
```

### Batch Processing

Process multiple wildcard directories:

```python
directories = ['wildcards', 'custom_wildcards', 'test_wildcards']

for directory in directories:
    linter = WildcardLinter(directory)
    results = linter.lint_all()
    print(f"\n{directory}: Health Score = {results['summary']['health_score']}")
```

---

**Last Updated**: Version 2.3  
**Author**: Forge API Tool Team  
**License**: MIT
