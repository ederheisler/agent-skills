# Anti-Patterns: What NOT to Do

Examples of generic, uninspired frontend design choices and how to fix them.

## Generic AI Slop: The Prototype

This is what **not** to build - the stereotypical AI-generated interface that lacks character.

### The Anti-Pattern Site

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    * {
      font-family: 'Inter', sans-serif;
    }
    
    body {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #333;
    }
    
    .hero {
      text-align: center;
      padding: 80px 20px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    h1 {
      font-size: 48px;
      margin-bottom: 16px;
    }
    
    p {
      font-size: 18px;
      color: #666;
      margin-bottom: 32px;
    }
    
    button {
      background: #667eea;
      color: white;
      border: none;
      border-radius: 8px;
      padding: 12px 24px;
      font-size: 16px;
      cursor: pointer;
    }
    
    .features {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
      padding: 80px 20px;
    }
    
    .card {
      background: white;
      padding: 24px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="hero">
    <h1>Welcome to Our Product</h1>
    <p>The best solution for your needs</p>
    <button>Get Started</button>
  </div>
  
  <div class="features">
    <div class="card">
      <h3>Feature One</h3>
      <p>Description of feature</p>
    </div>
    <div class="card">
      <h3>Feature Two</h3>
      <p>Description of feature</p>
    </div>
    <div class="card">
      <h3>Feature Three</h3>
      <p>Description of feature</p>
    </div>
  </div>
</body>
</html>
```

### Why This Fails

❌ **Inter font** - Most overused AI default
❌ **Purple gradient** - Clichéd background
❌ **8px border-radius** - Generic rounded corners everywhere
❌ **Centered hero** - Predictable layout
❌ **Generic shadows** - Same `0 2px 4px rgba(0,0,0,0.1)` everywhere
❌ **Three-card feature grid** - Cookie-cutter pattern
❌ **No personality** - Could be for any product
❌ **Boring copy** - "Welcome to Our Product"

---

## Anti-Pattern Breakdown

### 1. Overused Fonts

**DON'T:**
```css
font-family: 'Inter', sans-serif;
font-family: 'Roboto', sans-serif;
font-family: -apple-system, system-ui, sans-serif;
font-family: 'Space Grotesk', sans-serif;
```

**DO:**
```css
/* Pick something with character */
font-family: 'Playfair Display', serif;
font-family: 'Bebas Neue', sans-serif;
font-family: 'DM Serif Display', serif;
font-family: 'Archivo Black', sans-serif;
```

---

### 2. Cliché Color Schemes

**DON'T:**
```css
/* Purple gradient (AI favorite) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Generic blue */
--primary: #007bff;

/* Washed pastels */
--pink: #ffc0cb;
--blue: #add8e6;
```

**DO:**
```css
/* Commit to a direction */

/* Bold retro */
--primary: #ff006e;
--secondary: #8338ec;
--accent: #ffbe0b;

/* Natural organic */
--primary: #2d6a4f;
--secondary: #52b788;
--accent: #d4a373;

/* Monochrome with punch */
--primary: #000000;
--accent: #00ff00;
```

---

### 3. Same Border-Radius Everywhere

**DON'T:**
```css
.everything {
  border-radius: 8px; /* The AI special */
}
```

**DO:**
```css
/* Vary based on element and aesthetic */

/* Brutalist: none */
.brutalist {
  border-radius: 0;
}

/* Playful: generous */
.playful {
  border-radius: 24px;
}

/* Mixed: intentional variation */
.cards {
  border-radius: 16px;
}

.buttons {
  border-radius: 32px;
}

.badges {
  border-radius: 4px;
}
```

---

### 4. Predictable Layouts

**DON'T:**
```html
<div style="text-align: center;">
  <h1>Centered Title</h1>
  <p>Centered text</p>
  <button>Centered Button</button>
</div>
```

**DO:**
```html
<!-- Asymmetric -->
<div style="display: grid; grid-template-columns: 60% 40%;">
  <div>
    <h1>Title aligned left</h1>
    <p>Text creates visual weight on one side</p>
    <button>Action</button>
  </div>
  <div>
    <img src="..." alt="Visual balance" />
  </div>
</div>

<!-- Diagonal flow -->
<div style="transform: rotate(-2deg); margin: 40px 0;">
  <h2>Breaking the grid</h2>
</div>

<!-- Overlapping -->
<div style="position: relative;">
  <img style="width: 100%;" />
  <div style="position: absolute; bottom: -50px; left: 50px;">
    <div class="card">Overlapping card</div>
  </div>
</div>
```

---

### 5. Generic Shadows

**DON'T:**
```css
box-shadow: 0 2px 4px rgba(0,0,0,0.1);
```

**DO:**
```css
/* Layered depth */
box-shadow: 
  0 2px 4px rgba(0,0,0,0.05),
  0 8px 16px rgba(0,0,0,0.1),
  0 16px 32px rgba(0,0,0,0.15);

/* Colored shadows */
box-shadow: 0 8px 32px rgba(255, 0, 110, 0.3);

/* Dramatic */
box-shadow: 0 20px 60px rgba(0,0,0,0.3);

/* Neumorphism */
box-shadow: 
  8px 8px 16px rgba(0,0,0,0.1),
  -8px -8px 16px rgba(255,255,255,0.8);
```

---

### 6. Cookie-Cutter Component Patterns

**DON'T:**
```html
<!-- Three equal cards -->
<div class="grid-3">
  <div class="card">Feature 1</div>
  <div class="card">Feature 2</div>
  <div class="card">Feature 3</div>
</div>
```

**DO:**
```html
<!-- Varied sizes and layouts -->
<div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 24px;">
  <div class="card-large">Hero feature</div>
  <div class="card-small">Supporting</div>
  <div class="card-small">Supporting</div>
</div>

<!-- Asymmetric -->
<div style="display: grid; grid-template-areas:
  'a a b'
  'c d d'; gap: 24px;">
  <div style="grid-area: a;">Feature A</div>
  <div style="grid-area: b;">Feature B</div>
  <div style="grid-area: c;">Feature C</div>
  <div style="grid-area: d;">Feature D</div>
</div>
```

---

### 7. No Visual Details

**DON'T:**
```css
body {
  background: white;
}
```

**DO:**
```css
/* Textured */
body {
  background: #fefefe;
  background-image: url("data:image/svg+xml,...noise...");
}

/* Gradient mesh */
body {
  background: 
    radial-gradient(at 20% 30%, rgba(255, 0, 110, 0.15) 0px, transparent 50%),
    radial-gradient(at 80% 70%, rgba(131, 56, 236, 0.15) 0px, transparent 50%),
    #ffffff;
}

/* Subtle pattern */
body {
  background-color: #f9f9f9;
  background-image: 
    linear-gradient(30deg, #f0f0f0 12%, transparent 12.5%, transparent 87%, #f0f0f0 87.5%),
    linear-gradient(150deg, #f0f0f0 12%, transparent 12.5%, transparent 87%, #f0f0f0 87.5%);
  background-size: 20px 35px;
}
```

---

### 8. Boring Animations

**DON'T:**
```css
button:hover {
  opacity: 0.8;
}
```

**DO:**
```css
button {
  position: relative;
  overflow: hidden;
  transition: transform 0.2s;
}

button:hover {
  transform: translateY(-2px);
}

/* Ripple effect on click */
button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

button:active::after {
  width: 300px;
  height: 300px;
}
```

---

## Transformation Example

### Before (Generic)

```css
.card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card h3 {
  font-family: 'Inter', sans-serif;
  font-size: 24px;
  color: #333;
  margin-bottom: 16px;
}

.card p {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  color: #666;
  line-height: 1.5;
}
```

### After (Distinctive - Brutalist)

```css
.card {
  background: white;
  border: 4px solid black;
  padding: 32px;
  transform: rotate(-1deg);
  box-shadow: 8px 8px 0 black;
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: rotate(0deg) translateY(-4px);
  box-shadow: 12px 12px 0 black;
}

.card h3 {
  font-family: 'Courier New', monospace;
  font-size: 28px;
  color: black;
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.card p {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: black;
  line-height: 1.6;
  border-left: 4px solid black;
  padding-left: 16px;
}
```

### After (Distinctive - Luxury)

```css
.card {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border: 1px solid rgba(212, 175, 55, 0.2);
  padding: 48px 40px;
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent, 
    #d4af37, 
    transparent
  );
}

.card h3 {
  font-family: 'Bodoni', serif;
  font-size: 32px;
  font-weight: 400;
  color: #d4af37;
  margin-bottom: 20px;
  letter-spacing: 0.05em;
}

.card p {
  font-family: 'Lora', serif;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.8;
  font-weight: 300;
}
```

---

## Red Flags Checklist

When reviewing your design, watch for these warning signs:

- [ ] Using Inter, Roboto, or system fonts
- [ ] Purple gradient background
- [ ] Everything is border-radius: 8px
- [ ] All shadows are `0 2px 4px rgba(0,0,0,0.1)`
- [ ] Hero is centered with generic copy
- [ ] Three equal feature cards
- [ ] Default button styles
- [ ] No atmospheric effects or textures
- [ ] Could swap in any brand name
- [ ] Looks like every other AI-generated site

**If you checked 3+ boxes, start over with a bolder direction.**

---

## See Also

- [references/aesthetics.md](aesthetics.md) - Comprehensive aesthetic guidelines
- [references/examples.md](examples.md) - Real-world examples across aesthetics
