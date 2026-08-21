---
name: Luminescent Precision
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1b1b1b'
  surface-container: '#1f1f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353535'
  on-surface: '#e2e2e2'
  on-surface-variant: '#baccb0'
  inverse-surface: '#e2e2e2'
  inverse-on-surface: '#303030'
  outline: '#85967c'
  outline-variant: '#3c4b35'
  surface-tint: '#2ae500'
  primary: '#efffe3'
  on-primary: '#053900'
  primary-container: '#39ff14'
  on-primary-container: '#107100'
  inverse-primary: '#106e00'
  secondary: '#c8c6c5'
  on-secondary: '#313030'
  secondary-container: '#4a4949'
  on-secondary-container: '#bab8b7'
  tertiary: '#efffe4'
  on-tertiary: '#253421'
  tertiary-container: '#d1e3c6'
  on-tertiary-container: '#56664f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#79ff5b'
  primary-fixed-dim: '#2ae500'
  on-primary-fixed: '#022100'
  on-primary-fixed-variant: '#095300'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474646'
  tertiary-fixed: '#d6e8cb'
  tertiary-fixed-dim: '#baccb0'
  on-tertiary-fixed: '#111f0d'
  on-tertiary-fixed-variant: '#3b4b36'
  background: '#131313'
  on-background: '#e2e2e2'
  surface-variant: '#353535'
typography:
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.1em
  label-mono:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style

This design system is engineered for professional drivers and hardware operators who require high-visibility interfaces in low-light environments. The aesthetic sits at the intersection of **High-Contrast Minimalism** and **Cyber-Tech**, prioritizing legibility and status awareness above all else.

The visual language utilizes a "Pure Dark" strategy to leverage OLED power savings and infinite contrast ratios. It features vibrant neon accents that pierce through a charcoal-layered hierarchy. Interaction design focuses on tactical precision, using subtle glows and razor-sharp borders to indicate focus and state changes, ensuring the interface feels like an integrated piece of high-performance hardware.

## Colors

The palette is optimized for OLED hardware, focusing on the preservation of true blacks to reduce eye strain and power consumption.

- **Primary (Neon Green):** Reserved for critical actions, active states, and success indicators. It is the singular source of light in the UI.
- **Secondary (Elevated Charcoal):** Used for surface containment to create a perceptible hierarchy above the pure black floor.
- **Muted (Green-Gray):** Applied to secondary information and inactive states to maintain brand harmony while reducing visual noise.
- **Background (Pure Black):** The foundation of every screen, providing maximum contrast for the neon accents.

## Typography

The typography system utilizes two distinct sans-serifs to balance personality and technical utility. 

- **Hanken Grotesk** is the primary typeface for headlines and body copy, providing a contemporary, sharp look that remains highly legible at various scales. 
- **Geist** is used for labels, metadata, and status readouts. Its technical, monospaced-adjacent proportions provide the "driver dashboard" feel essential for data-heavy views.

For mobile layouts, headline sizes are scaled down to ensure critical information remains visible above the fold without excessive scrolling. Use `label-caps` for all-caps section headers to create clear vertical rhythm.

## Layout & Spacing

This design system uses a strict **4px baseline grid** to ensure mathematical precision in all component alignments. 

- **Grid Model:** A 12-column fluid grid for desktop and a 4-column fluid grid for mobile.
- **Margins:** 16px safe-area margins for mobile devices; 32px for tablet and desktop.
- **Density:** High-density layouts are preferred. Use `16px (md)` padding for most card containers to maximize data display area.
- **Reflow:** On mobile, side-by-side card elements should stack vertically unless they represent small metric tiles (e.g., speed, battery), which may stay in a 2-column grid.

## Elevation & Depth

In a pure black environment, traditional shadows are ineffective. Depth is instead communicated through **Tonal Layering** and **Stroke Illumination**:

1.  **Level 0 (Base):** Pure Black (#000000). Reserved for the application background.
2.  **Level 1 (Surface):** Elevated Charcoal (#131313). Used for cards, navigation bars, and inputs.
3.  **Level 2 (Interaction):** Surface strokes. Active or focused elements receive a 1px solid border of Neon Green (#39FF14).
4.  **The Glow:** Active components (like toggles or primary buttons) should feature a subtle outer glow (box-shadow) using the Primary Accent color with a 15-20px blur at low opacity (20%) to simulate a hardware light source.

## Shapes

The shape language is defined by **rounded-2xl** geometry, providing a sophisticated, modern feel that softens the high-contrast color palette.

- **Large Containers:** Use `rounded-xl` (1.5rem) for main cards and modals.
- **Standard Components:** Use `rounded-lg` (1rem) for buttons, input fields, and chips.
- **Small Elements:** Use `rounded` (0.5rem) for checkboxes and tooltips.

This consistent radius creates a "encapsulated" feel for data points, making the UI feel like a series of modules docked into a main terminal.

## Components

### Buttons
- **Primary:** Solid Neon Green background with Pure Black text. On hover, apply a 10px outer glow.
- **Secondary:** Ghost style. 1px Neon Green border with White text. Pure Black background.
- **Tertiary:** Pure Black background, Muted Green-Gray text. No border.

### Cards & Surfaces
All cards utilize Elevated Charcoal (#131313). For interactive cards, the border should transition from transparent to a 1px Muted Green-Gray stroke on hover, and Neon Green on selection.

### Inputs & Form Fields
Fields should be Elevated Charcoal with White text. The label should use `label-caps` in Muted Green-Gray. The focus state must use a Neon Green border and a soft glow.

### Status Indicators (Chips)
Small, pill-shaped elements. Active status uses Neon Green text with a 10% opacity Neon Green background. Inactive uses Muted Green-Gray.

### Data Visualizations
Charts and graphs should exclusively use Neon Green for data lines. Use Muted Green-Gray for grid lines and axes to ensure the data is the primary focal point.