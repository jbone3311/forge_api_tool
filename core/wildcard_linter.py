#!/usr/bin/env python3
"""
Wildcard Linter & Analyzer

Comprehensive wildcard validation and analysis tool that extends the encoding fix utility
with deep linting capabilities:
- Empty wildcard detection
- Cycle detection (self-referencing wildcards)
- Weight sum validation
- Encoding pitfalls (UTF-8, UTF-16, BOM, Windows line endings)
- Dry-run diffs
- Per-token frequency reports
"""

import os
import re
import json
from typing import Dict, List, Tuple, Set, Optional, Any
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
import difflib


@dataclass
class WildcardIssue:
    """Represents a single wildcard issue."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'empty', 'cycle', 'encoding', 'weight', 'format'
    message: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class WildcardStats:
    """Statistics for a wildcard file."""
    file_path: str
    total_items: int
    unique_items: int
    empty_lines: int
    duplicate_items: int
    encoding: str
    has_bom: bool
    line_endings: str  # 'unix', 'windows', 'mixed'
    file_size_bytes: int
    uses_weights: bool
    weight_sum: float


@dataclass
class FrequencyReport:
    """Token frequency analysis."""
    wildcard_name: str
    total_tokens: int
    unique_tokens: int
    token_frequencies: Dict[str, int]
    most_common: List[Tuple[str, int]]
    least_common: List[Tuple[str, int]]


class WildcardLinter:
    """
    Comprehensive wildcard linter with validation, analysis, and reporting.
    """
    
    def __init__(self, wildcards_dir: str = "wildcards", strict_mode: bool = False):
        """
        Initialize the wildcard linter.
        
        Args:
            wildcards_dir: Directory containing wildcard files
            strict_mode: If True, treat warnings as errors
        """
        self.wildcards_dir = wildcards_dir
        self.strict_mode = strict_mode
        self.issues: List[WildcardIssue] = []
        self.stats: Dict[str, WildcardStats] = {}
        self.frequency_reports: Dict[str, FrequencyReport] = {}
        self.wildcard_graph: Dict[str, Set[str]] = {}  # For cycle detection
    
    def lint_all(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Run comprehensive linting on all wildcard files.
        
        Args:
            dry_run: If True, only analyze without fixing
            
        Returns:
            Dictionary with complete linting results
        """
        self.issues.clear()
        self.stats.clear()
        self.frequency_reports.clear()
        self.wildcard_graph.clear()
        
        # Find all wildcard files
        wildcard_files = self._discover_wildcard_files()
        
        if not wildcard_files:
            return {
                'success': False,
                'error': f"No wildcard files found in '{self.wildcards_dir}'"
            }
        
        # Analyze each file
        for file_path in wildcard_files:
            self._analyze_file(file_path)
        
        # Detect cycles across all wildcards
        self._detect_cycles()
        
        # Generate frequency reports
        for file_path in wildcard_files:
            self._generate_frequency_report(file_path)
        
        # Generate results summary
        results = self._generate_results(dry_run)
        
        return results
    
    def _discover_wildcard_files(self) -> List[str]:
        """Discover all .txt files in the wildcards directory."""
        wildcard_files = []
        
        if not os.path.exists(self.wildcards_dir):
            return wildcard_files
        
        for root, dirs, files in os.walk(self.wildcards_dir):
            for file in files:
                if file.endswith('.txt') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    wildcard_files.append(file_path)
        
        return sorted(wildcard_files)
    
    def _analyze_file(self, file_path: str):
        """Perform comprehensive analysis on a single wildcard file."""
        # Get file stats
        stats = self._get_file_stats(file_path)
        self.stats[file_path] = stats
        
        # Check for empty files
        if stats.total_items == 0:
            self.issues.append(WildcardIssue(
                severity='error',
                category='empty',
                message='Wildcard file is empty or contains only whitespace',
                file_path=file_path,
                suggestion='Add at least one valid wildcard entry or remove this file'
            ))
        
        # Check for encoding issues
        self._check_encoding(file_path, stats)
        
        # Check for duplicate items
        if stats.duplicate_items > 0:
            self.issues.append(WildcardIssue(
                severity='warning',
                category='format',
                message=f'Found {stats.duplicate_items} duplicate items',
                file_path=file_path,
                suggestion='Remove duplicate entries to improve randomization'
            ))
        
        # Check weight sums if weights are used
        if stats.uses_weights:
            self._check_weights(file_path, stats)
        
        # Build wildcard graph for cycle detection
        self._build_wildcard_graph(file_path)
    
    def _get_file_stats(self, file_path: str) -> WildcardStats:
        """Gather comprehensive statistics for a wildcard file."""
        # Detect encoding
        encoding, has_bom = self._detect_encoding(file_path)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()
            
            lines = content.splitlines()
        except Exception as e:
            # Fallback
            with open(file_path, 'rb') as f:
                raw_content = f.read()
            lines = raw_content.decode('utf-8', errors='replace').splitlines()
        
        # Analyze content
        items = [line.strip() for line in lines if line.strip()]
        empty_lines = len([line for line in lines if not line.strip()])
        unique_items = len(set(items))
        duplicate_items = len(items) - unique_items
        
        # Detect line endings
        line_endings = self._detect_line_endings(content)
        
        # Check for weights
        uses_weights = any(':' in item and self._is_weighted_item(item) for item in items)
        weight_sum = self._calculate_weight_sum(items) if uses_weights else 0.0
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return WildcardStats(
            file_path=file_path,
            total_items=len(items),
            unique_items=unique_items,
            empty_lines=empty_lines,
            duplicate_items=duplicate_items,
            encoding=encoding,
            has_bom=has_bom,
            line_endings=line_endings,
            file_size_bytes=file_size,
            uses_weights=uses_weights,
            weight_sum=weight_sum
        )
    
    def _detect_encoding(self, file_path: str) -> Tuple[str, bool]:
        """
        Detect file encoding and BOM presence.
        
        Returns:
            Tuple of (encoding_name, has_bom)
        """
        with open(file_path, 'rb') as f:
            raw_bytes = f.read()
        
        # Check for BOM markers
        if raw_bytes.startswith(b'\xff\xfe'):
            return 'utf-16-le', True
        elif raw_bytes.startswith(b'\xfe\xff'):
            return 'utf-16-be', True
        elif raw_bytes.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig', True
        
        # Try UTF-8
        try:
            raw_bytes.decode('utf-8')
            return 'utf-8', False
        except UnicodeDecodeError:
            pass
        
        # Try other encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                raw_bytes.decode(encoding)
                return encoding, False
            except UnicodeDecodeError:
                continue
        
        return 'unknown', False
    
    def _detect_line_endings(self, content: str) -> str:
        """Detect line ending style (Unix, Windows, or mixed)."""
        has_crlf = '\r\n' in content
        has_lf_only = '\n' in content.replace('\r\n', '')
        
        if has_crlf and has_lf_only:
            return 'mixed'
        elif has_crlf:
            return 'windows'
        elif has_lf_only:
            return 'unix'
        else:
            return 'none'
    
    def _check_encoding(self, file_path: str, stats: WildcardStats):
        """Check for encoding-related issues."""
        # Check for non-UTF-8 encoding
        if stats.encoding not in ['utf-8', 'utf-8-sig']:
            self.issues.append(WildcardIssue(
                severity='error',
                category='encoding',
                message=f'File uses {stats.encoding} encoding instead of UTF-8',
                file_path=file_path,
                suggestion='Convert file to UTF-8 encoding (use --fix flag)'
            ))
        
        # Check for BOM in UTF-8
        if stats.has_bom and stats.encoding == 'utf-8-sig':
            self.issues.append(WildcardIssue(
                severity='warning',
                category='encoding',
                message='File contains UTF-8 BOM marker (unnecessary)',
                file_path=file_path,
                suggestion='Remove BOM marker for cleaner UTF-8'
            ))
        
        # Check for Windows line endings (CRLF)
        if stats.line_endings == 'windows':
            self.issues.append(WildcardIssue(
                severity='info',
                category='encoding',
                message='File uses Windows line endings (CRLF)',
                file_path=file_path,
                suggestion='Consider using Unix line endings (LF) for consistency'
            ))
        
        # Check for mixed line endings
        if stats.line_endings == 'mixed':
            self.issues.append(WildcardIssue(
                severity='warning',
                category='encoding',
                message='File has mixed line endings (both CRLF and LF)',
                file_path=file_path,
                suggestion='Normalize to consistent line endings'
            ))
    
    def _is_weighted_item(self, item: str) -> bool:
        """Check if an item uses weight syntax (e.g., "value:0.5")."""
        # Simple heuristic: check if colon is followed by a number
        parts = item.rsplit(':', 1)
        if len(parts) == 2:
            try:
                float(parts[1].strip())
                return True
            except ValueError:
                pass
        return False
    
    def _calculate_weight_sum(self, items: List[str]) -> float:
        """Calculate the sum of all weights in weighted items."""
        weight_sum = 0.0
        
        for item in items:
            if self._is_weighted_item(item):
                parts = item.rsplit(':', 1)
                try:
                    weight = float(parts[1].strip())
                    weight_sum += weight
                except ValueError:
                    pass
        
        return weight_sum
    
    def _check_weights(self, file_path: str, stats: WildcardStats):
        """Check weight-related issues."""
        # Weight sum should typically be around 1.0 for proper probability distribution
        if stats.uses_weights:
            if abs(stats.weight_sum - 1.0) > 0.01:  # Allow small floating point errors
                severity = 'warning' if abs(stats.weight_sum - 1.0) < 0.1 else 'error'
                self.issues.append(WildcardIssue(
                    severity=severity,
                    category='weight',
                    message=f'Weight sum is {stats.weight_sum:.3f} (expected ~1.0)',
                    file_path=file_path,
                    suggestion='Adjust weights to sum to 1.0 for proper probability distribution'
                ))
    
    def _build_wildcard_graph(self, file_path: str):
        """Build a graph of wildcard references for cycle detection."""
        wildcard_name = self._get_wildcard_name(file_path)
        referenced_wildcards = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Find all wildcard references (e.g., __OTHER_WILDCARD__)
            wildcard_pattern = r'__([A-Z_]+)__'
            references = re.findall(wildcard_pattern, content)
            referenced_wildcards.update(references)
        
        except Exception:
            pass
        
        self.wildcard_graph[wildcard_name] = referenced_wildcards
    
    def _get_wildcard_name(self, file_path: str) -> str:
        """Convert file path to wildcard name."""
        rel_path = os.path.relpath(file_path, self.wildcards_dir)
        name = rel_path.replace('.txt', '')
        name = name.replace(os.sep, '_').upper()
        return name
    
    def _detect_cycles(self):
        """Detect cycles in wildcard references using DFS."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str, path: List[str]) -> Optional[List[str]]:
            """DFS to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.wildcard_graph.get(node, set()):
                if neighbor not in visited:
                    cycle_path = has_cycle(neighbor, path.copy())
                    if cycle_path:
                        return cycle_path
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            return None
        
        # Check each wildcard for cycles
        for wildcard in self.wildcard_graph:
            if wildcard not in visited:
                cycle = has_cycle(wildcard, [])
                if cycle:
                    cycle_str = ' -> '.join(cycle)
                    # Find the file path for this wildcard
                    file_path = None
                    for fp, stats in self.stats.items():
                        if self._get_wildcard_name(fp) == wildcard:
                            file_path = fp
                            break
                    
                    self.issues.append(WildcardIssue(
                        severity='error',
                        category='cycle',
                        message=f'Detected reference cycle: {cycle_str}',
                        file_path=file_path or f'wildcard:{wildcard}',
                        suggestion='Remove circular references between wildcards'
                    ))
    
    def _generate_frequency_report(self, file_path: str):
        """Generate token frequency analysis for a wildcard file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            items = [line.strip() for line in lines if line.strip()]
            
            # Remove weights if present
            clean_items = []
            for item in items:
                if self._is_weighted_item(item):
                    clean_item = item.rsplit(':', 1)[0].strip()
                    clean_items.append(clean_item)
                else:
                    clean_items.append(item)
            
            # Count frequencies
            counter = Counter(clean_items)
            wildcard_name = self._get_wildcard_name(file_path)
            
            report = FrequencyReport(
                wildcard_name=wildcard_name,
                total_tokens=len(clean_items),
                unique_tokens=len(set(clean_items)),
                token_frequencies=dict(counter),
                most_common=counter.most_common(10),
                least_common=counter.most_common()[:-11:-1]  # Last 10
            )
            
            self.frequency_reports[file_path] = report
        
        except Exception as e:
            pass
    
    def _generate_results(self, dry_run: bool) -> Dict[str, Any]:
        """Generate comprehensive results dictionary."""
        # Count issues by severity
        error_count = len([i for i in self.issues if i.severity == 'error'])
        warning_count = len([i for i in self.issues if i.severity == 'warning'])
        info_count = len([i for i in self.issues if i.severity == 'info'])
        
        # Count issues by category
        category_counts = defaultdict(int)
        for issue in self.issues:
            category_counts[issue.category] += 1
        
        # Calculate health score (0-100)
        total_files = len(self.stats)
        if total_files == 0:
            health_score = 0
        else:
            # Deduct points for issues
            deductions = error_count * 10 + warning_count * 5 + info_count * 1
            max_score = 100
            health_score = max(0, max_score - deductions)
        
        return {
            'success': True,
            'dry_run': dry_run,
            'summary': {
                'total_files': total_files,
                'total_issues': len(self.issues),
                'errors': error_count,
                'warnings': warning_count,
                'info': info_count,
                'health_score': health_score
            },
            'category_counts': dict(category_counts),
            'issues': [asdict(issue) for issue in self.issues],
            'stats': {path: asdict(stats) for path, stats in self.stats.items()},
            'frequency_reports': {
                path: {
                    'wildcard_name': report.wildcard_name,
                    'total_tokens': report.total_tokens,
                    'unique_tokens': report.unique_tokens,
                    'diversity_ratio': report.unique_tokens / report.total_tokens if report.total_tokens > 0 else 0,
                    'most_common': report.most_common,
                    'least_common': report.least_common
                }
                for path, report in self.frequency_reports.items()
            }
        }
    
    def fix_issues(self, fix_categories: List[str] = None) -> Dict[str, Any]:
        """
        Automatically fix issues where possible.
        
        Args:
            fix_categories: List of categories to fix (e.g., ['encoding', 'weight'])
                           If None, fixes all auto-fixable issues
        
        Returns:
            Dictionary with fix results
        """
        if fix_categories is None:
            fix_categories = ['encoding', 'format']
        
        fixed_count = 0
        failed_fixes = []
        
        for file_path in self.stats.keys():
            fixes_applied = []
            
            # Fix encoding issues
            if 'encoding' in fix_categories:
                encoding_fix = self._fix_encoding(file_path)
                if encoding_fix['fixed']:
                    fixes_applied.append('encoding')
                    fixed_count += 1
            
            # Fix line endings
            if 'format' in fix_categories:
                line_ending_fix = self._fix_line_endings(file_path)
                if line_ending_fix['fixed']:
                    fixes_applied.append('line_endings')
                    fixed_count += 1
            
            if fixes_applied:
                print(f"✅ Fixed {', '.join(fixes_applied)} in {file_path}")
        
        return {
            'success': True,
            'fixed_count': fixed_count,
            'failed_fixes': failed_fixes
        }
    
    def _fix_encoding(self, file_path: str) -> Dict[str, Any]:
        """Fix encoding issues in a file."""
        stats = self.stats.get(file_path)
        if not stats:
            return {'fixed': False, 'error': 'No stats available'}
        
        if stats.encoding in ['utf-8', 'utf-8-sig']:
            return {'fixed': False, 'reason': 'Already UTF-8'}
        
        try:
            # Read with original encoding
            with open(file_path, 'r', encoding=stats.encoding, errors='replace') as f:
                content = f.read()
            
            # Write as UTF-8
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {'fixed': True}
        
        except Exception as e:
            return {'fixed': False, 'error': str(e)}
    
    def _fix_line_endings(self, file_path: str) -> Dict[str, Any]:
        """Normalize line endings to Unix (LF)."""
        stats = self.stats.get(file_path)
        if not stats or stats.line_endings == 'unix':
            return {'fixed': False, 'reason': 'Already Unix line endings'}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Normalize to Unix line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            return {'fixed': True}
        
        except Exception as e:
            return {'fixed': False, 'error': str(e)}
    
    def generate_diff_report(self, file_path: str, fixed_content: str) -> str:
        """Generate a unified diff showing changes."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                original_content = f.read()
            
            original_lines = original_content.splitlines(keepends=True)
            fixed_lines = fixed_content.splitlines(keepends=True)
            
            diff = difflib.unified_diff(
                original_lines,
                fixed_lines,
                fromfile=f'{file_path} (original)',
                tofile=f'{file_path} (fixed)',
                lineterm=''
            )
            
            return '\n'.join(diff)
        
        except Exception as e:
            return f"Error generating diff: {e}"


def print_lint_results(results: Dict[str, Any], verbose: bool = False):
    """Pretty-print linting results."""
    summary = results['summary']
    
    print("\n" + "="*80)
    print("🔍 WILDCARD LINTER RESULTS")
    print("="*80)
    
    # Health score with color
    health_score = summary['health_score']
    if health_score >= 80:
        health_emoji = "💚"
    elif health_score >= 60:
        health_emoji = "💛"
    else:
        health_emoji = "❤️"
    
    print(f"\n{health_emoji} Health Score: {health_score}/100")
    print(f"📁 Files Analyzed: {summary['total_files']}")
    print(f"🚨 Total Issues: {summary['total_issues']}")
    print(f"   ❌ Errors: {summary['errors']}")
    print(f"   ⚠️  Warnings: {summary['warnings']}")
    print(f"   ℹ️  Info: {summary['info']}")
    
    # Issue breakdown by category
    if results['category_counts']:
        print(f"\n📊 Issues by Category:")
        for category, count in sorted(results['category_counts'].items()):
            print(f"   • {category}: {count}")
    
    # List issues
    if results['issues']:
        print(f"\n🔍 Issues Found:")
        for issue in results['issues']:
            severity_emoji = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[issue['severity']]
            print(f"\n{severity_emoji} [{issue['severity'].upper()}] {issue['category']}")
            print(f"   File: {issue['file_path']}")
            if issue.get('line_number'):
                print(f"   Line: {issue['line_number']}")
            print(f"   {issue['message']}")
            if issue.get('suggestion'):
                print(f"   💡 Suggestion: {issue['suggestion']}")
    
    # Frequency reports (if verbose)
    if verbose and results.get('frequency_reports'):
        print(f"\n📈 Token Frequency Reports:")
        for file_path, report in list(results['frequency_reports'].items())[:5]:  # Show first 5
            print(f"\n   📄 {report['wildcard_name']}")
            print(f"      Total tokens: {report['total_tokens']}")
            print(f"      Unique tokens: {report['unique_tokens']}")
            print(f"      Diversity: {report['diversity_ratio']:.2%}")
            if report['most_common']:
                print(f"      Most common:")
                for token, count in report['most_common'][:3]:
                    print(f"         • {token}: {count}x")
    
    print("\n" + "="*80)
