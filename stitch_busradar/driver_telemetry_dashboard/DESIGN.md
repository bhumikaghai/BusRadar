---
name: LogiCode OLED Dark
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
  on-surface-variant: '#bccabb'
  inverse-surface: '#e2e2e2'
  inverse-on-surface: '#303030'
  outline: '#869486'
  outline-variant: '#3d4a3e'
  surface-tint: '#4de082'
  primary: '#6bfb9a'
  on-primary: '#003919'
  primary-container: '#4ade80'
  on-primary-container: '#005e2d'
  inverse-primary: '#006d36'
  secondary: '#c8c5ca'
  on-secondary: '#303033'
  secondary-container: '#47464a'
  on-secondary-container: '#b6b4b8'
  tertiary: '#ffdc96'
  on-tertiary: '#402d00'
  tertiary-container: '#f6bb1f'
  on-tertiary-container: '#684c00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6dfe9c'
  primary-fixed-dim: '#4de082'
  on-primary-fixed: '#00210c'
  on-primary-fixed-variant: '#005227'
  secondary-fixed: '#e4e1e6'
  secondary-fixed-dim: '#c8c5ca'
  on-secondary-fixed: '#1b1b1e'
  on-secondary-fixed-variant: '#47464a'
  tertiary-fixed: '#ffdf9f'
  tertiary-fixed-dim: '#f9bd22'
  on-tertiary-fixed: '#261a00'
  on-tertiary-fixed-variant: '#5c4300'
  background: '#131313'
  on-background: '#e2e2e2'
  surface-variant: '#353535'
typography:
  metric-hero:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 52px
    letterSpacing: -0.02em
  metric-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 36px
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 26px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.1em
  metric-hero-mobile:
    fontFamily: Space Grotesk
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 44px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  touch-target-min: 56px
  gutter: 1rem
  margin-edge: 1.25rem
  stack-gap: 0.75rem
  inset-card: 1.5rem
---

## Brand & Style
The design system is engineered for mission-critical industrial environments where glanceability and rapid interaction are paramount. It centers on a **High-Contrast / Modern** aesthetic specifically optimized for OLED displays to minimize power consumption and reduce driver eye strain during night shifts. 

The personality is authoritative, precise, and utilitarian. Every visual element serves a functional purpose, utilizing a "Night-Vision" philosophy where critical telemetry data is separated from secondary information through extreme tonal contrast and neon signaling. The interface leverages tactile metaphors, providing high-visibility feedback loops for drivers operating in high-vibration or low-light scenarios.

## Colors
The palette is built on a "True Black" foundation to achieve infinite contrast ratios. 

- **Master Background:** Pure Black (#000000) to ensure zero light emission from unused pixels.
- **Surface Layer:** Elevated Charcoal (#18181b) for container surfaces to provide a subtle visual break from the pitch-black background.
- **Telemetry Primary:** Neon Green (#4ade80) reserved strictly for active, healthy telemetry metrics and primary action states.
- **Alert Tiers:** Amber (#fbbf24) for cautionary data, Orange (#fb923c) for non-critical incidents, and Crimson Red (#dc2626) for Emergency/SOS functions only.
- **Typography:** Stark White (#ffffff) for data values; Muted Slate (#94a3b8) for auxiliary labeling to reduce cognitive load.

## Typography
The typographic scale emphasizes "Glanceable Data." 

- **Headlines & Metrics:** Uses **Space Grotesk** for its technical, geometric clarity. Large-scale metrics use tight tracking and bold weights to ensure visibility from an arm's length (the typical driver-to-dashboard distance).
- **Body & Controls:** **Hanken Grotesk** provides a clean, contemporary sans-serif experience for status updates and logs.
- **Technical Labels:** **JetBrains Mono** is utilized for metadata, timestamps, and secondary labels to evoke a precise, instrument-cluster feel. All labels should be uppercase with increased letter spacing to prevent character blurring at low brightness.

## Layout & Spacing
This design system employs a **Fluid Grid** optimized for landscape-oriented mobile or tablet mounting. 

- **Touch Safety:** Every interactive element must adhere to a minimum 56px touch target to account for vibrations and rapid "no-look" interactions.
- **Rhythm:** An 8px base unit drives the spacing logic. 
- **Mobile-First Constraints:** On mobile, the layout stacks vertically with a single primary metric hero. On tablet, a 2-column dashboard view is preferred to separate "Driving Metrics" (Left) from "Route/Logistics" (Right).
- **Margins:** Generous outer margins (20px) ensure content is not obscured by physical device bezels or mounting brackets.

## Elevation & Depth
In an OLED-first environment, depth is communicated through **Tonal Layers** and **Bold Borders** rather than soft shadows, which can cause "smearing" on certain panel types.

- **Surface Tiering:** The background is #000000. Interactive cards are #18181b.
- **Structural Outlines:** Surfaces are defined by 1px solid borders (#27272a). This creates a "grid" feel that helps the driver map the interface mentally.
- **Active State Depth:** When a component is pressed, it should scale down (98%) and the border color should shift to the Primary Neon Green. This "Tactile Scale" provides immediate feedback that the system has registered the touch.

## Shapes
The design system uses **Soft (0.25rem)** roundedness to maintain an industrial, rigid feel while avoiding the harshness of sharp corners.

- **Primary Cards:** Use `rounded-lg` (0.5rem) to differentiate the main container from smaller nested UI elements.
- **Action Buttons:** Use `rounded-lg` for standard actions; however, the **SOS/Emergency** button is a perfect circle to provide a distinct tactile and visual shape-differentiation.

## Components
- **Metrics Cards:** Heavy-weight numeric values top-aligned, with the JetBrains Mono label at the bottom. The background remains #18181b unless in an alert state.
- **High-Visibility Buttons:** Minimum height 56px. Ghost buttons (borders only) are used for secondary actions. Solid #4ade80 backgrounds are reserved for the "Finish Route" or "Start Shift" primary actions.
- **Telemetry Bars:** Horizontal progress bars for fuel, battery, or speed. Use a 12px height for the track to ensure high visibility. Background track is #27272a.
- **Incident Chips:** Small, high-contrast badges used in logs. Amber for "Late", Orange for "Traffic", Red for "Mechanical".
- **Input Fields:** Large text inputs with #27272a borders. Focus state swaps the border to #4ade80 and increases border-width to 2px.
- **SOS Button:** A persistent, fixed-position Crimson Red button. It must require a "Long Press" (2 seconds) to activate, visualized by a radial progress fill around the circle.