#!/usr/bin/env python3
"""
Simple test runner for Forge API Tool.
Delegates to the organized test suite in tests/run_all_tests.py
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run tests using the organized test suite."""
    # Get the path to the test runner
    test_runner = Path(__file__).parent / "tests" / "run_all_tests.py"
    
    if not test_runner.exists():
        print("❌ Test runner not found at tests/run_all_tests.py")
        sys.exit(1)
    
    # Pass all arguments to the test runner
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    try:
        # Run the test suite
        result = subprocess.run([sys.executable, str(test_runner)] + args, 
                              cwd=Path(__file__).parent)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 