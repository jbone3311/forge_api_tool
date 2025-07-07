# Wildcard Encoding Fix - Complete Documentation

## Overview

The Wildcard Encoding Fix utility is a comprehensive solution for detecting and fixing encoding issues in wildcard files. It addresses the common problem of UTF-16 encoded files that cause read errors when the application tries to load wildcards.

## Problem Description

### What Causes Encoding Issues?
- **Cross-Platform File Transfer**: Files created on Windows with UTF-16 encoding
- **Text Editor Defaults**: Some text editors save files with UTF-16 BOM by default
- **Copy-Paste Operations**: Copying content from certain applications can introduce encoding issues
- **File System Differences**: Different operating systems handle text encoding differently

### Symptoms of Encoding Issues
- `UnicodeDecodeError` when reading wildcard files
- Wildcard files not loading properly
- Application crashes when accessing wildcard content
- Inconsistent behavior across different systems

## Solution Components

### 1. Core Script: `scripts/fix_wildcard_encoding.py`

A comprehensive Python script that:
- **Recursively scans** all `.txt` files in the wildcards directory
- **Detects multiple encodings**: UTF-16, UTF-16-BE, and UTF-8
- **Safely converts** problematic files to UTF-8
- **Provides detailed reporting** of all operations
- **Includes verification** to ensure files are readable after fixing

#### Key Features
```python
# Recursive file discovery
def find_wildcard_files(wildcards_dir: str = "wildcards") -> List[str]:
    pattern = os.path.join(wildcards_dir, "**", "*.txt")
    return glob.glob(pattern, recursive=True)

# Encoding detection
def check_file_encoding(file_path: str) -> Tuple[bool, str, str]:
    # Detects UTF-16, UTF-16-BE, and UTF-8 encodings
    # Returns (needs_fix, current_encoding, error_message)

# Safe conversion
def fix_file_encoding(file_path: str) -> Tuple[bool, str]:
    # Converts files to UTF-8 while preserving content
    # Includes error handling and verification
```

### 2. CLI Integration: `cli.py`

New command-line interface for wildcard encoding management:

```bash
# Check for encoding issues (safe preview)
python cli.py wildcards fix-encoding --dry-run

# Fix all encoding issues
python cli.py wildcards fix-encoding

# Use custom wildcards directory
python cli.py wildcards fix-encoding --wildcards-dir custom_wildcards
```

#### CLI Features
- **Dry-run mode**: Preview changes without making them
- **Custom directory support**: Work with different wildcard locations
- **Detailed output**: Shows progress and results for each file
- **Error handling**: Graceful handling of file access issues

### 3. Web Interface Integration

#### Settings Modal Integration
The wildcard encoding fix is integrated into the web dashboard's Settings modal:

1. **Access**: Click the Settings button (gear icon) in the dashboard
2. **Location**: Navigate to the "Wildcard Encoding Fix" section
3. **Actions**: Three main buttons available:
   - **Check Encoding**: Preview issues without making changes
   - **Fix Encoding**: Apply fixes to all problematic files
   - **Dry Run**: Test the fix process safely

#### Real-time Results Display
- **Summary Statistics**: Total files, checked files, fixed files, errors
- **Detailed Lists**: Shows which files were fixed, skipped, or had errors
- **Visual Indicators**: Color-coded status indicators
- **Progress Tracking**: Live updates during operations

## Usage Examples

### Scenario 1: Initial Setup Check
```bash
# Check if there are any encoding issues
python cli.py wildcards fix-encoding --dry-run

# Output example:
# 🔍 Scanning for wildcard files in 'wildcards'...
# 📁 Found 186 wildcard files
# 🔍 DRY RUN MODE - No files will be modified
# 
# 📄 Checking: wildcards\actions.txt
# ⚠️  Detected UTF-16 encoding
# 🔍 Would fix: wildcards\actions.txt
# 
# 📄 Checking: wildcards\people.txt
# ⚠️  Detected UTF-16 encoding
# 🔍 Would fix: wildcards\people.txt
```

### Scenario 2: Fixing Issues
```bash
# Apply fixes to all problematic files
python cli.py wildcards fix-encoding

# Output example:
# 🔧 Fixing wildcard encoding issues...
# 🔍 Scanning for wildcard files in 'wildcards'...
# 📁 Found 186 wildcard files
# 
# 📄 Checking: wildcards\actions.txt
# ⚠️  Detected UTF-16 encoding
# ✅ Fixed UTF-16 encoding
# ✅ Readable (32 lines)
# 
# 📄 Checking: wildcards\people.txt
# ⚠️  Detected UTF-16 encoding
# ✅ Fixed UTF-16 encoding
# ✅ Readable (15 lines)
```

### Scenario 3: Web Interface Usage
1. **Open Dashboard**: Navigate to the web dashboard
2. **Access Settings**: Click the Settings button
3. **Check Status**: Click "Check Encoding" to see current status
4. **Apply Fixes**: Click "Fix Encoding" to resolve issues
5. **Review Results**: View detailed results in the interface

## Technical Details

### Supported Encodings
- **UTF-8**: Standard encoding, no conversion needed
- **UTF-16 (LE)**: Little-endian UTF-16 with BOM (`\xff\xfe`)
- **UTF-16-BE**: Big-endian UTF-16 with BOM (`\xfe\xff`)

### File Processing
1. **Binary Read**: Files are read as binary to detect BOM
2. **Encoding Detection**: BOM patterns are checked for encoding type
3. **Safe Conversion**: Content is decoded and re-encoded as UTF-8
4. **Verification**: Files are tested for readability after conversion
5. **Error Handling**: Any issues are logged and reported

### Safety Features
- **Dry-run Mode**: Preview changes without making them
- **Backup Verification**: Ensures files are readable after conversion
- **Error Recovery**: Graceful handling of file access issues
- **Detailed Logging**: Comprehensive logging of all operations

## API Endpoints

### Check Wildcard Encoding
```http
GET /api/check-wildcard-encoding?wildcards_dir=wildcards
```

**Response:**
```json
{
  "status": "success",
  "results": {
    "total_files": 186,
    "files_checked": 186,
    "files_fixed": 0,
    "files_with_errors": 0,
    "errors": [],
    "fixed_files": [],
    "skipped_files": ["wildcards/weather.txt", "..."],
    "verification_errors": []
  },
  "message": "Encoding check completed. 0 files need fixing, 186 are OK."
}
```

### Fix Wildcard Encoding
```http
POST /api/fix-wildcard-encoding
Content-Type: application/json

{
  "wildcards_dir": "wildcards",
  "dry_run": false
}
```

**Response:**
```json
{
  "status": "success",
  "results": {
    "total_files": 186,
    "files_checked": 186,
    "files_fixed": 3,
    "files_with_errors": 0,
    "errors": [],
    "fixed_files": [
      "wildcards/actions.txt",
      "wildcards/people.txt",
      "wildcards/Sort/art_styles/art_movements.txt"
    ],
    "skipped_files": ["wildcards/weather.txt", "..."],
    "verification_errors": []
  },
  "message": "Encoding fix completed. 3 files fixed, 183 skipped."
}
```

## Error Handling

### Common Error Scenarios
1. **File Access Denied**: Files that can't be read or written
2. **Corrupted Files**: Files with invalid encoding data
3. **Permission Issues**: Insufficient permissions for file operations
4. **Disk Space**: Insufficient disk space for file operations

### Error Recovery
- **Graceful Degradation**: Continues processing other files when one fails
- **Detailed Error Reporting**: Specific error messages for each file
- **Partial Success**: Reports both successful and failed operations
- **Verification**: Tests files after conversion to ensure success

## Best Practices

### When to Use
- **Initial Setup**: Check encoding when setting up the application
- **After File Transfers**: After copying wildcard files from other systems
- **Regular Maintenance**: Periodic checks to ensure file health
- **Troubleshooting**: When experiencing wildcard loading issues

### Safety Recommendations
1. **Always use dry-run first**: Preview changes before applying them
2. **Backup important files**: Keep backups of critical wildcard collections
3. **Test after fixing**: Verify that wildcards work correctly after conversion
4. **Monitor for issues**: Watch for any new encoding problems

### Performance Considerations
- **Large Collections**: The utility efficiently handles large wildcard collections
- **Recursive Scanning**: Only processes `.txt` files to avoid unnecessary work
- **Memory Efficient**: Processes files one at a time to minimize memory usage
- **Progress Reporting**: Provides real-time feedback for long operations

## Troubleshooting

### Common Issues

#### "No wildcard files found"
- **Cause**: Empty wildcards directory or incorrect path
- **Solution**: Verify wildcards directory exists and contains `.txt` files

#### "Permission denied" errors
- **Cause**: Insufficient file permissions
- **Solution**: Run with appropriate permissions or fix file permissions

#### "File is corrupted" errors
- **Cause**: Invalid file content or encoding
- **Solution**: Manually check and fix the problematic file

### Getting Help
- **Check Logs**: Review application logs for detailed error information
- **Use Dry-run**: Always test with dry-run mode first
- **Manual Verification**: Manually check files that report errors
- **Community Support**: Check GitHub issues for similar problems

## Future Enhancements

### Planned Features
- **Batch Processing**: Process multiple directories simultaneously
- **Encoding Detection**: Support for additional encoding types
- **Automated Monitoring**: Regular background checks for encoding issues
- **Integration**: Deeper integration with wildcard management system

### Extension Points
- **Custom Encodings**: Plugin system for additional encoding support
- **Advanced Reporting**: More detailed analytics and reporting
- **Scheduling**: Automated scheduling of encoding checks
- **Notifications**: Alert system for encoding issues

---

This documentation provides comprehensive information about the Wildcard Encoding Fix utility. For additional support or questions, please refer to the main README or open an issue on GitHub. 