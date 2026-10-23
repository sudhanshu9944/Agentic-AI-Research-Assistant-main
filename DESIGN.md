# Reference and implementation design

Reference: https://taai.live/, captured 23 October 2026 using Firecrawl branding/HTML and a browser screenshot. The screenshot was visually inspected at desktop width. The reference has a white horizontal header, a cream hero, oversized black Poppins headings, yellow highlighted words, hard black offset shadows and pink/blue note cards. These patterns are adapted to Research.AI, retaining its own identity and research content rather than copying the course website or its branding.

## Evidence and tokens

- Body/display font Poppins: branding output and computed body font. DM Mono is present in the reference font stylesheet and is used for labels/note headings here.
- White background #FFFFFF, ink #111111, yellow #FDE047: extracted branding.
- Purple #8B5CF6 and soft background #FBF9FF: computed reference CSS variables.
- Cream #FFF5D6, pink #F6ADD6 and blue #80D3F4: visual approximations based on inspected screenshot.
- Square primary buttons, 2px black borders and 4px black offset shadows: extracted button metadata plus screenshot.
- 1150px working container, 24px card gaps, 800px/500px responsive adaptations are implementation choices, not exact extracted values. Reference mobile and animation behavior were not measured.

## Product layout

White navigation → three-step journey → cream topic hero and question form → recommendation checkbox cards → explicit research action → summary/selected and excluded scope/evidence gaps → expandable full report → explicit PDF export. Real saved history is available through My Research. No fake authentication, endorsements or college claims.

## Imagery

Reference uses TAAI logo.webp and testimonial photos on lower sections. They are not needed in this application and have not been copied. Research.AI uses its own text mark, Lucide icons and CSS cards. Fonts load through Google Fonts with system fallbacks.

## Dark theme and account additions

A persisted moon/sun toggle keeps the reference layout while adapting surfaces to charcoal/plum, with readable pale text, muted pink/blue cards and yellow actions. Local account controls and a GitHub icon are functional additions to the header, not copied reference behavior. The 100-token signup grant and app costs are labeled as a browser-local demo balance. Author credits appear in both themes.
