# Chat UI Design Enhancements

## Overview
This document outlines design enhancements for the poker.ev chat interface, inspired by system.css minimalist retro aesthetic (Apple System 6 era). The goal is to create a more authentic retro computing experience while maintaining usability.

## Design Philosophy

### Core Principles (from system.css)
1. **Monochromatic Palette**: Single-color approach for visual coherence
2. **Component-Based Architecture**: Discrete UI elements with consistent patterns
3. **Historical Authenticity**: Match classic Macintosh interface patterns
4. **Minimalist Clarity**: Reduce visual complexity, emphasize function

## Current State

### Existing Strengths
- Component separation (ChatPanel, MessageRenderer, ChatInput, ScrollHandler)
- Pixel-art corner treatments
- Retro scrollbar with grip lines
- PixeloidMono monospace font
- Dark background with bright accents

### Color Scheme (Current)
```python
# Multiple accent colors per role
USER: Dark green bg (20, 60, 20) + Bright green (0, 255, 100)
AI: Dark blue bg (20, 40, 60) + Cyan (0, 200, 255)
SYSTEM: Dark gold bg (60, 50, 20) + Gold (255, 215, 0)
```

## Proposed Enhancements

### 1. Monochrome Palette Simplification

**Goal**: Reduce to 2-3 shades for authentic retro feel

**Implementation**:
```python
# File: poker_ev/gui/chat/chat_panel.py, message_renderer.py

# Primary palette - Retro phosphor green
BG_DARK = (15, 15, 15)          # Almost black
BG_MEDIUM = (26, 26, 26)        # Dark gray
BG_PANEL = (35, 35, 35)         # Medium dark
ACCENT_PRIMARY = (0, 255, 100)  # Retro green (only bright color)
ACCENT_DIM = (0, 180, 70)       # Dimmed green
TEXT_PRIMARY = (220, 255, 220)  # Light green tint
TEXT_SECONDARY = (150, 150, 150) # Gray
```

**Changes**:
- Replace role-based colors (blue, gold) with single green accent
- Distinguish message types through border patterns, not colors
- Use brightness variation instead of hue variation

**Files to modify**:
- `poker_ev/gui/chat/chat_panel.py` (lines 24-28)
- `poker_ev/gui/chat/message_renderer.py` (lines 17-29)
- `poker_ev/gui/chat/scroll_handler.py` (lines 16-20)
- `poker_ev/gui/chat/chat_input.py` (lines 16-22)

---

### 2. Message Bubble Simplification

**Goal**: More rectangular, System 6-style dialog boxes

**Current Design**:
- Rounded corners
- Different colors per role
- Soft pixel borders

**Proposed Design**:
- Hard rectangular edges (no rounding)
- Single pixel or double pixel borders
- Role distinction through border style:
  - **User**: Double-line border (2px)
  - **Assistant**: Single-line border (1px)
  - **System**: Dashed border pattern

**Implementation**:
```python
# File: poker_ev/gui/chat/message_renderer.py

def _draw_retro_border(self, screen, rect, role):
    """Draw System 6-style borders based on role"""
    if role == 'user':
        # Double border (like active window)
        pygame.draw.rect(screen, self.ACCENT_PRIMARY, rect, 2)
        pygame.draw.rect(screen, self.ACCENT_DIM, rect.inflate(-4, -4), 1)
    elif role == 'assistant':
        # Single border
        pygame.draw.rect(screen, self.ACCENT_PRIMARY, rect, 1)
    else:  # system
        # Dashed border pattern
        self._draw_dashed_border(screen, rect)

def _draw_dashed_border(self, screen, rect):
    """Draw retro dashed border for system messages"""
    dash_length = 8
    gap_length = 4
    # Draw top/bottom
    for x in range(rect.left, rect.right, dash_length + gap_length):
        pygame.draw.line(screen, self.ACCENT_PRIMARY,
                        (x, rect.top), (min(x + dash_length, rect.right), rect.top), 1)
        pygame.draw.line(screen, self.ACCENT_PRIMARY,
                        (x, rect.bottom), (min(x + dash_length, rect.right), rect.bottom), 1)
    # Draw left/right
    for y in range(rect.top, rect.bottom, dash_length + gap_length):
        pygame.draw.line(screen, self.ACCENT_PRIMARY,
                        (rect.left, y), (rect.left, min(y + dash_length, rect.bottom)), 1)
        pygame.draw.line(screen, self.ACCENT_PRIMARY,
                        (rect.right, y), (rect.right, min(y + dash_length, rect.bottom)), 1)
```

**Changes**:
- Remove corner pixel highlighting
- Remove color-coded backgrounds (use single bg color)
- Simplify to rectangular shapes
- Use border patterns for visual distinction

**Files to modify**:
- `poker_ev/gui/chat/message_renderer.py` (methods `_draw_pixel_border`, `render_message`)

---

### 3. Header Redesign - Classic Title Bar

**Goal**: Mac System 6 title bar aesthetic

**Current Design**:
- Dark green background
- Centered title + subtitle
- Simple line separator

**Proposed Design**:
- Single-color background with subtle pattern
- Classic title bar close box (optional)
- Horizontal line pattern (like System 6 drag handles)

**Implementation**:
```python
# File: poker_ev/gui/chat/chat_panel.py

def _render_header(self, screen):
    """Render System 6-style title bar"""
    # Background
    pygame.draw.rect(screen, self.BG_PANEL, self.header_rect)

    # Top border highlight
    pygame.draw.line(screen, self.ACCENT_PRIMARY,
                    (self.header_rect.left, self.header_rect.top),
                    (self.header_rect.right, self.header_rect.top), 2)

    # Title (centered, single line, larger)
    title = "POKER ADVISOR"
    title_surface = self.font_large.render(title, True, self.ACCENT_PRIMARY)
    title_x = self.header_rect.centerx - title_surface.get_width() // 2
    title_y = self.header_rect.centery - title_surface.get_height() // 2
    screen.blit(title_surface, (title_x, title_y))

    # Bottom border with double line (classic separator)
    pygame.draw.line(screen, self.ACCENT_PRIMARY,
                    (self.header_rect.left, self.header_rect.bottom - 2),
                    (self.header_rect.right, self.header_rect.bottom - 2), 1)
    pygame.draw.line(screen, self.ACCENT_DIM,
                    (self.header_rect.left, self.header_rect.bottom - 1),
                    (self.header_rect.right, self.header_rect.bottom - 1), 1)

    # Optional: Add drag handle lines (centered horizontal lines)
    center_x = self.header_rect.centerx
    center_y = self.header_rect.centery
    handle_width = 40
    for i in range(-2, 3, 2):
        y = center_y + i * 3 - 15  # Above title
        pygame.draw.line(screen, self.ACCENT_DIM,
                        (center_x - handle_width // 2, y),
                        (center_x + handle_width // 2, y), 1)
```

**Changes**:
- Remove subtitle ("AI-Powered Strategy Guide")
- Simplify to single title
- Add classic separator lines
- Optional: Add visual drag handle pattern

**Files to modify**:
- `poker_ev/gui/chat/chat_panel.py` (method `_render_header`, lines 261-287)

---

### 4. Input Field Enhancement

**Goal**: Classic input box with clearer visual states

**Current Design**:
- Pixel corners
- Border color change on active
- Blinking cursor

**Proposed Design**:
- Inset appearance (3D effect with simple lines)
- More pronounced active state
- Retain blinking cursor

**Implementation**:
```python
# File: poker_ev/gui/chat/chat_input.py

def render(self, screen):
    """Render classic input field"""
    # Inset effect - dark shadow on top/left
    shadow_offset = 2

    if not self.is_active:
        # Inactive - subtle inset
        pygame.draw.rect(screen, (0, 0, 0),
                        self.rect.inflate(shadow_offset, shadow_offset))
        pygame.draw.rect(screen, self.BG_COLOR, self.rect)
        pygame.draw.rect(screen, self.BORDER_COLOR, self.rect, 1)
    else:
        # Active - bright border
        pygame.draw.rect(screen, self.ACCENT_PRIMARY,
                        self.rect.inflate(4, 4))
        pygame.draw.rect(screen, self.BG_COLOR, self.rect)
        pygame.draw.rect(screen, self.ACCENT_PRIMARY, self.rect, 2)

    # Text rendering (unchanged)
    # ... existing text rendering code ...
```

**Changes**:
- Add inset shadow effect
- Make active state more obvious (thicker bright border)
- Simplify corner decorations

**Files to modify**:
- `poker_ev/gui/chat/chat_input.py` (method `render`, lines 207-253)

---

### 5. Scrollbar Refinement

**Goal**: More authentic classic scrollbar

**Current Design**:
- Custom styled with grip lines
- Hover effects
- Draggable handle

**Proposed Design**:
- Simplified track (no background pattern)
- Handle with horizontal grip lines (3-5 lines)
- Arrow buttons at top/bottom (optional)

**Implementation**:
```python
# File: poker_ev/gui/chat/scroll_handler.py

def render(self, screen, mouse_pos):
    """Render System 6-style scrollbar"""
    if self.content_height <= self.scroll_area.height:
        return

    # Scrollbar track (simple outline)
    pygame.draw.rect(screen, self.BG_DARK, self.scrollbar_rect)
    pygame.draw.rect(screen, self.ACCENT_DIM, self.scrollbar_rect, 1)

    # Handle
    handle_rect = self._get_handle_rect()
    if handle_rect:
        is_hover = handle_rect.collidepoint(mouse_pos) or self.is_dragging
        handle_color = self.ACCENT_PRIMARY if is_hover else self.ACCENT_DIM

        # Fill handle
        pygame.draw.rect(screen, self.BG_PANEL, handle_rect)
        pygame.draw.rect(screen, handle_color, handle_rect, 2)

        # Horizontal grip lines (centered)
        num_lines = 4
        spacing = 3
        center_y = handle_rect.centery
        start_y = center_y - (num_lines // 2) * spacing

        for i in range(num_lines):
            y = start_y + i * spacing
            pygame.draw.line(screen, handle_color,
                           (handle_rect.left + 3, y),
                           (handle_rect.right - 3, y), 1)
```

**Changes**:
- Simplify track appearance
- Make grip lines horizontal (not just 3 centered)
- Use consistent color scheme

**Files to modify**:
- `poker_ev/gui/chat/scroll_handler.py` (method `render`, lines 186-226)

---

### 6. Typography Refinement

**Goal**: Maximize retro aesthetic through font usage

**Current Implementation**:
- PixeloidMono for all text (good!)

**Proposed Enhancement**:
- Ensure consistent sizing hierarchy
- Use fixed sizes (no anti-aliasing)
- Consider Chicago-style font for header

**Recommended Sizes**:
```python
# File: poker_ev/gui/pygame_gui.py or wherever fonts are loaded

FONT_SIZES = {
    'tiny': 10,      # Rarely used
    'small': 14,     # Timestamps, metadata
    'medium': 16,    # Message content (changed from 18)
    'large': 24,     # Header title (changed from 28)
    'xlarge': 32     # Unused, for future
}

# Ensure no anti-aliasing (already done when rendering with True/False flag)
```

**Changes**:
- Reduce font sizes slightly for more authentic retro feel
- Keep PixeloidMono or consider adding Chicago font for header
- Ensure all rendering uses aliased (non-smoothed) rendering

**Files to modify**:
- Font loading location (check `poker_ev/gui/pygame_gui.py` or main GUI file)
- `poker_ev/gui/chat/chat_panel.py` (font initialization)

---

## Implementation Priority

### Phase 1: Core Visual Changes (High Impact)
1. **Monochrome palette** - Update all color constants
2. **Message bubble borders** - Simplify to rectangular with pattern-based distinction
3. **Header redesign** - Classic title bar

### Phase 2: Refinements (Medium Impact)
4. **Input field enhancement** - Inset effect and active states
5. **Scrollbar refinement** - Simplified classic look

### Phase 3: Polish (Low Impact)
6. **Typography adjustments** - Fine-tune sizes

---

## File Modification Summary

| File | Lines | Changes |
|------|-------|---------|
| `chat_panel.py` | 24-28, 261-287 | Color constants, header rendering |
| `message_renderer.py` | 17-29, 171-197 | Color constants, border methods |
| `scroll_handler.py` | 16-20, 186-226 | Color constants, scrollbar rendering |
| `chat_input.py` | 16-22, 207-253 | Color constants, input rendering |
| Font loading file | Font sizes | Adjust size constants |

---

## Testing Checklist

After implementing changes:

- [ ] Message bubbles render correctly for all roles (user, assistant, system)
- [ ] Border patterns distinguish message types clearly
- [ ] Scrollbar functions properly (drag, wheel, visibility)
- [ ] Input field shows active/inactive states
- [ ] Header displays correctly
- [ ] Color scheme is consistent across all components
- [ ] Text is readable with new colors
- [ ] Typing indicator works with new styling
- [ ] Performance is not impacted (especially with border pattern rendering)

---

## Visual Reference

### System 6 Characteristics
- **Windows**: Single pixel borders, title bar with horizontal lines
- **Buttons**: Rectangular with subtle 3D effect
- **Scrollbars**: Simple track with patterned handle
- **Dialogs**: Hard edges, double borders for active elements
- **Palette**: Monochrome (black, white, grays) with single accent

### poker.ev Adaptation
- **Base**: Dark theme instead of white (modern consideration)
- **Accent**: Phosphor green (retro terminal aesthetic)
- **Hybrid**: Classic patterns + modern readability
- **Consistency**: All components share visual language

---

## Future Enhancements

Beyond this initial redesign:

1. **Animation**: Subtle scan-line effect overlay
2. **Sound**: Retro beep/click sounds for interactions
3. **Themes**: Allow user to toggle between green/amber/cyan phosphor
4. **Window controls**: Add minimize/maximize buttons to header
5. **Panel docking**: Allow chat panel to be repositioned or resized

---

## Resources

- **system.css GitHub**: https://github.com/sakofchit/system.css
- **System 6 Visual Reference**: Classic Mac OS interface screenshots
- **PixeloidMono Font**: Already in use at `poker_ev/assets/fonts/PixeloidMono-1G8ae.ttf`
- **Current Chat Components**: `poker_ev/gui/chat/` directory

---

## Notes

- Maintain backward compatibility with existing `ChatPanel` API
- Test on different screen resolutions
- Ensure accessibility (sufficient contrast despite retro styling)
- Keep code readable and well-commented
- Profile performance if pattern-based borders impact frame rate

---

*Last Updated: 2025-11-08*
