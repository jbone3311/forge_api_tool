#!/usr/bin/env python3
"""
Fix the encoding issue in weather.txt file
"""

def fix_weather_encoding():
    """Fix the UTF-16 encoding issue in weather.txt"""
    try:
        # Read the file as binary
        with open('wildcards/weather.txt', 'rb') as f:
            content = f.read()
        
        # Check if it has UTF-16 BOM
        if content.startswith(b'\xff\xfe'):
            print("Detected UTF-16 BOM, converting to UTF-8...")
            # Decode as UTF-16 and re-encode as UTF-8
            content_utf8 = content.decode('utf-16').encode('utf-8')
            
            # Write back as UTF-8
            with open('wildcards/weather.txt', 'wb') as f:
                f.write(content_utf8)
            
            print("✓ Fixed weather.txt encoding")
            
            # Verify the fix
            with open('wildcards/weather.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"File now contains {len(lines)} lines:")
                for line in lines[:5]:  # Show first 5 lines
                    print(f"  {line.strip()}")
        else:
            print("File doesn't have UTF-16 BOM, no fix needed")
            
    except Exception as e:
        print(f"Error fixing weather.txt: {e}")

if __name__ == "__main__":
    fix_weather_encoding() 