# Design Examples

Real-world examples of distinctive frontend designs across different aesthetic directions.

## Brutally Minimal Portfolio

**Context**: Designer portfolio showcasing work

**Aesthetic choices:**
- Pure black (#000) and white (#FFF)
- Helvetica Neue (ironically used well here)
- 90% negative space
- Single column, massive type
- No images in hero, just typography

**Key code:**
```css
:root {
  --fg: #000;
  --bg: #FFF;
}

.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 0 10vw;
}

.hero h1 {
  font-size: clamp(3rem, 10vw, 8rem);
  font-weight: 300;
  letter-spacing: -0.02em;
  line-height: 0.9;
}
```

**Why it works**: Restraint creates sophistication. The lack of decoration makes each typographic choice powerful.

---

## Maximalist Music Festival

**Context**: Electronic music festival landing page

**Aesthetic choices:**
- Neon colors: hot pink, cyan, yellow, lime green
- 5 different fonts mixing
- Overlapping sections with blend modes
- Rotating elements, glitch effects
- Video backgrounds with color overlays

**Key code:**
```css
:root {
  --neon-pink: #ff006e;
  --neon-cyan: #00f5ff;
  --neon-yellow: #ffbe0b;
  --neon-lime: #8ac926;
}

.section {
  mix-blend-mode: screen;
  position: relative;
  transform: rotate(-2deg);
}

.glitch-text {
  animation: glitch 0.3s infinite;
  text-shadow: 
    2px 2px var(--neon-cyan),
    -2px -2px var(--neon-pink);
}

@keyframes glitch {
  0%, 100% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(2px, -2px); }
  60% { transform: translate(-2px, -2px); }
  80% { transform: translate(2px, 2px); }
}
```

**Why it works**: Total commitment to chaos. Everything is intentionally over-the-top, creating energy and excitement.

---

## Organic Wellness Brand

**Context**: Holistic wellness product site

**Aesthetic choices:**
- Earth tones: sage, terracotta, cream, olive
- Crimson Text (serif) + Source Sans Pro
- Soft shadows, no harsh lines
- Paper texture overlay
- Hand-drawn SVG illustrations
- Smooth scroll animations

**Key code:**
```css
:root {
  --sage: #87a96b;
  --terracotta: #c97064;
  --cream: #fefae0;
  --olive: #6a7560;
}

body {
  background: var(--cream);
  color: var(--olive);
  background-image: url('data:image/svg+xml,...paper texture...');
}

.card {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(8px);
}

.illustration {
  filter: drop-shadow(0 2px 8px rgba(106, 117, 96, 0.15));
}
```

**Why it works**: Every choice reinforces the natural, calming brand. Soft edges and organic colors create harmony.

---

## Luxury Fashion E-commerce

**Context**: High-end fashion brand

**Aesthetic choices:**
- Monochrome: black, white, one gold accent
- Bodoni (elegant serif) for headings
- Massive product imagery
- Minimal UI chrome
- Sophisticated hover effects
- Generous whitespace

**Key code:**
```css
:root {
  --black: #1a1a1a;
  --white: #fefefe;
  --gold: #d4af37;
}

.product-card {
  position: relative;
  overflow: hidden;
}

.product-image {
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

.add-to-cart {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  transform: translateY(100%);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--gold);
  color: var(--black);
  border: none;
  padding: 16px;
  font-size: 11px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.product-card:hover .add-to-cart {
  transform: translateY(0);
}
```

**Why it works**: Restraint signals luxury. Limited color palette and perfect spacing create premium feel.

---

## Playful SaaS Dashboard

**Context**: Project management tool

**Aesthetic choices:**
- Bright colors: coral, mint, lavender, sunshine yellow
- Rounded corners everywhere (16-24px)
- Bouncy animations
- Illustrated empty states
- Soft shadows (neumorphism lite)

**Key code:**
```css
:root {
  --coral: #ff6b6b;
  --mint: #51cf66;
  --lavender: #a78bfa;
  --sunshine: #ffd43b;
  --bg: #f8f9fa;
}

.button {
  border-radius: 12px;
  padding: 12px 24px;
  border: none;
  background: var(--coral);
  color: white;
  font-weight: 600;
  box-shadow: 
    0 4px 12px rgba(255, 107, 107, 0.3),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(255, 107, 107, 0.4),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1);
}

.button:active {
  transform: translateY(0);
}

.card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.04),
    0 0 0 1px rgba(0, 0, 0, 0.02);
}

@keyframes bounce-in {
  0% {
    transform: scale(0.95);
    opacity: 0;
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.task-item {
  animation: bounce-in 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

**Why it works**: Playful aesthetics reduce anxiety around work tools. Bright colors and animations make tasks feel lighter.

---

## Brutalist Tech Blog

**Context**: Developer blog, experimental

**Aesthetic choices:**
- Harsh colors: pure black, white, one accent (lime green)
- System monospace font
- Exposed grid structure
- No images, only ASCII art
- Raw HTML aesthetic

**Key code:**
```css
:root {
  --black: #000;
  --white: #fff;
  --lime: #00ff00;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Courier New', monospace;
  background: var(--white);
  color: var(--black);
  border: 4px solid var(--black);
  min-height: 100vh;
}

.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 0;
  border: 2px solid var(--black);
}

.grid > * {
  border: 1px solid var(--black);
  padding: 16px;
}

a {
  color: var(--lime);
  text-decoration: none;
  border-bottom: 2px solid var(--lime);
}

a:hover {
  background: var(--lime);
  color: var(--black);
}

pre {
  background: var(--black);
  color: var(--lime);
  padding: 16px;
  overflow-x: auto;
}
```

**Why it works**: Aggressive rejection of "nice" design makes a statement. Appeals to developer aesthetic and counterculture.

---

## Art Deco Event Site

**Context**: Gatsby-themed gala invitation

**Aesthetic choices:**
- Gold (#d4af37), navy (#1e3a5f), emerald (#2d6a4f)
- Geometric patterns, zigzags
- Custom art deco display font
- Symmetrical layouts
- Metallic gradients

**Key code:**
```css
:root {
  --gold: #d4af37;
  --navy: #1e3a5f;
  --emerald: #2d6a4f;
}

body {
  background: var(--navy);
  color: var(--gold);
}

.art-deco-border {
  border-image: repeating-linear-gradient(
    45deg,
    var(--gold),
    var(--gold) 10px,
    transparent 10px,
    transparent 20px
  ) 1;
  border-width: 4px;
  border-style: solid;
  padding: 40px;
}

.gold-gradient-text {
  background: linear-gradient(
    135deg,
    #d4af37 0%,
    #f9e79f 50%,
    #d4af37 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 4rem;
  font-weight: 700;
  text-align: center;
}

.geometric-pattern {
  background-image: 
    linear-gradient(30deg, var(--gold) 12%, transparent 12.5%, transparent 87%, var(--gold) 87.5%),
    linear-gradient(150deg, var(--gold) 12%, transparent 12.5%, transparent 87%, var(--gold) 87.5%);
  background-size: 40px 60px;
  opacity: 0.1;
}
```

**Why it works**: Cohesive visual language from a specific era. Every element references Art Deco design principles.

---

## Common Patterns

### Successful Designs Share:

1. **Clear aesthetic commitment** - Not mixing incompatible styles
2. **Consistent execution** - Every detail reinforces the direction
3. **Appropriate complexity** - Match code effort to aesthetic ambition
4. **Context awareness** - Design fits the purpose and audience
5. **Technical polish** - Clean code, smooth animations, attention to detail

### Differentiation Techniques:

- **Custom fonts** - Not default system fonts
- **Unexpected color palettes** - Avoid common combinations
- **Unique layouts** - Break from standard patterns
- **Signature element** - One memorable distinctive feature
- **Atmospheric details** - Textures, effects that create mood

---

## See Also

- [references/aesthetics.md](aesthetics.md) - Comprehensive aesthetic guidelines
- [references/anti-patterns.md](anti-patterns.md) - What not to do
