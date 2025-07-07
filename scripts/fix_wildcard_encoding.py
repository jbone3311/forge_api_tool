#!/usr/bin/env python3
"""
Wildcard Encoding Fix Utility

This script fixes encoding issues in all wildcard files by converting them from UTF-16 to UTF-8.
It recursively scans the wildcards directory and fixes any files with UTF-16 BOM encoding.
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Tuple


def find_wildcard_files(wildcards_dir: str = "wildcards") -> List[str]:
    """Find all .txt files in the wildcards directory and subdirectories."""
    wildcard_files = []
    
    # Find all .txt files recursively
    pattern = os.path.join(wildcards_dir, "**", "*.txt")
    wildcard_files = glob.glob(pattern, recursive=True)
    
    return wildcard_files


def check_file_encoding(file_path: str) -> Tuple[bool, str, str]:
    """
    Check if a file has UTF-16 BOM encoding.
    
    Returns:
        Tuple of (needs_fix, current_encoding, error_message)
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check for UTF-16 BOM
        if content.startswith(b'\xff\xfe'):
            return True, "UTF-16", ""
        elif content.startswith(b'\xfe\xff'):
            return True, "UTF-16-BE", ""
        else:
            return False, "UTF-8", ""
            
    except Exception as e:
        return False, "Unknown", str(e)


def fix_file_encoding(file_path: str) -> Tuple[bool, str]:
    """
    Fix the encoding of a single file by converting from UTF-16 to UTF-8.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        # Read the file as binary
        with open(file_path, 'rb') as f:
            content = f.read()

        # Check if it has UTF-16 BOM
        if content.startswith(b'\xff\xfe'):
            # Decode as UTF-16 and re-encode as UTF-8
            content_utf8 = content.decode('utf-16').encode('utf-8')
            
            # Write back as UTF-8
            with open(file_path, 'wb') as f:
                f.write(content_utf8)
            
            return True, "Fixed UTF-16 encoding"
            
        elif content.startswith(b'\xfe\xff'):
            # Decode as UTF-16-BE and re-encode as UTF-8
            content_utf8 = content.decode('utf-16-be').encode('utf-8')
            
            # Write back as UTF-8
            with open(file_path, 'wb') as f:
                f.write(content_utf8)
            
            return True, "Fixed UTF-16-BE encoding"
        else:
            return False, "No encoding fix needed"

    except Exception as e:
        return False, f"Error fixing file: {e}"


def verify_file_readable(file_path: str) -> Tuple[bool, str]:
    """
    Verify that a file can be read properly after fixing.
    
    Returns:
        Tuple of (readable, message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return True, f"Readable ({len(lines)} lines)"
    except Exception as e:
        return False, f"Read error: {e}"


def fix_all_wildcard_encoding(wildcards_dir: str = "wildcards", dry_run: bool = False) -> Dict[str, any]:
    """
    Fix encoding issues in all wildcard files.
    
    Args:
        wildcards_dir: Directory containing wildcard files
        dry_run: If True, only check files without making changes
    
    Returns:
        Dictionary with results summary
    """
    results = {
        "total_files": 0,
        "files_checked": 0,
        "files_fixed": 0,
        "files_with_errors": 0,
        "errors": [],
        "fixed_files": [],
        "skipped_files": [],
        "verification_errors": []
    }
    
    print(f"🔍 Scanning for wildcard files in '{wildcards_dir}'...")
    
    # Find all wildcard files
    wildcard_files = find_wildcard_files(wildcards_dir)
    results["total_files"] = len(wildcard_files)
    
    if not wildcard_files:
        print("❌ No wildcard files found!")
        return results
    
    print(f"📁 Found {len(wildcard_files)} wildcard files")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    
    # Process each file
    for file_path in wildcard_files:
        results["files_checked"] += 1
        print(f"\n📄 Checking: {file_path}")
        
        # Check current encoding
        needs_fix, current_encoding, error_msg = check_file_encoding(file_path)
        
        if error_msg:
            results["files_with_errors"] += 1
            results["errors"].append(f"{file_path}: {error_msg}")
            print(f"❌ Error checking file: {error_msg}")
            continue
        
        if needs_fix:
            print(f"⚠️  Detected {current_encoding} encoding")
            
            if dry_run:
                print(f"🔍 Would fix: {file_path}")
                results["fixed_files"].append(file_path)
            else:
                # Fix the encoding
                success, message = fix_file_encoding(file_path)
                if success:
                    print(f"✅ {message}")
                    results["files_fixed"] += 1
                    results["fixed_files"].append(file_path)
                    
                    # Verify the fix
                    readable, verify_msg = verify_file_readable(file_path)
                    if readable:
                        print(f"✅ {verify_msg}")
                    else:
                        print(f"❌ Verification failed: {verify_msg}")
                        results["verification_errors"].append(f"{file_path}: {verify_msg}")
                else:
                    print(f"❌ {message}")
                    results["errors"].append(f"{file_path}: {message}")
        else:
            print(f"✅ Already UTF-8 encoded")
            results["skipped_files"].append(file_path)
    
    return results


def print_summary(results: Dict[str, any]):
    """Print a summary of the encoding fix results."""
    print("\n" + "="*60)
    print("📊 WILDCARD ENCODING FIX SUMMARY")
    print("="*60)
    print(f"📁 Total files found: {results['total_files']}")
    print(f"🔍 Files checked: {results['files_checked']}")
    print(f"✅ Files fixed: {results['files_fixed']}")
    print(f"⏭️  Files skipped (already UTF-8): {len(results['skipped_files'])}")
    print(f"❌ Files with errors: {results['files_with_errors']}")
    
    if results['fixed_files']:
        print(f"\n🔧 Fixed files:")
        for file_path in results['fixed_files']:
            print(f"   ✅ {file_path}")
    
    if results['errors']:
        print(f"\n❌ Errors encountered:")
        for error in results['errors']:
            print(f"   ❌ {error}")
    
    if results['verification_errors']:
        print(f"\n⚠️  Verification errors:")
        for error in results['verification_errors']:
            print(f"   ⚠️  {error}")
    
    print("="*60)


def main():
    """Main function to run the wildcard encoding fix."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix encoding issues in wildcard files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/fix_wildcard_encoding.py                    # Fix all wildcard files
  python scripts/fix_wildcard_encoding.py --dry-run          # Check without fixing
  python scripts/fix_wildcard_encoding.py --wildcards-dir custom_wildcards  # Custom directory
        """
    )
    
    parser.add_argument(
        "--wildcards-dir",
        default="wildcards",
        help="Directory containing wildcard files (default: wildcards)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check files without making changes"
    )
    
    args = parser.parse_args()
    
    # Check if wildcards directory exists
    if not os.path.exists(args.wildcards_dir):
        print(f"❌ Wildcards directory '{args.wildcards_dir}' not found!")
        return 1
    
    # Run the encoding fix
    results = fix_all_wildcard_encoding(args.wildcards_dir, args.dry_run)
    
    # Print summary
    print_summary(results)
    
    # Return appropriate exit code
    if results['errors'] or results['verification_errors']:
        return 1
    else:
        return 0


if __name__ == "__main__":
    exit(main()) 