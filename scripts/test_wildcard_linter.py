#!/usr/bin/env python3
"""
Test script for the Wildcard Linter

Demonstrates the comprehensive wildcard linting capabilities.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from core.wildcard_linter import WildcardLinter, print_lint_results


def main():
    print("="*80)
    print("🔍 WILDCARD LINTER - DEMONSTRATION")
    print("="*80)
    print()
    
    # Test with the actual wildcards directory
    wildcards_dir = project_root / "wildcards"
    
    if not wildcards_dir.exists():
        print(f"❌ Wildcards directory not found: {wildcards_dir}")
        return 1
    
    print(f"📁 Analyzing wildcards in: {wildcards_dir}")
    print()
    
    # Create linter instance
    linter = WildcardLinter(str(wildcards_dir), strict_mode=False)
    
    # Run comprehensive linting
    print("Running comprehensive analysis...")
    print()
    results = linter.lint_all(dry_run=True)
    
    # Print results
    if results.get('success'):
        print_lint_results(results, verbose=True)
        
        # Show some frequency analysis examples
        print("\n" + "="*80)
        print("📊 SAMPLE FREQUENCY ANALYSIS")
        print("="*80)
        
        freq_reports = results.get('frequency_reports', {})
        for file_path, report in list(freq_reports.items())[:3]:  # Show first 3
            print(f"\n📄 {report['wildcard_name']}")
            print(f"   Total tokens: {report['total_tokens']}")
            print(f"   Unique tokens: {report['unique_tokens']}")
            print(f"   Diversity: {report['diversity_ratio']:.2%}")
            
            if report.get('most_common'):
                print(f"   Most common items:")
                for token, count in report['most_common'][:5]:
                    print(f"      • {token}: {count}x")
        
        print("\n" + "="*80)
        print("✅ LINTING COMPLETE")
        print("="*80)
        
        # Return appropriate exit code
        summary = results['summary']
        if summary['errors'] > 0:
            return 1
        return 0
    else:
        print(f"❌ Linting failed: {results.get('error', 'Unknown error')}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
