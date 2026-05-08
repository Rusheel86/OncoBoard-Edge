# Design Tokens & Medical UI System

**Version**: 1.0  
**Status**: Specification for OncoBoard-Edge Phase 11 UI Polish  
**Date**: May 2026  

---

## Overview

This document defines the visual design language for OncoBoard-Edge. All UI components should follow these tokens for consistency, accessibility, and medical-grade professionalism.

---

## Color Palette

### Primary Medical Blues
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Clinical Blue** | `#1E88E5` | 30, 136, 229 | Primary actions, headers, links |
| **Lighter Blue** | `#42A5F5` | 66, 165, 245 | Hover states, secondary actions |
| **Darker Blue** | `#1565C0` | 21, 101, 192 | Active states, focus rings |

### Semantic Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Success Green** | `#4CAF50` | 76, 175, 80 | High confidence (>0.7), OK status |
| **Warning Amber** | `#FF9800` | 255, 152, 0 | Medium confidence (0.5-0.7), caution |
| **Danger Red** | `#F44336` | 244, 67, 54 | Low confidence (<0.5), critical alerts |
| **Info Cyan** | `#00BCD4` | 0, 188, 212 | Information, neutral status |

### Neutral Grays
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Text Primary** | `#1A1A1A` | 26, 26, 26 | Body text, high contrast |
| **Text Secondary** | `#666666` | 102, 102, 102 | Secondary text, labels |
| **Text Tertiary** | `#999999` | 153, 153, 153 | Disabled, placeholders |
| **Background Light** | `#F8F8F8` | 248, 248, 248 | Page background, light surfaces |
| **Background Medium** | `#F0F0F0` | 240, 240, 240 | Cards, panels, subtle backgrounds |
| **Border Light** | `#E0E0E0` | 224, 224, 224 | Dividers, subtle borders |
| **Border Medium** | `#CCCCCC` | 204, 204, 204 | Component borders, input borders |

### Clinical Accent Colors
| Name | Hex | Purpose |
|------|-----|---------|
| **Biomarker Highlight** | `#FFE082` | Highlight biomarker findings |
| **Critical Finding** | `#EF5350` | Red flag warnings |
| **Recommendation** | `#66BB6A` | Actionable recommendations |

---

## Typography

### Font Stack
```css
/* System sans-serif, medical-grade readability */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
             "Helvetica Neue", Arial, sans-serif;
```

**Rationale**: System fonts render natively on all devices, ensure accessibility, and feel professional.

### Font Sizes & Line Heights

| Scale | Size | Line Height | Usage |
|-------|------|-------------|-------|
| **XL** | 32px | 1.2 | Page titles, H1 |
| **LG** | 24px | 1.3 | Section titles, H2 |
| **MD** | 18px | 1.4 | Subsection, H3, labels |
| **Base** | 16px | 1.5 | Body text, input fields |
| **SM** | 14px | 1.5 | Secondary text, captions |
| **XS** | 12px | 1.6 | Metadata, timestamps |

### Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| Regular | 400 | Body text, paragraphs |
| Medium | 500 | Labels, secondary emphasis |
| Semibold | 600 | Subheadings, badges |
| Bold | 700 | Headings, critical text |

### Line Length & Readability
- **Max line length**: 65-75 characters (optimal for reading)
- **Paragraph spacing**: 1.5x font size (24px for 16px base)
- **Letter spacing**: 0.3px for uppercase labels

---

## Spacing System

**8px Grid Unit** — All spacing derives from multiples of 8px

| Token | Value | Usage |
|-------|-------|-------|
| **xs** | 4px | Minimal spacing (icon margins) |
| **sm** | 8px | Compact spacing (input padding) |
| **md** | 16px | Default spacing (section margins) |
| **lg** | 24px | Large spacing (card margins) |
| **xl** | 32px | Extra large (page margins) |
| **2xl** | 48px | Section separation |

### Common Spacing Patterns
```css
/* Card padding */
padding: 24px;

/* Section margins */
margin-bottom: 32px;

/* Component gaps */
gap: 16px;

/* Input padding */
padding: 12px 16px;  /* 1.5x sm + 2x sm */
```

---

## Component Styles

### Buttons

**Primary Button** (Clinical Blue)
```css
background: #1E88E5;
color: white;
padding: 12px 24px;
border-radius: 6px;
font-weight: 600;
border: none;
cursor: pointer;
transition: background 0.2s;

&:hover {
  background: #42A5F5;
}

&:active {
  background: #1565C0;
}

&:focus {
  outline: 2px solid #1565C0;
  outline-offset: 2px;
}
```

**Secondary Button** (Light border)
```css
background: transparent;
color: #1E88E5;
padding: 12px 24px;
border: 2px solid #1E88E5;
border-radius: 6px;
font-weight: 600;
cursor: pointer;
transition: all 0.2s;

&:hover {
  background: rgba(30, 136, 229, 0.1);
}
```

**Disabled State**
```css
opacity: 0.5;
cursor: not-allowed;
```

### Cards & Panels

**Base Card**
```css
background: white;
border: 1px solid #E0E0E0;
border-radius: 8px;
padding: 24px;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
transition: box-shadow 0.2s;

&:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}
```

**Evidence Card** (Research citation)
```css
background: #F8F8F8;
border-left: 4px solid #1E88E5;
border-radius: 4px;
padding: 16px;
margin-bottom: 12px;

.evidence-source {
  font-size: 12px;
  color: #666666;
  font-weight: 500;
}

.evidence-quote {
  margin-top: 8px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  font-style: italic;
  font-size: 14px;
  line-height: 1.6;
}

.evidence-score {
  display: inline-block;
  margin-top: 8px;
  font-size: 12px;
  color: #666666;
}
```

**Warning/Alert Card**
```css
background: #FFF3E0;
border-left: 4px solid #FF9800;
border-radius: 4px;
padding: 16px;

.alert-title {
  font-weight: 600;
  color: #E65100;
  margin-bottom: 8px;
}

.alert-text {
  color: #666666;
  font-size: 14px;
}
```

### Badges & Confidence Indicators

**Confidence Badge** (Color-coded, inline)
```css
display: inline-flex;
align-items: center;
gap: 4px;
padding: 6px 12px;
border-radius: 12px;
font-size: 12px;
font-weight: 600;
text-transform: uppercase;

/* HIGH (>0.7) */
&.confidence-high {
  background: #E8F5E9;
  color: #2E7D32;
  border: 1px solid #4CAF50;
}

/* MEDIUM (0.5-0.7) */
&.confidence-medium {
  background: #FFF3E0;
  color: #E65100;
  border: 1px solid #FF9800;
}

/* LOW (<0.5) */
&.confidence-low {
  background: #FFEBEE;
  color: #C62828;
  border: 1px solid #F44336;
}

/* UNKNOWN */
&.confidence-unknown {
  background: #F5F5F5;
  color: #616161;
  border: 1px solid #CCCCCC;
}
```

### Loading States

**Progress Bar** (Indeterminate)
```css
.progress-bar {
  width: 100%;
  height: 4px;
  background: #E0E0E0;
  border-radius: 2px;
  overflow: hidden;

  .progress-fill {
    height: 100%;
    background: linear-gradient(
      90deg,
      #1E88E5 0%,
      #42A5F5 50%,
      #1E88E5 100%
    );
    background-size: 200% 100%;
    animation: progress-animation 1.5s ease-in-out infinite;
  }
}

@keyframes progress-animation {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

**Stage Label** (During analysis)
```css
.stage-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #1E88E5;
  font-weight: 500;

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid #E0E0E0;
    border-top-color: #1E88E5;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### Input Fields

**Text Input / Textarea**
```css
padding: 12px 16px;
font-size: 16px;
border: 2px solid #E0E0E0;
border-radius: 6px;
font-family: inherit;
transition: border-color 0.2s, box-shadow 0.2s;

&:focus {
  border-color: #1E88E5;
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
  outline: none;
}

&:hover:not(:focus) {
  border-color: #CCCCCC;
}

&:disabled {
  background: #F5F5F5;
  color: #999999;
  cursor: not-allowed;
}
```

**File Upload Dropzone**
```css
border: 2px dashed #1E88E5;
border-radius: 8px;
padding: 32px 16px;
text-align: center;
background: rgba(30, 136, 229, 0.02);
transition: all 0.2s;
cursor: pointer;

&:hover {
  border-color: #42A5F5;
  background: rgba(30, 136, 229, 0.05);
}

&.drag-active {
  border-color: #1E88E5;
  background: rgba(30, 136, 229, 0.1);
}

.upload-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: #666666;
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 12px;
  color: #999999;
}
```

---

## Layout & Responsive Design

### Breakpoints

```css
$mobile: 375px;    /* Small phones */
$tablet: 768px;    /* Tablets, large phones */
$desktop: 1024px;  /* Desktops */
$large: 1440px;    /* Large displays */
```

### Grid System

**12-column grid on desktop**
```css
@media (min-width: 1024px) {
  .container {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 24px;
    max-width: 1440px;
    margin: 0 auto;
  }

  .sidebar { grid-column: span 4; }
  .main { grid-column: span 8; }
}
```

**2-column on tablet**
```css
@media (min-width: 768px) and (max-width: 1023px) {
  .container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}
```

**Single column on mobile**
```css
@media (max-width: 767px) {
  .container {
    display: block;
  }

  .sidebar, .main {
    width: 100%;
    margin-bottom: 16px;
  }
}
```

### Mobile-Specific Considerations
- **Touch targets**: Minimum 48x48px for buttons/interactive elements
- **Font sizes**: Base 16px minimum (prevents iOS auto-zoom)
- **Padding**: Increase to 16px on mobile (easier to tap)
- **Labels**: Full-width on mobile, inline on desktop
- **File upload**: Large touch area, clear drag-drop indicator

---

## Accessibility (WCAG 2.1 AA)

### Color Contrast
- **Text**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Components**: All interactive elements must be distinguishable without color alone

### Semantic HTML
```html
<!-- Good -->
<button>Submit</button>
<label for="patient-id">Patient ID:</label>
<input id="patient-id" type="text" />

<!-- Avoid -->
<div onclick="submit()">Submit</div>
```

### ARIA Labels
```html
<!-- Loading indicator -->
<div role="status" aria-live="polite" aria-label="Analysis in progress">
  Parsing pathology...
</div>

<!-- Alert/Warning -->
<div role="alert" class="alert">
  Critical finding: Needs urgent follow-up
</div>

<!-- Expandable section -->
<button aria-expanded="false" aria-controls="evidence-panel">
  View Evidence
</button>
<div id="evidence-panel" hidden>...</div>
```

### Keyboard Navigation
- **Tab order**: Logical left-to-right, top-to-bottom
- **Focus indicator**: Always visible (2px outline)
- **Escape key**: Close modals/expandables
- **Enter key**: Submit forms/trigger actions

---

## Dark Mode (Future)

**CSS Variables for Light/Dark Toggle**
```css
:root {
  /* Light mode (default) */
  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F8F8F8;
  --color-text-primary: #1A1A1A;
  --color-text-secondary: #666666;
  --color-border: #E0E0E0;
  --color-primary: #1E88E5;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #1A1A1A;
    --color-bg-secondary: #2A2A2A;
    --color-text-primary: #FFFFFF;
    --color-text-secondary: #CCCCCC;
    --color-border: #444444;
  }
}

/* Usage */
body {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}
```

---

## Medical UI Patterns

### Confidence Hierarchy
```
HIGH confidence (>0.7):      🟢 GREEN — trust the recommendation
MEDIUM confidence (0.5-0.7): 🟡 YELLOW — use with clinical judgment
LOW confidence (<0.5):       🔴 RED — treat as exploratory
```

### Evidence Citation Pattern
```
📄 Pathology Report — NSCLC Screening Guidelines (Page 3, Score: 0.89)
"Adenocarcinoma with KRAS mutation warrants targeted therapy..."
← Clickable to expand full context
```

### Red Flag / Critical Finding
```
🚨 CRITICAL: PD-L1 <1% and high tumor burden — recommend urgent oncology review
```

### Biomarker Highlighting
```
Key Biomarkers:
├─ HER2: IHC 3+ ✓ (actionable)
├─ ER: Positive ✓ (hormone therapy eligible)
├─ PR: Negative ⚠ (atypical for luminal)
└─ MSI: Not performed ❌ (needs testing)
```

---

## Implementation Notes

### Gradio-Specific Considerations

Gradio uses automatic styling; override with custom CSS:

```python
# In Gradio build_ui():
with gr.Blocks(css=open('ui/style.css').read()) as demo:
    # Components automatically use CSS classes
    gr.Markdown("<h1>OncoBoard-Edge</h1>")
    # Style applies to .markdown-text, h1, etc.
```

**Gradio CSS Classes** (automatically applied):
- `.gradio-container` — main wrapper
- `.gradio-block` — component wrapper
- `.input` — input fields
- `.gr-button` — buttons
- `.gr-markdown` — markdown content
- `.gr-code` — code blocks
- `.gr-textbox`, `.gr-textarea`, `.gr-slider`, etc.

### Testing Accessibility

```bash
# Install axe DevTools browser extension
# Run Lighthouse audit in Chrome DevTools
# Test keyboard navigation (Tab, Enter, Escape)
# Verify color contrast with WCAG Contrast Checker
```

---

## References

- **WCAG 2.1 Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **Material Design Colors**: https://material.io/design/color/
- **System Font Stack**: https://systemfontstack.com/
- **Medical UI Best Practices**: Human-Computer Interaction in Healthcare (Shneiderman & Plaisant)

