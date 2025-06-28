# Wildcard Organization - Sort Directory

This directory contains organized wildcard files for the Forge API Tool, reorganized for better maintainability and user experience.

## Directory Structure

### `/colors/` - Color-related wildcards
- `basic_colors.txt` - Essential color names (14 colors)
- `extended_colors.txt` - Comprehensive color palette (156 colors)
- `color_palettes.txt` - Pre-defined color combinations (30 palettes)

### `/emotions/` - Emotion and mood wildcards
- `all_emotions.txt` - Complete consolidated emotions list (deduplicated)
- `positive_emotions.txt` - Positive emotion subset (28 emotions)
- `negative_emotions.txt` - Negative emotion subset (40 emotions)
- `complex_emotions.txt` - Complex/neutral emotions (20 emotions)

### `/atmosphere/` - Atmospheric and mood wildcards
- `atmospheric_qualities.txt` - Environmental atmosphere descriptors (23 terms)
- `narrative_moods.txt` - Storytelling mood descriptors (19 terms)
- `intensity_levels.txt` - Energy and intensity descriptors (20 terms)

### `/styles/` - Artistic style and technique wildcards
- `visual_techniques.txt` - Visual effects and techniques (45 terms)
- `artistic_styles.txt` - Complete artistic style collection (116 styles)
- `art_movements.txt` - Historical art movements (58 movements)

### `/content/` - Content-specific wildcards
- `emojis.txt` - Emoji collection (368 emojis)
- `animals.txt` - Animal names (101 animals)

## Usage Examples

### Colors
```
{colors/basic_colors} - Use basic colors
{colors/extended_colors} - Use extended color palette
{colors/color_palettes} - Use pre-defined color combinations
```

### Emotions
```
{emotions/all_emotions} - Use any emotion
{emotions/positive_emotions} - Use only positive emotions
{emotions/negative_emotions} - Use only negative emotions
{emotions/complex_emotions} - Use complex/neutral emotions
```

### Atmosphere
```
{atmosphere/atmospheric_qualities} - Add atmospheric qualities
{atmosphere/narrative_moods} - Set narrative mood
{atmosphere/intensity_levels} - Set intensity level
```

### Styles
```
{styles/visual_techniques} - Apply visual techniques
{styles/artistic_styles} - Apply artistic styles
{styles/art_movements} - Apply historical art movements
```

### Content
```
{content/emojis} - Add emojis
{content/animals} - Add animals
```

## Migration Notes

### Before (Changers directory)
- 15 files with overlapping content
- Inconsistent naming conventions
- Duplicate entries across files
- No clear organization

### After (Organized structure)
- 12 files in logical categories
- Consistent naming conventions
- Deduplicated content
- Clear organization with README

## Benefits

1. **Reduced Duplication**: Consolidated overlapping content
2. **Better Organization**: Logical grouping by category
3. **Easier Maintenance**: Clear structure for updates
4. **Improved Usability**: Intuitive file naming and organization
5. **Documentation**: Clear usage examples and structure

## File Count Reduction

- **Before**: 15 files in single directory
- **After**: 12 files in 5 organized subdirectories
- **Reduction**: 20% fewer files with better organization 