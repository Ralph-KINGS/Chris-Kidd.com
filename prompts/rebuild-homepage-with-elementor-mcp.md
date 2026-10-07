# Prompt: Rebuild chris-kidd.com with the new design (Elementor MCP)

Copy everything below the line into Claude Code in a session where the
`chris-kidd.com WP Elementor MCP` server is connected.

Design reference (canvas board): https://claude.ai/artifact/U3CZz6UvnYj8KzEYasLdnC

---

You are rebuilding the homepage of **chris-kidd.com** (WordPress 7.1, Hello Elementor theme, Elementor Pro 4.3) using the connected **chris-kidd.com WP Elementor MCP** tools. The design and audit are already done; your job is to implement them exactly. **Do not change fonts or colours** — only the layout, spacing, hierarchy and responsiveness change.

## Ground rules

1. **Never edit the live homepage first.** Work on a draft copy:
   - Read the current homepage (`elementor_get_page` id **20**) and save its JSON locally as a backup.
   - Create a new **draft** page titled `Homepage v2 (draft)` with `elementor_create_page` and build the new design there.
   - Only after I approve the draft, replace page 20's content (take a snapshot first; `elementor_list_snapshots` / `elementor_restore_snapshot` are the rollback path).
2. Before any write, call `elementor_get_structure` on the target page so you are working from current element IDs.
3. Use containers (flexbox) only — no sections/columns, no absolute positioning, **no background images used as content**, no negative margins, no %-width buttons, no fixed px text widths.
4. Set **tablet and mobile values** for every size, padding, gap and direction you set (Elementor `_tablet` / `_mobile` setting suffixes).
5. Keep existing copy unless this prompt gives new copy. Anything in `[square brackets]` is a placeholder Chris must fill — leave it visible, don't invent content.
6. Work section by section. After each section, re-read the structure and confirm the settings landed before moving on. At the end give me the draft's preview URL and a checklist of what was done.

## Brand tokens (unchanged — use exactly)

| Role | Hex | Use |
|---|---|---|
| Empire Navy (primary) | `#1E3A8A` | Headings, primary buttons, links, icons |
| Deep Navy | `#132557` | Button hover, dark section backgrounds (stats, CTA, footer), icon chips |
| Charcoal | `#4E4E4E` | All body text |
| Silver | `#E0E0E0` | 1px borders, dividers |
| White | `#FFFFFF` | Page background, text on navy |
| Gold (Build accent) | `#D6A71C` | Text **only on navy**; on white use as rules/borders only |
| Green (Sharp accent) | `#5EC76B` | Text **only on navy**; on white use for check icons only |
| Red (Core / family accent) | `#C43838` | Text **only on white**; never as text on navy |
| Light section tint | `rgba(30,58,138,0.04)` | Family section background (navy at 4%, not a new colour) |

If the MCP can edit Elementor Site Settings / the Kit, register these as **Global Colors** and the type below as **Global Fonts**, then reference the globals. If it cannot, set them per widget and tell me at the end so I can create the globals manually.

**Fonts:** Bebas Neue (headings, buttons, eyebrows) + Open Sans (body).
**Bebas Neue must be weight 400 everywhere** (the site currently uses 500–600; the font only has 400, so browsers fake-bold it).

### Type scale (desktop / tablet / mobile)

| Element | Font | Size | Line height | Other |
|---|---|---|---|---|
| H1 | Bebas Neue 400 | 104 / 80 / 64 px | 0.9 | colour `#1E3A8A` |
| H2 | Bebas Neue 400 | 64 / 52 / 44 px | 1.0 | colour `#1E3A8A` (white on navy bands) |
| H3 card title | Bebas Neue 400 | 32 / 30 / 28 px | 1.1 | |
| Eyebrow | Bebas Neue 400 | 18 / 16 / 16 px | 1.2 | letter-spacing 0.14em |
| Lead | Open Sans 600 | 22 / 20 / 18 px | 1.4 | `#4E4E4E` |
| Body | Open Sans 400 | 18 / 17 / 16 px | 1.65 | `#4E4E4E`, max-width ~60ch |
| Stat number | Bebas Neue 400 | 72 / 64 / 48 px | 1.0 | |
| Button | Bebas Neue 400 | 21 px | 1 | letter-spacing 0.04em |

### Components

- **Primary button:** bg `#1E3A8A`, text white, hover bg `#132557`, radius 10px, padding 0 28px, min-height 52px, arrow-right icon after text (15px gap), **no "grow" hover animation**. Full width on mobile.
- **Secondary button:** transparent bg, 2px solid `#1E3A8A` border, text `#1E3A8A`, hover bg `#1E3A8A` + white text, same size/radius.
- **Gold CTA button (dark bands only):** bg `#D6A71C`, text `#132557`, hover bg `#FFFFFF`.
- **Text link:** Open Sans 700 16px `#1E3A8A`, 2px `#D6A71C` bottom border, arrow icon.
- **Card:** 1px `#E0E0E0` border, radius 16px, shadow `0 12px 32px rgba(19,37,87,0.08)`, a 6px accent bar on top, padding 36px 32px (mobile 24px 22px). Hover: translateY −6px.
- **Icon chip:** 56×56 (mobile 48), radius 12, bg `#132557`, white line icon.
- **Spacing scale:** 8 · 16 · 24 · 40 · 64 · 96 · 128. Use container **gap**, not margins.
- **Content width:** boxed, max 1200px. Side padding 80 / 40 / 20 px.
- **Section vertical padding:** 128 / 96 / 72 px.

## Page structure to build (top → bottom)

Existing media to reuse: **ID 58** `Chris-Kidd-Website.png` (portrait cut-out) and **ID 156** `Chris-Kidd-Website-1200-x-628-px.png` (family image). Use them in **Image widgets**, with alt text.

### 1. Hero
- Container: row, boxed 1200, align center, gap 64; padding 72/96 top-bottom desktop. Min-height none (not 900px). **Mobile: column-reverse** so the image sits on top (or order the image first on mobile).
- **Left column (≈55%)**, column, gap 24:
  - Eyebrow row: 48×4px gold `#D6A71C` bar + eyebrow text `BUSINESS OWNER · FAMILY MAN · PERTH` in `#1E3A8A`.
  - H1 `Building Empires` (break after "Building"). **This is the only H1 on the page.**
  - Lead `Stay Sharp, Protect the Core`.
  - Body: existing intro paragraph ("I'm Chris Kidd, a successful business owner…").
  - Buttons row (gap 14, wraps; mobile stacked full-width): **Primary** `Work with Chris` → `/work-with-chris/`; **Secondary** `View my Empire` → `#empire`.
- **Right column (≈45%)**: Image widget, media 58, radius 16px, alt `Chris Kidd`. Behind it, a decorative 3px gold-border box offset bottom-left (optional — skip if the MCP can't do it cleanly; never use pixel-offset backgrounds).
- Mobile: image height ~300px, object-fit cover, top-aligned on face.

### 2. Stats band
- Full-width container, bg `#132557`; inner boxed grid of **3 columns** (stays 3 compact columns on mobile), gap 40 (mobile 12), padding 56 (mobile 32/20).
- Each stat: 40×4px accent bar, number, label (Open Sans 600 16px / mobile 13px, white).
  - `15+` green `#5EC76B` — `Years in business`
  - `70+` gold `#D6A71C` — `Projects completed`
  - `100%` **white** number with red `#C43838` bar — `Family focused`
- Remove the old 12%-width headings and −20px label margins.

### 3. Three Pillars (id `pillars`)
- Section padding 128/96/72. Header row (wraps): left = eyebrow `THE FRAMEWORK` + H2 `Three Pillars of Success`; right = existing intro sentence (max 30em).
- Grid 3 columns desktop, 1 column mobile (tablet: 3 if it fits, else 1), gap 24.
- Three cards (component spec above), each with its accent bar + icon:
  1. **Building Empires** — gold bar, crown icon; points: Strategic Vision, Scalable Systems, Long-term Value.
  2. **Stay Sharp** — green bar, target/bullseye icon (**currently missing an icon — fix**); points: Continuous Learning, Strategic Thinking, Market Awareness.
  3. **Protect the Core** — red bar, heart icon; points: Family First, Work-Life Balance, Core Values.
- Each card's checklist = **one** Icon List widget with 3 items (not three separate widgets), green `#5EC76B` check-circle icons, text Open Sans 700 15px `#132557`, separated from the body by a 1px `#E0E0E0` top border.
- Remove the groove borders and the 40–50% black shadows.
- Below the grid: text link `Learn more about my journey` → `/about/`.
- Delete the grey 45% dividers.

### 4. Family section (id `family`)
- Full-width bg `rgba(30,58,138,0.04)`, 1px `#E0E0E0` top and bottom borders. Inner boxed row, gap 72, align center; **mobile: column, image first**.
- Left: Image widget, media 156, height 520 (mobile 220), object-fit cover, radius 16, alt `Chris Kidd with his family`.
- Right column, gap 28:
  - Eyebrow `PROTECT THE CORE` in red `#C43838`.
  - **H2** (not H1) `Success Means Nothing Without Family`.
  - Three numbered values — number in Bebas 36px red (`01`, `02`, `03`), title H3 Bebas 24px `#1E3A8A`, existing body copy:
    01 Home is the Foundation · 02 Balance Creates Strength · 03 Legacy Over Profit.
  - Primary button `Explore my Family Values` (**fix the "EXLPORE" typo**) → `/about/#family-values`.
- Delete the empty 66% spacer container and the pixel-positioned background image.

### 5. The Empire (id `empire`) — new
- Section padding 128/96/72. Eyebrow `THE EMPIRE`, H2 `The Empire`.
- Grid 3 → 1 columns, gap 24: three cards (border style, no accent bar), each = dashed placeholder logo box `[Venture logo]`, title `[Venture one/two/three]` Bebas 28px navy, body `[One line on what it does and Chris's role.]`, link `Visit ↗`.
- Testimonial block below: bg `#132557`, radius 16, padding 48 (mobile 28/24), gold quote icon, quote `[Client or partner testimonial]` Open Sans 600 24px (mobile 18) white, caption `[Name] · [Role, Company]` gold.

### 6. Closing CTA
- Full-width bg `#132557`, padding 112/96/72. Row (wraps; mobile column):
  - H2 white `Big Ideas Start with Small Conversations`; body white `Exploring a collaboration, looking for advice, or building something real? Let's talk.`
  - **Gold CTA button** `Work with Chris` → `/work-with-chris/` (min-height 60, full width on mobile).

### 7. Footer
- If the site uses an Elementor Pro Theme Builder footer, update that template instead of adding it to the page; otherwise add as the last container.
- bg `#132557`, 1px `rgba(255,255,255,0.12)` top border. Row (wraps; mobile column): wordmark `CHRIS KIDD` (Bebas 28 white) + tagline `Stay Sharp, Protect the Core`; links About, Work with Chris, `[LinkedIn]`, `[Instagram]` (white, Open Sans 600, ≥44px tap height on mobile); `© 2026 Chris Kidd`.

### Header / navigation
- If a Theme Builder header exists, update it: wordmark `CHRIS KIDD` left (Bebas 30, `#1E3A8A`, letter-spacing 0.04em); nav About · The Pillars (`/#pillars`) · The Empire (`/#empire`) · Family (`/#family`); compact primary button `Work with Chris` (min-height 44). Mobile: hamburger menu toggle (44×44). 1px `#E0E0E0` bottom border. If no header template exists, tell me rather than building one inside the page.

## Other pages (after the homepage is approved)

Apply the same tokens, button styles, card style, type scale and responsive values to:
- **About (id 1):** Bebas weight 400; replace any background-image layouts with Image widgets; same card style for "Features that Set Chris Apart". Flag (don't rewrite) that this page is written in third person while the homepage is first person — ask me which voice to use.
- **Work with Chris (id 24):** shorten the H1 to `Work with Chris` and move the current long sentence into the intro paragraph; style the form inputs radius 10px, 1px `#E0E0E0` border, 52px height, navy focus ring; the six service cards use the card spec with 2×3 → 1 column grid.

## Acceptance checklist (verify before reporting done)

- [ ] Exactly one H1 per page.
- [ ] Every button has a working link.
- [ ] No background images used for portraits/photos; all photos are Image widgets with alt text.
- [ ] No negative margins, no %-width buttons, no fixed-px text widths, no empty spacer containers.
- [ ] Bebas Neue weight 400 everywhere.
- [ ] Gold/green never used as text on white; red never used as text on navy.
- [ ] Tablet and mobile values set for typography, padding, gap and direction on every container you touched.
- [ ] Layout checked at 1440, 1280, 1024, 820, 390 and 360 px wide — nothing overlaps and there's no horizontal scroll (use a browser/screenshot tool if available; otherwise tell me which widths I need to check).
- [ ] Draft left unpublished until I approve; backup JSON of the original page saved; snapshot taken before replacing page 20.
