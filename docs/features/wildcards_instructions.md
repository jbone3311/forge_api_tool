# 🃏 Wildcards Instruction Manual

**Supports: Forge, AUTOMATIC1111, sd-dynamic-prompts extension**

This guide explains how to use **wildcards** in your prompt templates to generate varied and powerful image prompts dynamically.

---

## 📂 1. Wildcard Directory

Wildcard files are simple `.txt` files stored in:

```
/wildcards/
```

You can organize them into folders:

```
/wildcards/animals.txt
/wildcards/styles/fantasy.txt
```

---

## 📝 2. Wildcard Format

Each `.txt` file should contain one item per line.
Blank lines are ignored.

**Example: `animals.txt`**

```
cat
dog
fox
elephant
koala
```

**Example: `styles/fantasy.txt`**

```
steampunk
cyberpunk
dystopian
high fantasy
```

---

## 🧠 3. How to Use Wildcards in Prompts

Use double underscores to reference a wildcard file:

```
"a portrait of a __animals__ in __styles/fantasy__ style"
```

When this prompt is processed:

* `__animals__` will be replaced by a random animal
* `__styles/fantasy__` will be replaced by a random fantasy style

---

## 🔁 4. Wildcard Expansion Behavior

* By default, one random line is selected from each wildcard file.
* You can nest wildcards inside other wildcard files:

  * `__styles/fantasy__` can contain lines like:
    `steampunk __animals__ hybrid`

---

## 🎲 5. Inline Variant Syntax

Wildcards can also be combined with **inline options**:

```
"a {portrait|photo|illustration} of a __animals__"
```

This selects:

* One option from the `{}` group
* One item from the `animals.txt` file

---

## 🔗 6. Advanced Variants

**Select multiple options:**

```
"{2$$cat|dog|fox|koala}"
```

* Selects **2 distinct options**, like: `cat, dog`
* Default separator is `, `. You can override it:

  * `{2$$cat|dog|fox|koala@@ and }` → `cat and dog`

---

## 🔄 7. Combinatorial Generation (Optional)

If your system supports it:

* Enable *Combinatorial Mode* to generate **every possible combination** of options
* Use with caution — it can produce large batches

---

## 🧪 8. Testing with Prompt Preview

To preview how prompts will look:

* Use the **Prompt Preview** feature in your dashboard
* This resolves wildcards/variants without generating images
* Useful for debugging or exploring creative combinations

---

## 📌 9. Summary of Syntax

| Syntax               | Meaning                         | Example |
| -------------------- | ------------------------------- | ------- |
| `__animals__`        | Random entry from `animals.txt` | `cat` |
| `__styles/fantasy__` | Random entry from nested file   | `steampunk` |
| `{A|B|C}`           | Choose one of A, B, or C        | `portrait` |
| `{2$$A|B|C}`        | Choose 2 distinct options       | `cat, dog` |
| `{3$$A|B|C@@ and }` | Choose 3 with "and" separator   | `cat and dog and fox` |

---

## ✅ Best Practices

* Keep wildcard lists clean and specific
* Break large categories into subfolders
* Avoid repetition by rotating wildcards (your system may support non-repeating mode)
* Use descriptive names for wildcard files
* Test your wildcards with the preview feature before generating large batches

---

## 🔧 Forge-API-Tool Specific Features

This tool includes several advanced wildcard features:

### Smart Cycling
- Wildcards cycle through all available options before repeating
- Ensures even distribution of all wildcard values
- Tracks usage statistics for each wildcard item

### Usage Tracking
- Monitor how often each wildcard value is used
- Identify underutilized or overused options
- Reset wildcard cycles when needed

### Wildcard Validation
- Automatic validation of wildcard files
- Detection of missing wildcard references
- Suggestions for wildcard values based on prompt context

### Batch Generation
- Generate multiple prompts with different wildcard combinations
- Preview wildcard expansions before generation
- Export prompt lists with wildcard values

---

## 📚 Example Configurations

Here are some example configurations using wildcards:

### Basic Portrait
```json
{
  "prompt_settings": {
    "base_prompt": "a beautiful __STYLE__ portrait of a __SUBJECT__ in __LIGHTING__",
    "negative_prompt": "blurry, low quality"
  },
  "wildcards": {
    "STYLE": "wildcards/styles.txt",
    "SUBJECT": "wildcards/subjects.txt", 
    "LIGHTING": "wildcards/lighting.txt"
  }
}
```

### Landscape Scene
```json
{
  "prompt_settings": {
    "base_prompt": "a __STYLE__ landscape of __LOCATION__ during __TIME_OF_DAY__ with __WEATHER__",
    "negative_prompt": "blurry, distorted"
  },
  "wildcards": {
    "STYLE": "wildcards/artistic_styles.txt",
    "LOCATION": "wildcards/locations.txt",
    "TIME_OF_DAY": "wildcards/time_of_day.txt",
    "WEATHER": "wildcards/weather.txt"
  }
}
```

---

## 🚀 Getting Started

1. Create your wildcard files in the `/wildcards/` directory
2. Reference them in your prompt templates using `__filename__` syntax
3. Use the dashboard to preview and test your wildcard combinations
4. Generate batches with varied, dynamic prompts

For more information, see the main README.md file or check the sample configurations in the `/configs/` directory. 