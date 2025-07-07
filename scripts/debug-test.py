#!/usr/bin/env python3
"""
Debug script to identify specific test failures
"""

import subprocess
import sys
from pathlib import Path

def test_specific_component(component_name, test_func):
    """Test a specific component and report results"""
    print(f"\n🔍 Testing {component_name}...")
    try:
        result = test_func()
        if result:
            print(f"✅ {component_name}: PASS")
            return True
        else:
            print(f"❌ {component_name}: FAIL")
            return False
    except Exception as e:
        print(f"❌ {component_name}: ERROR - {e}")
        return False

def test_memory_system():
    """Test memory system"""
    main_progress = Path(".universal/memory/main/progress.md")
    if not main_progress.exists():
        return False
    
    with open(main_progress, 'r') as f:
        content = f.read()
    
    required_sections = ["Project Overview", "Recent Decisions & Changes", "Architecture Decisions", "Current Status"]
    return all(section in content for section in required_sections)

def test_template_system():
    """Test template system"""
    required_templates = ["ai-development-workflow.md", "ai-enhanced-testing.md", "ai-assisted-refactoring.md"]
    
    for template in required_templates:
        template_path = Path(f".universal/templates/{template}")
        if not template_path.exists():
            print(f"   Missing: {template}")
            return False
    
    return True

def test_pre_commit_hook():
    """Test pre-commit hook"""
    hook_path = Path(".universal/hooks/pre-commit")
    if not hook_path.exists():
        return False
    
    with open(hook_path, 'r') as f:
        content = f.read()
    
    required_features = ["BRANCH=$(git branch --show-current)", "PROGRESS_FILE=", "git add"]
    return all(feature in content for feature in required_features)

def main():
    print("🔧 Debug Test - Universal AI Development System")
    print("=" * 50)
    
    tests = [
        ("Memory System", test_memory_system),
        ("Template System", test_template_system),
        ("Pre-commit Hook", test_pre_commit_hook)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        if test_specific_component(name, test_func):
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("🔧 Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 