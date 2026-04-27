# ALFRED GUI Refinement — Design Spec
**Date:** 2026-04-26
**Scope:** Full widget-level GUI polish pass (Approach B)
**Status:** Approved

---

## 1. Goal

Elevate ALFRED's GUI from a competent dark-theme app to a genuinely premium "Elevated JARVIS" aesthetic. All five problem areas the user identified — visual design, layout, widget quality, interactions, and animations — are addressed in a single cohesive pass.

## 2. Design Direction: Elevated JARVIS

Keep the existing DNA (dark navy background, cyan accent, frameless window, sidebar-left + chat-right layout) but refine every detail. Reference aesthetic: sophisticated, intentional — closer to a Stark Industries display than a hobbyist project. No layout restructuring; this is purely execution quality.

## 3. Design System Refinements

### 3.1 Color Hierarchy

Cyan (`#00d4ff`) is currently used for almost everything, which flattens hierarchy. The refinement:

| Usage | Current | Proposed |
|---|---|---|
| Primary interactive (active states, focused inputs, send button, Alfred avatar ring) | `#00d4ff` | `#00d4ff` (unchanged) |
| Secondary / informational (system stats, timestamps, inactive icons) | `#00d4ff` | `#0088bb` |
| Alfred bubble background | `#2d2d44` (flat) | `rgba(0, 212, 255, 0.05)` + border `rgba(0, 212, 255, 0.15)` |
| User bubble background | `#0066cc` (solid) | `rgba(0, 102, 204, 0.35)` + border `rgba(0, 136, 255, 0.3)` |
| Background layer 1 (deepest) | `#0a0a14` | `#080812` |
| Background layer 2 (panels) | `#1a1a2e` | `#111122` |
| Background layer 3 (elevated) | `#2d2d44` | `#1e1e32` |
| Sidebar background | same as primary | `#0a0a18` (slightly darker for depth) |

These changes go in `ui/styles/colors.py`. Add new tokens:
- `"accent_cyan_secondary": "#0088bb"` — informational cyan
- `"bubble_alfred_border": "rgba(0, 212, 255, 0.15)"` — Alfred bubble border
- `"bubble_alfred_bg": "rgba(0, 212, 255, 0.05)"` — Alfred bubble fill
- `"bubble_user_border": "rgba(0, 136, 255, 0.3)"` — user bubble border
- `"bubble_user_bg": "rgba(0, 102, 204, 0.35)"` — user bubble fill
- `"bg_sidebar": "#0a0a18"` — sidebar background

### 3.2 Typography Scale

All text currently uses `Segoe UI 10pt` with minimal variation. New scale:

| Element | Font | Size | Weight | Additional |
|---|---|---|---|---|
| Title bar app name | Segoe UI | 10pt | 700 | letter-spacing: 3px |
| Section headers (sidebar) | Segoe UI | 7pt | 700 | uppercase, letter-spacing: 2px |
| Chat sender label | Segoe UI | 7pt | 700 | uppercase, letter-spacing: 2px, very muted |
| Chat message body | Segoe UI | 10.5pt | 400 | line-height: 1.6 |
| Chat timestamp | Consolas | 7pt | 400 | monospace, very dim |
| System stat labels | Segoe UI | 7pt | 400 | uppercase, letter-spacing: 1px |
| System stat values | Consolas | 9pt | 400 | monospace — data reads better in mono |
| Quick action labels | Segoe UI | 8pt | 700 | uppercase, letter-spacing: 0.5px |
| Status bar | Segoe UI | 8pt | 400 | |
| Input placeholder | Segoe UI | 10.5pt | 400 | |

### 3.3 Spacing

- Global content margins: `12px → 10px` (tighter outer gaps)
- Internal widget padding: `8px → 12px` (more breathing room inside each element)
- Chat bubble padding: `10px 12px → 11px 14px`
- Sidebar section gap: add `10px` between System and Quick Access sections

---

## 4. Widget Changes

### 4.1 Title Bar (`ui/widgets/title_bar.py`)

**Changes:**
- Background: `linear-gradient(180deg, #141428 0%, #0f0f20 100%)` replaces flat `#1a1a2e`
- Bottom border: `rgba(0, 212, 255, 0.15)` replaces `#333344`
- Add ALFRED logo: 20×20px circle, dark background, `#00d4ff` border (1.5px), cyan glow (`box-shadow` equivalent via `QGraphicsDropShadowEffect`), letter "A" in cyan
- App name: white `#ffffff`, 10pt bold, letter-spacing 3px — replaces cyan name
- Add status dot: small circle to the right of the name, `rgba(0, 212, 255, 0.4)` color, label "● ONLINE"
- Window controls: icon-only, no box borders, hover state is subtle `rgba(255,255,255,0.06)` background. Close button hover: `rgba(255, 80, 80, 0.15)`
- Height: reduce from implicit to fixed `40px`

### 4.2 Sidebar Panels (`ui/widgets/sidebar.py`, `ui/widgets/system_dashboard.py`, `ui/widgets/quick_actions.py`)

**Sidebar container:**
- Background: `#0a0a18` (slightly darker than main `#080812` for depth)
- Right border: `rgba(0, 212, 255, 0.08)` replaces `#333344`

**Section headers:**
- Replace plain `QLabel` headers with a composite: 2px wide × 10px tall cyan rect + uppercase letter-spaced label
- Add `padding-bottom: 6px; border-bottom: 1px solid rgba(0, 212, 255, 0.10)` below each header

**System dashboard progress bars:**
- Height: `5px → 3px`
- Background track: color-matched to stat (CPU: cyan-tinted, RAM: green-tinted, Disk: orange-tinted) at 8% opacity
- Fill: gradient appearance via a custom `QPainter`-based bar widget (subclass `QWidget`, override `paintEvent`) — Qt's `QProgressBar` ignores gradient fills in QSS on Windows and renders flat
- Stat values: Consolas 9pt, color-matched to stat

**Quick actions:**
- Replace 2×2 tile grid with vertical list of rows
- Each row: icon (14px) + uppercase label (8pt bold, letter-spacing 0.5px)
- Active/hover state: `border-left: 2px solid #00d4ff` + `background: rgba(0, 212, 255, 0.06)` — applied instantly via QSS `:hover` (Qt does not support CSS transitions in QSS; no animation)
- Inactive state: transparent border-left, label at 50% opacity

### 4.3 Chat Bubbles (`ui/widgets/chat_widget.py`)

**Alfred bubbles (`ChatBubble` where `is_user = False`):**
- Background: `rgba(0, 212, 255, 0.05)` replaces `#2d2d44`
- Border: `1px solid rgba(0, 212, 255, 0.15)` replaces `1px solid #333344`
- Add drop shadow: `QGraphicsDropShadowEffect`, blur 12px, `rgba(0,0,0,0.3)`, offset (0, 2)
- Border radius: `14px`, top-left `3px` (tighter than current `16px/4px`)
- Sender label: uppercase, letter-spacing 2px, `rgba(0, 212, 255, 0.55)`, 7pt bold
- Message body: 10.5pt, line-height 1.6 (set via HTML `style` in `_render_markdown_html`)
- Timestamp: Consolas 7pt, `rgba(255,255,255,0.20)`

**Alfred avatar:**
- Background: `#080812`
- Border: `2px solid #00d4ff`
- Glow: `QGraphicsDropShadowEffect`, blur 10px, `rgba(0, 212, 255, 0.35)`
- Letter: "A" in `#00d4ff`

**User bubbles (`ChatBubble` where `is_user = True`):**
- Background: `rgba(0, 102, 204, 0.35)` replaces solid `#0066cc`
- Border: `1px solid rgba(0, 136, 255, 0.30)`
- Drop shadow: same as Alfred bubbles
- Border radius: `14px`, top-right `3px`
- Sender label: uppercase, letter-spacing 2px, `rgba(255,255,255,0.35)`, 7pt bold, right-aligned
- Timestamp: Consolas 7pt, `rgba(255,255,255,0.20)`, right-aligned

**User avatar:**
- Background: `rgba(0, 102, 204, 0.4)`
- Border: `1.5px solid rgba(0, 136, 255, 0.4)`
- No glow
- Letter: user initial in `rgba(255,255,255,0.8)`

**Typing indicator (`TypingIndicator`):**
- Replace text label `"A.L.F.R.E.D is thinking..."` with three animated cyan dots
- Dots: 6×6px circles, `#00d4ff`, animated in wave pattern via `QTimer` at 150ms intervals
- Animation: cycle dot opacities `[1.0, 0.4, 0.15]` → `[0.15, 1.0, 0.4]` → `[0.4, 0.15, 1.0]` → repeat
- Container: `rgba(0, 212, 255, 0.04)` background, `rgba(0, 212, 255, 0.12)` border, padding `13px 16px`

**Date separator (`ui/widgets/date_separator.py`):**
- Divider line: `rgba(0, 212, 255, 0.08)` replaces `#333344`
- Label: `rgba(0, 212, 255, 0.35)`, uppercase, letter-spacing 2px, 7pt

### 4.4 Unified Input Zone (new widget: `ui/widgets/input_zone.py`)

This is the most significant structural change. `InputBar` + `DualWaveformWidget` merge into a single `InputZone` widget with three visual states.

**States:**

| State | Trigger signals | Visual |
|---|---|---|
| `IDLE` | Default / after listening/speaking ends | Single-row input field + mic button + send button. No waveform. |
| `LISTENING` | `listening_state_changed(True)` | Zone expands (200ms `OutCubic` height animation) to reveal inline waveform. Cyan border glows. Mic button pulses. Label "LISTENING" in dim cyan. |
| `SPEAKING` | `speaking_started` | Zone expands to reveal green waveform. Green border. Label "ALFRED SPEAKING". Stop button replaces send button. |

**Idle state layout:**
- Container: `border-radius: 12px`, `border: 1px solid rgba(0, 212, 255, 0.15)`, `background: #080812`
- Input field: transparent background, `font-size: 10.5pt`, placeholder `"Ask ALFRED anything..."`
- Mic button: 34×34px circle, `border: 1.5px solid rgba(0, 212, 255, 0.3)`, no background
- Send button: 34×34px rounded rect, `background: rgba(0, 212, 255, 0.15)`, `border: 1px solid rgba(0, 212, 255, 0.3)`, cyan arrow icon

**Listening state additions:**
- Waveform row: `QPropertyAnimation` on `maximumHeight` from `0 → 44px`, duration `200ms`, `OutCubic`
- Border color: `rgba(0, 212, 255, 0.40)` + `QGraphicsDropShadowEffect` glow `rgba(0, 212, 255, 0.12)`
- State label: "LISTENING" in `rgba(0, 212, 255, 0.6)`, 8pt bold, letter-spacing 2px
- Waveform bars: 3px wide bars in `#00d4ff`; driven by existing `audio_chunk` signal from `AudioCaptureThread`
- Mic button: glow added (`QGraphicsDropShadowEffect` blur 12px cyan), border becomes `2px solid #00d4ff`

**Speaking state additions:**
- Same expand animation, green palette (`#00cc66`)
- Waveform bars driven by existing `output_audio_data` signal; falls back to simulated animation via `QTimer` when no real data (pyttsx3 path)
- Input field: opacity 40%, `setEnabled(False)`
- Stop button: 34×34px circle, `rgba(0, 204, 102, 0.15)` background, green border, `■` icon — clicking it emits `signals.speaking_finished` to halt TTS playback and return the zone to `IDLE` state

**`main_window.py` changes:**
- Remove `DualWaveformWidget` import and instantiation
- Replace `InputBar` + `DualWaveformWidget` with single `InputZone`
- Connect `audio_thread.audio_chunk → input_zone.update_input_waveform`
- Connect `signals.output_audio_data → input_zone.update_output_waveform`
- Connect `signals.speaking_started → input_zone.set_state(InputZone.SPEAKING)`
- Connect `signals.speaking_finished → input_zone.set_state(InputZone.IDLE)`
- Connect `audio_thread.listening_state_changed → input_zone.on_listening_state_changed`

---

## 5. Animations Summary

| Animation | Duration | Easing | Trigger |
|---|---|---|---|
| Chat message fade-in | 300ms | OutCubic | New message added |
| Input zone expand (listening/speaking) | 200ms | OutCubic | State change |
| Input zone collapse | 150ms | OutCubic | State returns to IDLE |
| Typing indicator dot wave | 150ms cycle | Linear (timer) | `show_typing()` called |
| Quick action hover border | instant | QSS :hover | Mouse enter/leave |
| Status bar label fade on LLM switch | 100ms fade out + 100ms in | Linear | `llm_status_changed` signal |

**Constraint:** No animation exceeds 300ms. No purely decorative animations.

---

## 6. Files Changed

| File | Change type |
|---|---|
| `ui/styles/colors.py` | Add new color tokens (Section 3.1) |
| `ui/styles/dark_theme.py` | Update QSS to use new tokens, new typography scale |
| `ui/widgets/title_bar.py` | Logo, gradient bg, borderless controls, status dot |
| `ui/widgets/sidebar.py` | Darker bg, refined border |
| `ui/widgets/system_dashboard.py` | Section headers, thinner gradient bars, monospace values |
| `ui/widgets/quick_actions.py` | Row layout replaces tile grid, left-border active state |
| `ui/widgets/chat_widget.py` | Bubble styles, avatar styles, typing indicator, date separator |
| `ui/widgets/input_zone.py` | **New file** — replaces `input_bar.py` + `waveform_widget.py` |
| `ui/widgets/input_bar.py` | Deleted (absorbed into `input_zone.py`) |
| `ui/widgets/waveform_widget.py` | Deleted (absorbed into `input_zone.py`) |
| `ui/main_window.py` | Wire `InputZone`, remove old widget imports |

---

## 7. Out of Scope

- No new features or commands
- No changes to `core/`, `memory/`, `api/`, `services/`, `tests/`
- No changes to the REST API or voice logic
- No new dependencies

---

## 8. Success Criteria

- App launches and all existing functionality works unchanged
- All three input zone states (idle, listening, speaking) transition correctly
- `ruff format .` and `ruff check .` pass with no errors
- Existing test suite (`pytest tests/`) passes unchanged
