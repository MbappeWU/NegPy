# NegPy User Guide

NegPy turns film scans into positives with a non-destructive, darkroom-style pipeline. It never writes to your source files. Edits live in a local database.

For the pipeline order and math, read [PIPELINE.md](PIPELINE.md).

---

## 1. The Big Picture

### Protected data folders on Windows

If Windows blocks the default data folder, NegPy suggests `%LOCALAPPDATA%\NegPy\data`. Click the path to pick another, then **Use This Folder**. Nothing is copied: a new folder starts empty, and an existing NegPy folder keeps its data. The choice is saved in `data-location.json` and stays even if Documents becomes writable. `NEGPY_USER_DIR` overrides it.

### Screen layout

*   **Below the canvas, the film strip**: your frames as strips of film, with the toolbar under it at the bottom of the window.
*   **The toolbar**: its **Photo / Roll** switch picks the row it shows. **Roll** holds the film strip's import, sorting and triage tools and its filter (§2). **Photo** holds navigation, zoom (**Fit to Window**, 25–400%, **HQ Preview**), rotate/flip (on every selected frame), **Tools** (arms any canvas tool: crop, straighten, the pickers, masks, retouching), undo/redo, the **Print** menu (Before / After and the peeks below) and **Overlays** (Zone Overlay, Clipping Overlay, Printing Notes, Grain Focuser, Probe at Cursor, Frame Info). An armed canvas tool shows its use, its slider and **Done** on the toolbar; its name opens the same menu to switch tools. The **⋯** menu holds every action, including **Preferences…** (§14). Right-click the toolbar for **Edit Toolbar…**.
*   **Center, the canvas**: the live preview. Scroll or pinch to zoom, drag to pan, double-click to switch between fit and 100% at that spot. Zoomed in, a navigator in the lower right shows the visible part and the zoom; click or drag it to move the view. Right-click the image for **Reset View**, **Sticky Zoom**, the pickers, copy/paste settings, **Reset Settings**, **Reset to Roll Settings** and **Unload** (drop the frame from the session; its edit stays).
*   **Frame Info**: `I` cycles the corner pills. **Off**; **Basic**: file name, scan size, film mode; **Full**: adds the frame's place in the strip, film, camera and lens, the soft-proof profile, the export size and the zoom.
*   **Right, the controls**: tabs **Library** / **Roll** / **Frame** / **Metadata** / **Export** / **Scan**. **Roll** and **Frame** have a pinned **Analysis** readout; **Frame** has its own row of tabs. Only Roll and Frame change the render.

With nothing open, the canvas offers **Load Scans…** and **Take the Tour**.

Drag the film strip's top edge to change its height, which sets the size of its frames; the chevron at the toolbar's right end folds the strip away, and the canvas then sits on the toolbar (`Ctrl+[`). Drag the controls panel by its top edge to float it; its pin button docks it. **Shift+H** hides the controls panel and folds the film strip, or brings both back. **Reset Panel Layout** (**⋯** menu) restores the default layout.

### The tour

**Take the Tour** (**⋯** menu, or Find) has eight chapters. A circled step is a task. With nothing open, **Load Demo Negative** opens a synthetic negative. **Read More…** opens the panel's guide. Esc ends the tour; the next one offers **Resume Where You Left Off**.

### Find

**Ctrl+K** (or **Find Control or Action…** in the **⋯** menu) searches every slider, card, action and preset, by name or by another editor's word (*contrast* finds **ISO-R Grade**). Enter opens the row on its tab; on a preset it opens **Apply Preset**.

### Before / After

**Before / After** in the **Print** menu (or `\`) splits the canvas: left is the auto baseline (same film process, crop and rotation, every creative control at default), right is your edit. It stays up while you edit. `\`, `Esc`, a frame change, a peek or the test strip closes it. Hold `\` instead to see the whole frame as the baseline until you let go.

### Reference view

**Shift+R** (or **Reference View** in the **⋯** menu) pins the current frame in a pane beside the canvas, to match other frames to it. Press **Shift+R** twice to pin again. **✕** or **Shift+R** closes it.

### Peek Negative

**Negative** in the **Print** menu (or `N`) shows the scan as loaded: not inverted, not metered, no edits; crop, rotation and flip still apply. Use it to check density, mask color and scanner clipping. It is scaled to its brightest tone, so read density from the density histogram. It stays up through Export and Metadata changes and while you drag a crop or rotation handle or Fine Rotation. Any other edit or a frame change closes it.

### Peek Embedded Preview

**Embedded** in the **Print** menu (or `P`) shows the camera's own JPEG at your crop and rotation. NegPy uses nothing from it. Scanner TIFFs and most converter DNGs have none. It closes like Peek Negative.

`Esc` closes any peek, the split or a test strip. Hold a peek key (`N`, `M`, `P`) to peek only while it is down.

### The workflow

**Roll** holds what the whole roll shares:

| Tab | Panels | What it is for |
|-----|--------|---------------|
| **Roll** | Setup · Frame Assembly · Calibration · Metering · Crop · Roll Analysis · Raw Decode · Optics | The scanning rig, film type, capture color, crop shape, roll baselines, metering |

**Frame** tabs follow the pipeline order. Favorites (star) and History (clock) are the two icon tabs at the end:

| Tab | Panels | What it is for |
|-----|--------|---------------|
| **Geometry** | Geometry | Crop, straighten, easel movements |
| **Exposure** | Filtration · Tone · Dodge & Burn | White balance, density, contrast, curve, local burns |
| **Look** | Lab · Alternative Processes · Toning | Chroma, sharpening, lith, cyanotype, Sabattier, toning |
| **Finish** | Retouch · Finishing | Dust, vignette, border, carrier |
| **Favorites** | Your chosen sliders · Presets | Most-used controls, saved edits |
| **History** | Work prints · Edit history | Named versions, undo trail |

Tabs that do not change the render:

| Tab | Panels | What it is for |
|-----|--------|---------------|
| **Export** | Export settings | Format, size, color, batch |
| **Metadata** | Metadata Preview · Shot · Process · Presets · My Gear | Camera, lens, film; metadata presets and your gear library |
| **Scan** | Scanner · the scanner's cards · Output | Direct capture from a film scanner or camera |

On a slider, click the value to type one, drag the name to scrub (**Shift** for finer steps), and double-click or **Ctrl**+click the track to reset. A chevron beside a control or a sub-header folds the fine-tune controls under it; click the chevron or the name. Each fold stays as you leave it, and a dot on a closed one marks an edited control inside. On a dropdown, **‹** and **›** step to the previous or next choice; click the name for the full list. A **dot** on a panel header or tab marks a non-default value. Each panel header has a **reset** action and an **ⓘ** that opens this guide there.

### What carries to the next frame

An unedited frame gets the rig and roll settings: film process, crop ratio, flips, calibration, print stock, the Lab polish and export preferences. The look (density, filtration, tone curve, toning, dodge and burn) starts clean.

**Preferences → Session & Storage → Persistent Settings…** sets which settings carry. **Carry settings between frames** is the master switch; off, new frames get bare defaults.

An edited frame keeps its look; only export and metadata settings reach it. **Reset Settings** returns bare defaults and, in a roll, sets every Roll-tab card back to **Roll**. No reset changes the scanning setup (Linear RAW, demosaic); the **Setup** card's scanning choices set those, and a camera Scan sets the decode and the print stock per frame from its light.

### Frame or roll: the scope pair

Each section header has **Frame** (amber) and **Roll** (red) beside its reset arrow, which resets that card alone. The lit one shows where the card's values live; click the other to move them there. Frames that are not one roll (search results, several folders) show only **Frame** until **Save as Roll…**.

On a **Roll tab** or **Metadata** card the pair is a latch. On Roll, the card follows the roll and new frames inherit it; an edit flips it to Frame. **Roll** pushes this frame's value to the roll; **Frame** pins it to this frame. Right-click the card header for **Undo Apply to Roll**, which undoes this frame's last push.

On a **frame** card (Geometry, Filtration, Tone, Lab, Alternative Processes, Toning, Retouch, Finishing), **Roll** opens the section's clone picker, to apply your changes to the selection or the whole roll. After a whole-roll apply the card reads Roll until you change a pushed setting. Right-click its header for **Copy Card Settings**; Paste (`Ctrl+V`) then pastes that card alone.

**Reset to Roll**, beside the reset arrow, shows once a card differs from the roll. It puts the roll's values back on the card as one undo step; settings the roll never carried stay.

### The tab header

Tabs with several cards (Roll, Exposure, Look, Finish, Metadata) have a bar that reads **3 of 5 cards edited**. Its buttons act on every card: reset (asks first), **Reset to Roll**, one roll picker for the whole tab, and collapse/expand.

**Pick Better** (the red-green-blue balance scale at the left of the Exposure tab's bar) tunes Filtration, Tone and Paper Response: a separate window opens — a notch smaller than the main window — with three equal frames in a row: the current edit in the center, bracketed by the two candidates (the stronger on the left, the weaker on the right). Each frame is captioned above: "A" over the stronger left, "Skip" over the center and "B" over the weaker right. A hover draws a red ring around the frame under the cursor, in the Film Strip's selection style. The control the pair tunes shows as its name above the center "Skip" caption, prefixed by the round number, and stays there the whole time; the candidate values are not shown. Click a candidate to keep it; the next pair fills the same window. A left or right pick briefly shows the applied control's name and its delta above the frames. Click the center current photo to reject both candidates and move on to the next control. A **Difference** slider widens or narrows the spread between A and B live and keeps its setting for the next pair. The first eleven rounds each propose one control in the order set by **Custom Routing** — Grade, Density, Temperature, Dye Separation, Highlights Grade, Shadows Grade, Highlights Density, Shadows Density, Preflash, Snap and Toe by default — and two consecutive rounds never propose the same control; the later rounds cycle back through them, each visit a finer step. **Custom Routing** opens a window that reorders, by drag and drop, which control each round proposes, with a Randomize toggle that shuffles that order on each run — the order you set is the one used when Randomize is off, so turning it off restores it. The **OK** button (bottom-right) ends the mode; **Undo** re-shows the previous pair; the balance-scale toggle or `Esc` also ends it, keeping the last chosen settings. Luma Range Clip, Color Clip, Crop, Crosstalk, Cast Removal, Hue Trim and the Black and White Points stay at their current values.

### Menu bar (macOS)

`Ctrl` in this guide is `⌘` on macOS.

*   **NegPy**: Preferences… (`⌘,`), About and Quit.
*   **Window**: Minimize (`⌘M`), Zoom, Close (`⌘W`), Bring All to Front, and the open NegPy windows.
*   **Help**: Take the Tour, Keyboard Shortcuts, Customize Shortcuts, the Analysis panel guide, Report an Issue, Check for Updates.

Plain-key shortcuts such as `?` work but do not show in the menus. `⌘W` on the main window closes NegPy. Windows and Linux have no menu bar.

---

<!-- panel:frames -->
## 2. Library and film strip

The **Film Strip** under the canvas shows the open frames as strips of film, with the edge print and perforations of the film stock and format set in the Metadata card; each frame lies as it does on the film. The rebate takes the roll's mean print D-max, the deepest tone its thumbnails reach. The strip scrolls sideways, and its height sets the size of the frames; frames other than the selection are dimmed. The toolbar's **Roll** mode shows the roll's name and tally, the filter and the strip's actions; **Film Strip Guide…** in its **⋮** menu opens this guide. Your imported rolls are on the right panel's **Library** tab.

<!-- panel:library -->
### Your library

The **Library** tab, first on the right panel, lists every **roll** you imported: a named group of frames, not a live view of a folder. **Ctrl+L** opens it.

Each roll shows its name over a line with its photo count, film mode (the Film Strip's mode dot), film stock when Roll Settings set one, scenes and import date. The open roll is marked **Open** with a red bar. Double-click or **Enter** opens a roll; **⋮** on a row, or a right-click, offers **Open**, **Close Roll…**, **Roll Analysis**, **Rename…** and **Delete…**.

*   **Filter rolls…**: shows only the rolls whose name or line holds the text; the count under the list says how many show.
*   **Sort**: Name or Date, ascending or descending.
*   **Import**: **Import Folder as a Roll…** or **Import Subfolders as Rolls…** (below).
*   **⋮** → **Refresh**: finds new roll folders under each parent imported with **Import Subfolders as Rolls…** and recounts each roll's frames.
*   **⋮** → **Discovery Filters…**: folder names that importing and **Refresh** skip, with all their contents, one per line (default `export`). A line matches any part of a name, ignoring case; a line with `*` must match the whole name (`raw_*`).

A Trichrome triplet, stitch or HDR merge counts as one photo. A roll whose folder is gone shows **folder missing** in amber. Importing only records the folder; nothing decodes until you open the roll.

#### Importing

**+** (or the list's right-click menu) offers:

*   **Import Folder as a Roll…**: the folder becomes one roll and opens. A folder with no images of its own imports its subfolders instead. If its name matches a camera or film stock in your Gear library ("penf" finds "Pen F"), Roll Settings opens pre-filled.
*   **Import Subfolders as Rolls…**: every folder below the chosen one that holds images becomes a roll, without opening, except subfolders of a roll folder (export output). A roll is named by its path ("20260901/kentmere_400_1") under a folder row. Right-click a folder row for **Delete…**, which forgets every roll in it.

Importing never changes the folder. Reorganize on disk, then import again (or **Refresh**). Edits follow image content, so a moved file keeps its edit and marks.

#### Opening, renaming, deleting

**Double-click** a roll (or **Enter**) to open it in the Film Strip. NegPy asks first, since loading reads every frame (**Always load without asking** skips the prompt).

Right-click a roll for:

*   **Close Roll…** (loaded roll only): empties the Film Strip. Edits stay saved.
*   **Rename…**: renames the roll. A folder roll also offers **Also rename the folder on disk** (off by default). A cloud-sync folder (Dropbox, iCloud, OneDrive) can treat that rename as a delete and upload again.
*   **Delete…**: forgets the roll only; folder, images and edits stay. **Clear Library** in *Manage Database* forgets all rolls.
*   **Roll Analysis** (loaded roll only): runs Roll Analysis ([§10.6](#106-roll-analysis)).

#### Rolls that are not folders

A roll can also be a hand-picked set, and one photo can be in several rolls. Search the library or gather frames, then **Save as Roll…**. The set is fixed: add frames while it is loaded, or Save as Roll again.

A frame has one edit in every roll that holds it. On a frame in more than one roll, right-click → **Edit Independently in This Roll** gives it its own edit here; **Use the Shared Edit Again…** deletes that edit.

### Importing and managing files

**Nikon High Efficiency raw**: Z 8 and Z 9 NEFs in **HE** or **HE\*** use a licensed codec that NegPy cannot decode. Shoot **Lossless Compressed**, or convert with Adobe DNG Converter.

The toolbar's Roll row, from the left:

*   The roll's name over its tally of frames, the filter that hides any, keepers, rejects and the selection. **No roll** names frames that are not one roll, with **Save as Roll…** beside it ([Rolls that are not folders](#rolls-that-are-not-folders)).
*   The **filter box** ([Filtering the sheet](#filtering-the-sheet)). Inside it: the **regex** toggle, the **search-library** button and, once enabled in Preferences, the **search-by-meaning** toggle. If a filter hides everything, **Show all frames** clears it.
*   **Sort**: Name or Date, or **Scene** once the loaded roll has one, ascending or descending.
*   **Sheet filter**: *All Frames*, *Keepers Only*, *Hide Rejected* or *Unmarked Only*. **Advance After Marking** in the same menu moves on after a Keeper or Reject mark. `Home` and `End` jump to the first and last frame.
*   **Apply…**: copies the chosen aspects of the current frame's settings to selected frames or the whole roll. Crop and rotation stay per image.

In a narrow bar, Save as Roll moves to the **⋮** menu first, then Sort, Sheet filter and Apply show only their icons.

The **⋮** menu at the end of the row:

*   **Add Files…** or **Add Folder…** (or drop a folder on the window). A folder with no images of its own imports its subfolders as rolls.
*   **Save as Roll…**: keeps the loaded frames as a roll.
*   **Roll Settings…**: writes gear, capture, place, process and scanning metadata to the frame, a selection or the whole roll. **Load** fills the fields from a metadata preset; tick the groups to write. An empty Analog Gear is matched from the folder name.
*   **Update Thumbnails**: re-renders every stale thumbnail in the roll; **Cancel Thumbnail Update** while it runs.
*   **Hot Folder**: loads new files as they appear in the current folder, for a scanner or tethering app. While it is on, a flame shows in the row; click it to stop.
*   **Unload…**: drops the active frame or selection from the Film Strip. It is back the next time the roll opens.
*   **New Roll…**: clears the film strip, to drag in frames and keep them with **Save as Roll…**.
*   **Close Roll…** (**Unload All…** when the frames are not a roll): empties the film strip; edits stay saved.
*   **Reset Roll to Defaults…**: **Reset Settings** on every visible frame, each an undo step.
*   **Film Strip Guide…**: the Film Strip part of this guide.

**Remove from Roll…** (right-click, with a roll open): takes the frame or selection out of the roll for good, with its scene, card locks and own edit in that roll. The file and its shared edit stay. A file in the roll's own folder is skipped when the folder is opened again, until you add it back with **Add Files…**. A half-frame scan goes as one file.

**Trichrome Mode** and **Half Frame Mode** are on the Roll tab's Frame Assembly card ([§10.2](#102-frame-assembly)).

The grid button at the toolbar's right end opens the **Light Table** (`Shift+G`): the roll as strips of film on a light table for culling, with the same selection, marks and menus. It takes the place of the canvas and the Film Strip; the toolbar and the controls panel stay. `+` and `-`, or **Ctrl** and the wheel, make the frames larger or smaller, one frame a row at a time; the size is kept. **Esc**, `Shift+G` or the grid button goes back.

#### Filtering the sheet

A plain word matches the filename. `field:value` terms match frame data:

| Term | Finds |
|---|---|
| `film:portra` | frames whose film stock contains "portra" |
| `camera:"Nikon F3"` | quote anything with a space |
| `iso:>=400` | numeric fields also take `>`, `>=`, `<`, `<=` (`iso`, `frame`, `push`, `devtime`, `temp`) |
| `date:2024-03` · `date:>=2024` | by file date; a partial date is a prefix |
| `shot:1998` · `shot:>=1998-07` | by capture date from the Metadata panel |
| `place:tokyo` | by capture city, state or country |
| `devtime:>=9` · `temp:20` | development time in minutes, temperature in °C |
| `roll:` `developer:` `dilution:` `lens:` `format:` `scanning:` | the rest of the Metadata panel |
| `name:` `path:` `ext:tif` | file identity |
| `scene:beach` | frames in a scene of the loaded roll whose name contains "beach" |
| `keeper:` `rejected:` `edited:` | frames with that mark, or with a saved edit |
| `-rejected:` `-film:velvia` | a leading `-` negates any term |

Terms combine with AND (`film:portra iso:>=400 -rejected:`). Metadata fields match only once filled in the **Metadata** panel. The **regex** toggle makes the box a plain filename regex.

#### Searching by meaning

**Search by meaning** (Preferences → Performance) finds photos by content; it downloads a small model the first time. Turn on its toggle beside the filter box and describe the picture ("a photo of a dog"). Without an index it ranks only frames loaded this session.

#### Searching the whole library

The **search-library** button (or **Enter** in the box) searches the whole library and loads the results; with **Search by meaning** on, every indexed file. Keyword search reads only stored edits, so metadata matches only frames you filled in.

#### Indexing the library

With Search by meaning on, a **database** button beside the Library refresh button indexes every photo in your library. It runs only when you ask; an aborted run resumes where it stopped.

#### Stitching a frame from several shots

For a negative captured in overlapping pieces, select them and right-click → **Stitch Selected Frames**. NegPy aligns, matches and blends them into one composite, *a+b (Stitch)*. **Unstitch** restores the parts with their edits. **Merge Frame to TIFF Negative…** ([§10.2](#102-frame-assembly)) replaces the parts with one file.

For Trichrome, turn on **Trichrome Mode** first, then stitch the assembled frames.

#### Merging bracketed exposures (HDR)

For a slide with more range than one exposure, bracket it a stop apart, select the shots and right-click → **Merge Exposures (HDR)**. They become one frame, *a +4 (HDR)*; **Unmerge Exposures** restores them.

The merge is relative to the **reference**: the longest unclipped exposure, usually brighter than your metered shot. Choose the render exposure:

*   **Render exposure** (right-click a merged frame): pick a shot, listed in stops from the reference. Only the reference and shorter exposures are listed.
*   **Render Exposure** slider (Metering card): 0 EV (the reference) to −4 EV. It and a picked shot replace each other.
*   **Bracket middle (auto)** (default): the bracket's middle exposure, correct for a bracket centered on the metered shot.

A merge opens with **Shadows Density** above zero, from the shadow detail the bracket recovered; set it to zero to match the metered frame.

Bracket both ways, including the shot that already looks right. Longer frames (+1 to +3) extend the shadows; shorter ones (−1, −2) add render choices and keep a blown specular. To drop frames, drop long ones.

The merge exports under the first file's name with `-HDR` (`_DSC1715-HDR.jpg`).

Merging shows on Transparency frames only. B&W reversal (Scala, dr5, Fomapan R) is not supported. Merged, stitched and Trichrome frames cannot be merged.

### Triage (culling the roll)

Thumbnails are positives. Until you open a frame, it shows a quick inversion of a reduced preview. Transparencies are not inverted.

Right-click a thumbnail, or use shortcuts, to mark frames (multi-selection works):

*   **Keep**: a check badge.
*   **Reject**: a cross badge and dimming. Batch exports and sidecar writes skip it. The file never changes.

#### Reading the badges

| Corner | Badge | Means |
|---|---|---|
| Bottom-right | check | keeper |
| Bottom-right | cross, frame heavily dimmed | rejected |
| Bottom-left | *see below* | the frame is built from more than one file |
| Top-left | exclamation | the file failed to decode; click to retry |
| Top-left | small amber dot | the thumbnail is older than the frame's settings; open the frame or use **Update Thumbnails** |

The bottom-left glyph shows the frame type; its tooltip names it:

| Glyph | Frame |
|---|---|
| Two overlapping panes | a stitched composite ([§Stitching](#stitching-a-frame-from-several-shots)) |
| Three stacked bars | a merged bracket ([§Merging](#merging-bracketed-exposures-hdr)) |
| Three red/green/blue dots | a Trichrome triplet |
| A split rectangle, one side filled | one half of a half-frame scan |
| A split rectangle, both sides filled | a diptych: the whole scan, each half with its own edit |

The right-click menu also has:

*   **Copy/Paste Settings**, with or without normalization bounds (untick **Normalization bounds** in the paste picker to keep the frame's own). Paste writes every selected frame.
*   **Reset Settings**; with several frames selected, **Reset N Frames…**.
*   **Reset to Roll Settings**: **Reset to Roll** on every card that differs from the roll, as one undo step.
*   **Apply Settings…**.
*   **Sync Bounds…**: pushes only this frame's measured bounds (**Tonal span**, **Color balance**) to the selection or roll.
*   **Update Thumbnail(s)**: re-renders the selection's thumbnails. **Update Thumbnails** in the Roll row's **⋮** menu re-renders every stale one in the roll. Sharpening, chroma denoise, dust and heal repairs, demosaic, display profile and soft proof do not make a thumbnail stale.
*   **Reset Roll to Defaults…**, and per-frame export.
*   **Edit Independently in This Roll** / **Use the Shared Edit Again** ([Rolls that are not folders](#rolls-that-are-not-folders)).
*   **Show in Folder**: opens the system file manager on the frame's folder, with the file selected.
*   **Move to Trash…**: moves the selection's files and sidecars to the system Trash and unloads them; the edits stay, so a restored file keeps its edit. A file on a drive with no Trash stays. Stitches, HDR merges, trichromes and half-frame scans must be dissolved first.

#### Scenes

A scene is a group of frames in one roll shot in the same light. It has its own baseline, so its frames match each other, not the rest of the roll. Scenes need a roll (**Save as Roll…** first). On the Film Strip and the Light Table, an outline in the scene's color runs along the film's edge around each run of its frames.

*   **Scene** (right-click menu): **Group as Scene…** makes the selection a scene; **Add to** *name* and **Remove from Scene** move frames in and out. On a scene's frames, **Analyze Scene…** runs Scene Analysis; **Rename Scene…** and **Delete Scene…** manage it. A frame is in one scene at most. Deleting a scene keeps edits and baselines.
*   **Sort → Scene**: each scene's frames as a block, frames in no scene last.

---

<!-- panel:analysis -->
## 3. Analysis readout (always visible)

The readout sits above the Roll and Frame tabs and describes the current frame as you edit. Each tab remembers whether the readout is collapsed. Top to bottom:

#### Photometric curve

The paper characteristic (H&D) curve NegPy prints through: a model of the paper, not a curves editor. Horizontal is **negative density** (scene highlights to the right), vertical is **print tone**. Steeper means more contrast; the flat ends are the toe (shadows) and shoulder (highlights). The crosshair marks the **pivot** that contrast rotates around.

With a **Contrast Mask**, a violet band shows where large flat areas print; fine detail prints on the curve. Spatial tools (dodge/burn, CLAHE) do not show.

#### The two histograms

The gray **negative density histogram** shows the scan on the curve's horizontal axis; the colored **output histogram** shows the print, black left to white right. Contrast cannot separate data on the flat toe, so move the exposure onto the steep middle.

In Peek Negative the density histogram splits into R, G, B and luminance: a spike at an edge is that channel clipping, a trace apart from the others a strong cast.

#### Curve / Waveform / Parade / Vectorscope

The selector under the chart picks the chart. **Curve** is the paper curve and histograms above. **Waveform** plots print tone across the frame's width; a red tick marks a column that reaches paper black or white. **Parade** plots the print's R, G and B side by side, each channel's tone across the frame. A neutral sits at one height in all three, so judge a cast on neutrals; on neutral or even content, a channel that drifts across the frame is uneven light or a Flat Field mismatch. While you hover, a dashed line marks the pixel's green level in all three panels. In Peek Negative the Parade shows the scan: each channel's density in the camera's own channels (−log10 of the scan after any Crosstalk unmix, 0 at sensor full scale at the top, 3.0 at the bottom). On a negative, the solid lines are the range the stretch maps onto the curve, and the number beside each channel letter is that range. Scan exposure moves the traces (0.3 per stop) but not the range, so compare scans from one camera or scanner, light and unmix by their ranges. The dotted line is the clear film base: the Film Base set on the roll, else the base read from the rebate. A red tick marks a column with pixels at sensor clip (top) or in the axis's last step (bottom). **Vectorscope** plots the print's colors on the CIELAB a\*b\* plane, neutral at the center. On a color frame, a cluster off the center is a cast; on a toned B&W print, a toner draws an arm toward its hue.

*   **Parade Overlay** (layers icon): R, G and B on one plot, white where they agree. Grayed out under any Color vision choice but Standard (§14), and on the scan unless Base Relative is on.
*   **Base Relative** (ruler icon, Peek Negative): moves each channel so its film base, else its thin line, sits at the top, so the channels and the hover line compare at one height. The caption names the zero.

#### Lin / Log

Sets the count scale of the histograms, the waveform and the parade: **Log** shows thin tails (to find clipping), **Lin** the bulk of the frame. The Parade in Peek Negative keeps its own scale, **Log** by default, because the scan's thin and dense ends are small areas. On the Vectorscope it sets the chroma scale: **Log** (the B&W default) opens up the near-neutral center where a toner sits, **Lin** (the color default) keeps a color frame's spread in proportion.

#### Clipping triangles

R, G and B triangles in the top corners show crushed shadows (left) or blown highlights (right) once a channel passes 0.5% of the frame. One channel alone is a cast, not an exposure problem.

#### Clipping Overlay

The half-circle icon in the Analysis header marks on the photo every pixel with a channel at paper black or paper white.

#### Zone shading and zone ticks

The warm and cool washes mark the toe and shoulder, where separation is lost. The ticks on the left edge are Adams zones I to IX.

#### Step wedge

A 21-step wedge printed through the current curve, alternative process and toning. Patches that merge into black or white are lost tones; the brackets mark the usable span.

#### Zone strip

Eleven cells on the Adams scale (**0** paper black, **V** 18% mid-gray, **X** paper white), each zone rounded to the nearest as the Zone Overlay counts it; opacity shows how much of the frame lands in each. The two cells at each end turn **red** when shadows block up or highlights blow. Click a cell to start a Zone placement. The strip is disabled on a slide or a Positive frame.

Double-click the strip, or press `Shift+Z`, to toggle the canvas **Zone Overlay**. While it is up the toolbar shows its own row: the look, a legend with each zone's share of the frame, and **✕** (or `Esc`) to close it. **Color** tints each zone over the photo (I–IV cool, V gray, VI–IX warm, in your Color vision palette) and shows paper black and paper white as solid black and white; **Grayscale** draws the print in eleven gray steps; both number the larger regions. **Grid** lays a coarse grid over the photo with one numeral per region, red at paper black and paper white. Hovering the frame outlines the pointer's zone and rings its legend cell. Hovering a legend cell or a strip cell shows that zone alone, the rest of the frame dimmed, with the Zone Overlay on or off; the highlighter icon in the Analysis header turns this off for the strip.

#### Zone placement

Works like an enlarging analyzer: click a zone on the strip, then a spot on the photo, and NegPy solves the print so the spot prints on that zone. Up to three pins; − and + trim each pin's **target** in thirds.

*   One pin solves Print Density.
*   Two pins (usually shadow and highlight) solve Print Density and ISO-R Grade.
*   A third pin adds **Shadows Grade**, **Highlights Grade** or **Snap**, whichever can move that tone.

The result is a preview until **Place zones** (or **Enter**) commits it as one edit, which turns off Auto Density (and Auto Grade with two or more pins). **Esc** discards the armed zone, then the pins; **✕** removes one pin. Drag a pin to move it. An unreachable target shows the closest zone the print can make.

Pins are proofs, not edits: any other edit or a frame change removes them. Zone placement is off on an as-captured slide or a Positive frame.

#### Probe at Cursor

**Probe at Cursor** (**Overlays**, or `Shift+I`) is a spot densitometer in a chip beside the pointer: the print density, its zone and ΔD per channel. ΔD is density above the thin end of the normalization window. On a negative that end is the detected thin bound plus the Black Point offset, or the roll's bound under Roll Analysis; the rebate reads below zero. On a slide it is decoder white plus the White Point offset.

#### Readouts

The **Readouts** fold under the zone strip holds the negative stats; click its chevron or its name. It starts closed and keeps the state you leave it in. While it is closed, an amber dot marks a stat that warns.

#### Negative stats

Rows that measure the scan, not your edit; hover for details.

*   **Negative**: development character (lo = flat, ≈N−1; nrm = normal; hi = contrasty, ≈N+1), then Dmin · Dmed · Dmax above the clear base and Δ, the normalization window's density range. Comparable across a roll; an estimate, not a densitometer reading. The base is the one set with **Film Base** on the Metering card, else one read from the rebate; the hover names which, and without a base the row shows the character in full (flat, normal, contrasty) and Δ alone.
*   **Exposure**: approximate midtone in stops from neutral; positive is high-key, negative low-key.
*   **Clipping**: share of pixels crushed to black or blown to white, worst channel. Amber above 1%.
*   **Scan clip**: share of source pixels at or above sensor white. On a negative no edit recovers it: expose the scan lower. Amber above 1%.
*   **Repair**: share of the scan rewritten by IR Restore, dust detection and heals. A large value means the threshold is redrawing the picture. Amber above 5%.
*   **Gamut**: share of the frame the proof profile cannot print, while proofing. Amber above 2%.

---

## 4. Geometry tab

<!-- panel:geometry -->
### 4.1 Geometry: crop and straighten

Crop the picture and make it level.

**Crop:**

*   **Crop** tool: drag a rectangle on the picture. Drag a corner to resize it, the inside to move it, or outside the box to rotate. Drawing a crop turns Auto Crop off.
*   **Auto Crop** (the wand): finds the edges of the picture and crops to them. It is the same setting as on the Roll tab's Crop card ([§10.5](#105-crop)).
*   **Ratio**: the shape of the crop, for the whole roll. With **Free**, you can drag one side at a time.
*   **Guide**: composition lines, such as thirds. The rotate button turns them. **Reset** removes the crop.

**Alignment:**

*   **Straighten** tool: draw a line along the horizon or a vertical edge, and the picture turns to make it level.
*   **Fine Rotation**: turns the picture by small amounts. Positive is clockwise.
*   **Auto Skew**: lines the picture up with the edges of the film. It ignores what is in the picture, so a photo taken at a tilt stays tilted.
*   **Tilt** and **Swing**: straighten a building shot from below (Tilt) or a wall shot from one side (Swing). The reference-lines tool sets both from lines along the four film edges.
*   **Crop by Default**: crops away the empty corners that rotation, Tilt and Swing leave.

Crop before a large Tilt or Swing, or the film border can come into view and darken the print. Lens distortion is fixed in **Optics** ([§10.8](#108-optics)).

---

## 5. Exposure tab

These four cards set the brightness, contrast and color of the print.

<!-- panel:color -->
### 5.1 Filtration: color balance

Corrects the color of the print, as the color filters of a darkroom enlarger do. **Global / Shadows / Highlights** applies the color controls to the whole picture, or mostly to its dark or bright parts.

*   **Pick WB**: click something in the picture that should be gray, and NegPy corrects the color to make it gray.
*   **Temperature**: makes the picture warmer or cooler.
*   **Cyan / Magenta / Yellow**: shift the color between cyan and red, magenta and green, or yellow and blue.
*   **Ring-around** (`Shift+F`): shows the picture as a grid of slightly different colors. Click the one that looks right. `Esc` closes it.
*   **Cast Removal**: removes a color cast that differs between the dark and bright parts of the picture. It starts at 1 (full) on color negatives and at 0 on slides. Leaves, sky and water do not count as gray, so they keep their color.

<!-- panel:tone -->
### 5.2 Tone: brightness and contrast

How light or dark the print is, and how much contrast it has.

*   **Print Density**: how light or dark the print is (the darkroom's exposure time). Lower is lighter.
*   **ISO-R Grade**: contrast (the darkroom's paper grade). A lower number gives more contrast; about 110 is normal.
*   **Auto**: **Auto Density** and **Auto Grade** set brightness and contrast for each frame, so a roll prints evenly. A slider then shows the automatic value: move it to adjust, double-click it to go back. The Auto menu also has:
    *   **Set Targets…**: the brightness and contrast Auto aims for.
    *   **Bake Auto Density/Grade**: keeps this frame's automatic values and turns Auto off for it.
    *   **Hold Black**: when you lighten the shadows, the deepest blacks stay black.
*   **Test Strip** (`Shift+T`): a grid of versions at different brightness and contrast. Click the one you like. `Esc` closes it.
*   **Shadows Density** / **Highlights Density** (fold under Print Density): darken or lighten only the shadows or the highlights.
*   **Shadows Grade** / **Highlights Grade** (fold under ISO-R Grade): contrast in the shadows or the highlights only.
*   **Printing Aids** (fold):
    *   **Preflash**: brings back detail in the brightest areas.
    *   **Diffusion**: a soft glow; dark areas spread into bright ones.
    *   **Contrast Mask**: lowers overall contrast and keeps fine detail. Negative values add contrast. **Mask Spacer** sets how soft the mask is.
*   **Global / R / G / B**: R, G or B applies the grades to one color only, for a cast that differs between shadows and highlights.

**White Point** and **Black Point** are on the Roll tab's **Metering** card ([§10.4](#104-metering-negative--positive)).

<!-- panel:paper -->
### 5.3 Paper Response: the paper

The paper the picture prints on, and how it turns light into tones from black to white.

*   **Print stock**: the paper. A real paper sets the contrast curve and the colors from its maker's data. **Digital (Adobe RGB)**, the default, is an ideal paper. **Digital (Pakon Minilab)** has the colors of a Pakon lab scanner.
*   **Paper Test Strip** (the striped button): prints the frame on every paper. Click a paper to see it large, step with the arrow keys, and press **Keep** to use it.
*   **Dye Separation**: color strength in the print. 1 is unchanged. **Separation Damping** puts more of the change on dull colors and less on strong ones. **Chroma** on the Look tab changes all colors evenly instead.
*   **Paper White**: shows the white of real paper, a little darker than pure white.
*   **Paper Black**: shows the black of real paper, a little lighter than pure black.
*   **Curve Shape** (fold):
    *   **Snap**: midtone contrast. Black and white do not move.
    *   **Toe**: shapes the shadows. Positive lifts them, negative makes them deeper. **Toe Width** sets how far into the midtones it reaches.
    *   **Shoulder**: shapes the highlights. Positive softens them, negative brightens them and can lose detail. **Shoulder Width** sets how far it reaches.
*   **Global / R / G / B**: R, G or B applies the curve controls to one color layer.

<!-- panel:local -->
### 5.4 Dodge & Burn: lighten or darken areas

Draw a shape, then make only that area lighter (dodge) or darker (burn). A slide does not use this card, but its masks stay.

*   **Draw**: click to place points. Double-click, press Enter or click near the start to close the shape. Drag a point to move it, click a "+" on an edge to add one, and right-click a point to delete it.
*   **Oval**: drag out an oval. Its handles move, stretch and turn it.
*   **Card**: a burn that fades out, like a card moved over the paper. Drag from the full-strength edge (solid line) to where it ends (dashed line).
*   **Mask list**: click a mask to select it. Its icons turn it on or off, invert it (act everywhere except inside it), show its outline or delete it. The sliders below change the selected mask.
*   **Burn**: positive darkens the area, negative lightens it. The unit is stops: +1 doubles the light.
*   **Feather**: how soft the edge is.
*   **Grade**: contrast inside the mask. Negative gives more contrast.
*   **Flash**: brings back detail in bright areas inside the mask, like Preflash.
*   **Tone Limit**: **Highlights** or **Shadows** makes the mask act only on tones lighter or darker than **Tone Zone** (0 is black, V middle gray, X white). A sky burn then stops at the skyline. **Tone Softness** sets how gradually it starts.

**Printing Notes** (`Shift+N`) marks the masks on the picture with their numbers and values, as a printer's notes do.

---

## 6. Look tab

<!-- panel:lab -->
### 6.1 Lab: color and detail

The adjustments a lab scanner makes after the print.

*   **Chroma**: color strength. 1 is unchanged, 0 is black and white.
*   **Skin Protection**: keeps skin tones from getting too strong in color.
*   **Chroma Denoise**: removes colored speckles. Film grain stays.
*   **Sharpening**: sharpens detail without colored edges. Its fold holds **Method** (Unsharp Mask makes edges crisper; Deconvolution undoes the scanner's blur), **Radius** (the size of the detail, in pixels; judge it at 100% zoom) and **Masking** (sharpen only edges, so sky and skin stay smooth).
*   **CLAHE**: local contrast, to bring out detail. Strong values can look unnatural.
*   **Glow**: a soft glow around bright areas, like an old lens.
*   **Halation**: a red glow around bright areas, as some films give.

<!-- panel:altproc -->
### 6.2 Alternative Processes

Historic print processes for B&W negatives. Pick **None**, **Lith**, **Cyanotype** or **Sabattier**, and only that process's controls show.

#### Lith

Creamy, warm highlights and hard, deep blacks. The print stock on Paper Response sets the color. Only the Selenium and Gold toners work on a lith print.

*   **Exposure**: more gives warmer, more colorful highlights and softer tones.
*   **Snatch Point**: when the print leaves the developer. Higher gives deeper, colder blacks.
*   **Abruptness**: how suddenly the shadows turn black.

#### Cyanotype

A blue print with green highlights. Toners do not work on it; use Bleach and Tannin.

*   **Sensitizer**: **Classic** gives a light blue with green highlights. **New** gives deeper, cleaner blues.
*   **Exposure**: more makes the print bluer.
*   **Exposure Scale**: contrast. A shorter scale gives more contrast.
*   **Bleach**: removes blue, highlights first.
*   **Tannin**: turns bleached areas brown. Use Bleach first for a full brown.

#### Sabattier

A flash of light during development. The light tones reverse toward gray, and thin light lines (Mackie lines) appear along edges between dark and light.

*   **Strength**: the length of the flash. Above 1 the light tones reverse.
*   **Re-exposure**: where the reversal starts. Darker tones stay as they are.
*   **Agitation**: less agitation gives wider Mackie lines.

---

<!-- panel:toning -->
### 6.3 Toning

Toners are chemical baths that change the color of a B&W print. Split Toning adds color to any print.

**Chemical Toning** (B&W negatives) acts in the order shown:

*   **Selenium**: deeper, cooler blacks.
*   **Sepia**: warm brown, from the highlights down.
*   **Gold**: blue-black. Over sepia, it gives orange-red highlights.
*   **Iron Blue**: blue shadows and navy blacks.
*   **Copper**: pink to brick red. Blacks get weaker.
*   **Vanadium**: green midtones and highlights. Blacks stay black.

On a lith print only Selenium and Gold work. On a cyanotype no toner works.

**Split Toning** (all prints): **Shadow Strength** and **Highlight Strength** add color to the shadows and the highlights. **Shadow Hue** and **Highlight Hue** pick the color, and show once the strength is above 0.

---

## 7. Finish tab

<!-- panel:retouch -->
### 7.1 Retouch: dust, hairs, scratches

Removes dust, hairs and scratches. Each repair is rebuilt from the clean film around it.

*   **Overlay**: **Marked** shows what dust removal found, **IR** the scan's infrared channel.
*   **Optical Removal**: finds dust and hairs by itself. **Spot Threshold** and **Hair Threshold**: lower finds more but can remove real detail; 1 is off. **Size**: the largest dust to remove. To protect an area, right-drag over it or right-click a mark; the cursor button skips the right-click menu.
*   **IR Removal** (scans with an infrared channel): finds dust in infrared, where the picture does not show. **IR Threshold**: lower finds more. **Method**: **OpenICE** keeps more fine detail than **NegPy** but is less tested. B&W and Kodachrome are skipped: their picture shows in infrared too. The channel comes from 4-channel TIFF and DNG scans or an `_IR.tif` file beside the scan.
*   **Heal**: click or paint over dust. Only marks that stand out are repaired, so paint generously.
*   **Scratch**: click points along a scratch or hair, then press Enter.
*   **Line**: click once on a long straight scratch, and NegPy finds and repairs the whole line. **Line Sensitivity**: lower finds fainter lines.
*   **Brush Size**: also `Alt`+scroll on the picture.
*   **Clone**: copies film from another area over a defect Heal cannot fix. The first click (or `Alt`-click) picks the source; then paint. **Set Source** picks a new one. **Match Tone** takes the brightness and color around the defect. **Strength** sets how much it covers, **Feather** how soft its edge is.
*   **Undo Last** and **Clear All** remove manual repairs; right-click one on the picture to delete it.

<!-- panel:finish -->
### 7.2 Finishing: vignette, carrier, border

How the print is presented. The other sliders of each effect show once its first slider is not 0.

*   **Vignette**: **Burn** darkens (positive) or lightens (negative) the edges. **Size** sets how far it reaches. **Roundness** goes from round (0) to the shape of the print (1).
*   **Filed Carrier**: **Width** draws a rough black frame around the picture, as a darkroom negative carrier that was filed wider does. **Roughness**, **Flare** (a gray glow outside the frame) and **Corners** shape it.
*   **Border**: **Width** puts a mat around the print. **Bottom Weight** makes the bottom wider, as on a framing mat. **Color**: **Paper White** matches the paper, **Custom** uses a color you pick.

---

## 8. Favorites tab

The sliders you use most, in one place; empty until you fill it.

*   **Edit Favorites**: tick sliders on the left, drag them into order on the right, then press **Apply**.
*   They are the same controls as in their home panels; a favorite hides when its original does.

<!-- panel:presets -->
### Presets

Saves and recalls edit settings by name.

*   **Apply** (or double-click a preset): applies the selected preset to the current image.
*   **Save…**: pick which of the current settings to store as a new preset.
*   **Pen** and **Trash**: edit or delete the selected preset.

---

## 9. History tab

Two cards: the versions you chose to keep, above the record of every change.

<!-- panel:work_prints -->
### Work prints

A **work print** is a named version of this frame, like the test prints kept on the way to the final one.

*   **Save Work Print…** (**Ctrl+Shift+S**) keeps the current edit under a name.
*   **Click** one to make it live. That is an edit, so **Ctrl+Z** restores the previous state.
*   **⋮** on a row, or a right-click, for **Export This Version…**, **Rename…** or **Delete…**.
*   **Load Metadata** (off by default; a global setting, the same for every frame and roll) restores a work print's saved metadata when you load it; off keeps the metadata on screen now and ignores the print's. It shows once the frame has a work print.

Work prints are never pruned. They live in the database, not in `.negpy` sidecars.

<!-- panel:edit_history -->
### Edit history

Every edit step, newest on top; NegPy keeps the last 100. Each step names the card it changed and, within one card, the controls ("Filtration · Magenta, Yellow"); the first is **As opened**.

*   **Now** marks the current step. After an undo, the steps above it are struck through and marked **Undone** until the next edit replaces them.
*   **Click** a step to jump to that state; the undo and redo arrows in the card's header step one at a time.
*   **⋮** on a row, or a right-click → **Export This Version…** to export a past state.

---

## 10. Roll tab

These cards hold what the frames of a roll share: the film, how it was scanned, the crop shape and the roll's measurements. Each card has the Frame / Roll pair ([§1](#frame-or-roll-the-scope-pair)). The line above the cards lists the cards this frame changes for itself.

<!-- panel:film -->
### 10.1 Setup

What the film is and how you scanned it. These choices decide which cards and controls show.

*   **Color / B&W / Slide**: color negative (C-41), black-and-white negative, or slide (E-6 and similar).
*   **Positive** (Slide only): for a file that is already a positive, such as a scanned print or another app's export. NegPy then skips inversion and metering.
*   **Camera / Film Scanner**: what you scanned with. NegPy reads it from each file (a camera RAW is a camera) until you pick one. Your pick holds for every frame and sets the Scan tab's scanner.
*   **White Light / Narrowband RGB** (not for B&W): the light behind the negative. White light is a lightbox or LED panel. Narrowband is a light with pure red, green and blue, such as a Scanlight.

The scanning choices are one setting for the whole app. They set how a RAW file is decoded and which digital print stock is used:

| Scanned with | Light | Decode | Print stock |
| --- | --- | --- | --- |
| Camera | White | Camera WB | Digital (Adobe RGB) |
| Camera | Narrowband | Linear RAW | Digital (Pakon Minilab) |
| Film scanner | White | Linear RAW | Digital (Adobe RGB) |
| Film scanner | Narrowband | Linear RAW | Digital (Pakon Minilab) |

A camera shows the Raw Decode and Optics cards. A camera with narrowband light also shows Trichrome and Calibration. A change updates every open frame (Ctrl+Z undoes it per frame), but a print stock you picked yourself stays. A camera Scan sets the decode and the print stock for each frame from its own light.

<!-- panel:assembly -->
### 10.2 Frame Assembly

How files become frames. Each roll keeps its own settings here.

#### Trichrome

For a camera with narrowband light that takes three shots of each frame: red, green and blue.

*   **Trichrome Mode**: joins the three shots into one color frame. Shots are grouped by capture time (or file name), so take each frame's three shots one after another. Shots that do not group stay separate.
*   **Edit Triplet…**: pick the three shots of the current frame by hand. **Align channels** lines them up to remove color fringes.
*   **Merge Frame to TIFF Negative…** (right-click): saves a triplet or a stitch as one TIFF beside its first source file, with its edit. An option moves the source files to the Trash.

#### Half Frame

**Half Frame Mode** splits each scan into two frames, for half-frame cameras. Each half has its own edit.

*   **Adjust…**: drag the green box to crop and the orange line to set the split. **Split direction** and **Cut thickness** set the gap, **Auto-detect** finds them again, and **Apply** saves to this frame, the selection or all frames.
*   **Detect All**: finds the splits on every scan again.
*   **Unsplit** (on a split frame): makes it one frame again and deletes both halves' edits.

Right-click a half for **Adjust Split for This Frame…** and **Reset Split to Roll Default**. Turning Half Frame off keeps edited halves side by side as a **diptych**; turn it on again to edit them.

<!-- panel:sensor -->
### 10.3 Calibration: colors from your scanning setup

Corrects color errors that come from your light, camera and film.

**Single-Shot Narrowband Calibration** (camera with narrowband light, Linear RAW): removes the color that leaks between the sensor's channels. Run **Roll Analysis** again after a change.

*   **Profile**: the sensor profile. Your own `.toml` profiles go in `<Documents>/NegPy/sensor/`.
*   **Method**: **Two-Scale** (default) removes the leak and keeps very strong colors from speckling. **Linear** is exact, but strong colors can speckle. **Density** has no speckle, but strong colors are a little duller.
*   **Calibrate**: makes a profile from three shots of the bare light (red, green and blue), from files or a tethered camera (see CAMERA_SCANNING.md).

**Crosstalk** (color film): film dyes, your light and your sensor mix the colors a little, and a matrix separates them again. Run **Roll Analysis** again after a change.

*   **Matrix**: the matrices for this film type. Those marked *(approx)* come from film data sheets and are a starting point. Your own `.toml` files go in `<Documents>/NegPy/crosstalk/` (see CROSSTALK.md). The slider button opens the editor; **+** makes a new matrix. No slide matrix comes with NegPy.
*   **Strength**: how much of the matrix to apply.
*   **Measure from Chart…** (color negatives): measures a matrix from a ColorChecker 24 or SpyderCheckr 24 shot on the film. Drag the four dots onto the corner patches.

**Hue Trim** (camera with narrowband light): turns all colors around the color wheel, for a light that makes yellows orange or greens olive. Keep 0 for white light. It also works on slides, where the sensor profile does not.

<!-- panel:process -->
### 10.4 Metering: negative → positive

To turn a negative into a positive, NegPy measures its darkest and brightest parts (the black and white points) and the color of the film. These controls set what it measures.

*   **Reanalyze Frame**: measures this frame again from its current crop.
*   **Draw Region**: draw an area, and NegPy measures only that area. Double-click inside to confirm; **×** clears it.
*   **Film Base**: click the clear film between frames to set the roll's film base, for the Analysis readout. **×** clears it.
*   **Analysis Buffer**: ignores a border around the frame when measuring, so film edges and holders do not count.
*   **Clipping**: how much of the print is pure black or pure white.
*   **Lock Bounds**: keeps this frame's black and white points, even when the crop or Roll Analysis changes.
*   **Luma Range Clip** (fold): how tightly black and white are set. Positive gives more contrast, for dense or foggy negatives. Negative keeps more shadow and highlight detail.
*   **Color Clip** (fold): how tightly the color balance is set.
*   **White Point** / **Black Point** (fold): move the measured white and black points. A positive white point brightens the print; a positive black point lifts the blacks. **R / G / B** moves one color only.

A **slide** needs no inversion: the tone controls shape the picture directly. Auto Density and Auto Grade start off; turn them on for a faded slide. In Lightroom terms, Exposure is Print Density (lower is brighter), Contrast is ISO-R Grade, and Shadows and Highlights are Shadows and Highlights Density.

<!-- panel:autocrop -->
### 10.5 Crop

The crop shape for the whole roll, and how NegPy finds each frame. Each frame's own crop is in **Geometry** ([§4.1](#41-geometry-crop-and-straighten)).

*   **Ratio**: the crop shape, such as `3:2` or `1:1`, turned to fit each frame. **Free** uses the shape NegPy finds. **Detect** picks the nearest standard shape.
*   **Mode**: **Image only** crops to the picture. **Film edge** keeps the whole film with its border and holes.
*   **Crop Offset** (fold): moves the crop inside (positive) or outside (negative) the found edge.
*   **Rebate Trim** (fold, Image only): how far the crop cuts into the film border. 0% stops at the film edge and 100% at the picture edge; above 100% cuts into the picture to remove a white border.
*   **Auto Crop** (the wand): finds the edges and crops each frame. New frames start with this setting. A crop you draw turns it off for that frame.
*   **Square Before Crop**: straightens each frame to its film edges before Auto Crop crops it.
*   **Auto-crop all frames** (Image only): crops every frame together. Clear frames help unclear ones, and crops you drew stay.

Auto Crop needs the scanner light or holder to be the brightest part of the scan. It leaves a frame alone when the picture is as bright as the light, or when the next frame fills a large part of one side. Crop such a frame by hand, or use **Film edge** and trim in.

<!-- panel:baseline -->
### 10.6 Roll Analysis

Measures the whole roll once and shares the result, so the frames of one film print alike.

*   **Reanalyze**: measures every loaded frame (except scene and locked frames) and saves the average as the roll's baseline. Frames very different from the rest keep their own. Run **Auto-crop all frames** first.
*   **Use This Frame**: makes this frame's measurement the roll's baseline.
*   **Use average**: **Luma** uses the roll's black and white points, **Color** the roll's color balance, and **Cast** (color negatives) the roll's gray balance for Cast Removal. With Luma and Color on, the roll prints evenly; with both off, each frame is measured on its own.
*   **Baseline**: says where the baseline came from (roll, scene or frame). It warns when there is none or when it is out of date.
*   **Rolls**: pick another roll's saved baseline. A ticked roll has one.
*   **Scenes**: groups of frames with their own baseline, such as one subject under one light ([Scenes](#scenes)). **Analyze** measures the scene, **Select** selects its frames and **Delete** removes the group.

<!-- panel:demosaic -->
### 10.7 Raw Decode

How a camera RAW file is turned into pixels. Shown for a camera.

*   **Camera WB / Linear RAW**: Camera WB uses the camera's white balance. Linear RAW decodes neutral, for narrowband light. Setup sets it for you.
*   **Preview** / **Export**: the demosaic method, which fills in the colors each sensor pixel cannot see. **Auto** is fast on screen and uses **AHD** for export. **VNG** is smooth and **PPG** fast. **DCB** and **DHT** keep more fine detail but can turn grain into patterns. **AAHD** softens edges. Only the methods in your LibRaw build are listed.
*   **Recovery** (slides): rebuilds blown highlights in a camera RAW. **Blend** suits sun and sky. **Reconstruct** is stronger but can get the color wrong.

<!-- panel:optics -->
### 10.8 Optics

Corrections for the lens and the light, the same for every frame you scan with this setup. Shown for a camera.

#### Lens Correction

*   **Embedded**: uses the file's own lens correction (DNG, Sony ARW, Panasonic RW2). **Distortion** straightens curved lines and **CA** removes color fringes. Set it before you crop or retouch.
*   **Distortion Correction**: straightens lines that bow out (positive) or in (negative). Use the film edge as a straight guide.

#### Flat Field Correction: even out the light

Removes uneven light, such as darker corners, with a shot of the bare light source.

*   **Profile**: **+** saves a shot of the bare light as a named profile. The trash button deletes it, and every frame that uses it loses its correction.
*   **Apply Flat Field**: applies the selected profile to this roll.
*   **Check Flat Field**: shows how well the profile evens out its own shot. Even gray is good; a band or patch shows where it is off.

A new profile becomes the default for the next roll.

---

## 11. Metadata tab

Metadata for the original analog capture (camera, lens, film, process), written into every export as EXIF and XMP, so a DAM such as Lightroom shows your film gear, not the scanner.

**Metadata Preview** is pinned on top: fold it to its header, or drag the grip under it to set its height. Under it, **Shot** holds Analog Gear, Capture and Exposure, and **Process** holds Process and Scanning; a dot marks a tab with an edited card. The two icon tabs after them are **Presets** and **My Gear**.

**Analog Gear**, **Capture**, **Process**, **Scanning** and **Exposure** are roll-wide by default ([§1](#frame-or-roll-the-scope-pair)). The frame number is always per frame.

<!-- panel:metadata_gear -->
### Analog Gear

Searches your own gear (the **My Gear** tab). **Other…** opens the full built-in catalog.

*   **Camera / Lens / Film stock**: empty means not set.
*   **Clear**: empties all three.
*   **Infer from folder name**: fills unset camera, film stock, ISO and capture date from the folder name; an ambiguous field stays empty.

<!-- panel:metadata_capture -->
### Capture

*   **Date**: `1998`, `1998-07`, `1998-07-14` or `1998-07-14 16:30`, with an optional offset such as `+02:00`. EXIF pads a partial date; XMP keeps the short form. The scan's own timestamp moves to `DateTimeDigitized`.
*   **Place**: the map-pin button opens a map; the field also takes a coordinate pair or an OpenStreetMap/Google Maps link. A place replaces the source's GPS; with none set, a geotagged source keeps its own. The map contacts OpenStreetMap.

<!-- panel:metadata_process -->
### Process

*   **Saved process**: a library recipe that fills Developer, Dilution, Push / Pull, Time and Temperature. Typing over one unlinks it.
*   **Format**: `—` (not set), `35mm`, `120`, `4×5`, `8×10`, `110`, or `Other` (free text).
*   **Developer** and **Dilution**: for example `D-76` and `1+1`.
*   **Push / Pull**: `Push +3` … `Normal` … `Pull -3`.
*   **Time** and **Temperature (°C)**: time as `9:30` or minutes; searchable as `devtime:` and `temp:`.
*   **Clear**: empties the saved process and its fields. Format stays.

<!-- panel:metadata_scanning -->
### Scanning

*   **Saved setup**: a library digitizing setup that fills Scanning. Typing over it unlinks it.
*   **Scanning**: scan method or notes. EXIF `Software` is always `NegPy`.
*   **Clear**: empties the saved setup and the note.
*   **Roll / Frame**: the capture roll name and frame number, stamped on capture; filename template fields `{{ roll }}` and `{{ frame }}`.
*   **Sequence…**: assign a running capture frame number to the selected frames or the whole roll, in film order. Set a start number, a step and ascending or descending order, and each frame gets its own number. Tick **Skip Rejected Frames** to leave frames in the rejected state out of the run.

<!-- panel:metadata_exposure -->
### Exposure

Optional original shutter, aperture and ISO. Click the lock to edit a free-text string such as `1/125s f/2.8 ISO 400`.

<!-- panel:metadata_preview -->
### Metadata Preview

A live view of what goes into the file. The shield in its header, **Protect Original Metadata**, copies the source's own EXIF/XMP and resolution unchanged instead, and grays out the Shot and Process cards. **Description…** picks the fields joined into EXIF `ImageDescription` (default: camera, lens, film stock, ISO); the choice becomes the default for frames without their own.

Capture gear goes to standard EXIF and the digitizing rig to `negpy:Scan*` XMP tags; with gear unset, your scanner or DSLR stays in EXIF. Other XMP tags: `photoshop:DateCreated` (with `negpy:CaptureDatePrecision`), `photoshop:City`/`State`/`Country`, `exif:GPS*` (the only GPS in a TIFF), `negpy:DevelopmentDilution`/`DevelopmentTime`/`DevelopmentTemperature`, `negpy:CaptureRoll`/`CaptureFrame`. A star rating set in the camera carries over as `xmp:Rating`.

<!-- panel:gear_items -->
### My Gear

Your gear library, for Metadata, Roll Settings and every gear picker. **Category**: **Cameras**, **Lenses**, **Film Stocks**, **Process** (a development recipe) or **Scanning** (a digitizing setup). Your gear is saved to `~/NegPy/gear/`.

*   **+**: copy an item from the built-in catalog into your list, or **Add Custom** to enter one by hand.
*   **Catalog**: also shows the built-in reference models. Off by default.
*   **copy / trash**: duplicate or delete the selected item. Built-in entries cannot be deleted.

<!-- panel:gear_presets -->
### Presets

Saved sets of metadata values in `~/NegPy/presets/metadata/`. Each row names the fields its preset stores.

*   **Apply to This Frame**: writes the selected preset's fields onto this frame; other fields stay. Off while Protect Original Metadata is on.
*   **+**: stores the current frame's metadata under a name.
*   **⋮** on a preset, or a right-click: apply, duplicate, edit or delete it.
*   **Details**: edit the selected preset's fields in place; the pen renames it or changes which fields it stores. Per-frame fields (capture date, place, description) are read-only here. **Notes** is free text.

Gear applies as one unit (camera, lens, film stock, format). A film stock sets the format, so set a frame format such as `6×7` after the stock. Presets never store the frame number.

---

## 12. Export tab

**Export** is pinned at the bottom of the tab. Above it, **File** holds the output settings and **Proof** the soft proof, with a dot while Proof on Screen is on. The two icon tabs after them are **Presets** and **Alongside Exports**.

### Output intent

*   **Print** (default): the look you see on screen.
*   **Flat**: a neutral, low-contrast master for editing elsewhere. It skips the print look, effects, toning and vignette, and writes a 16-bit TIFF, or lossless JPEG XL when JXL is selected with sRGB, P3, Rec 2020 or Grayscale.
    *   **Preview Flat**: shows the flat master on the canvas.
    *   Run **Roll Analysis** (Roll tab) before a flat batch so the masters match.
*   **Linear**: writes the decoded buffer as linear 16-bit, with rotation, flip and only the corrections turned on below. **TIFF** (default, untagged) or **JPEG XL** (lossless; tagged with sRGB primaries, which is wrong for native primaries). **Effort** (1 to 9, default 7) trades JPEG XL speed for size.
    *   **LinearRaw DNG**: SilverFast HDRi (3-channel) and VueScan (4-channel RGB+IR). IR goes to a separate grayscale `_ir` file.
    *   **Camera RAW**: demosaiced at unity white balance with the Raw Decode card's Export algorithm (§10.7); as-shot WB goes to XMP (`RAW-WB: R G B`). Trichrome triplets merge into one TIFF.
    *   **Coolscan NEF**: not raw sensor data but the Nikon Scan output; the full-resolution RGB is written.
    *   **Flextight FFF**: 16-bit RGB and LogLuv raw (`.3fr`/`.fff`); FlexColor metadata is kept.
    *   **Noritsu RAW**: headerless BGR 16-bit dumps; size detected from file size.
    *   **TIFF**: IR (a 4th channel, an `_ir.tif` sidecar or a second page) goes to a separate `_ir` file. **Input gamma** (linear, 1.8, 2.2 or sRGB) linearizes the data.
    *   **Expansion**: scales the data before writing. Defaults: Pakon RAW 4× (the 16-bit F335 off), Noritsu RAW 16×, LinearRaw DNG off. Camera RAW, Coolscan NEF and Flextight FFF have none.
    *   **IR Dust Removal** (when IR exists): IR dust and scratch correction. Off by default.
    *   **Corrections** (camera RAW only, all off): **White Balance** (as-shot gains), **Flat Field**, **Sensor Correction** (crosstalk unmixing). Stitch composites always get Flat Field and sensor correction per part.
    *   **Lens Correction** (off; shown when the frame has a lens profile or a **Distortion Correction**): applies the **Optics** correction (§10.8). The embedded profile needs a single camera RAW; Distortion Correction skips half-frame scans.

    Files take `_linear` (then `_linear_2`… without **Overwrite Existing Files**), so a source is never overwritten. The file carries no ICC profile. **Abort** stops after the current frame.

### Format / Size / Color Management / Destination

*   **Format**: `JPEG`, `TIFF`, `PNG`, `JPEG XL` or `WebP`, each with quality or effort options. JPEG XL supports only `sRGB`, `P3 D65`, `Rec 2020` or `Grayscale`.
*   **Bit Depth**: `8-bit` or `16-bit` (TIFF, PNG, JPEG XL).
*   **Compression** (TIFF): `Uncompressed`, `LZW` or `ZIP`, all lossless; ZIP is usually smallest.
*   **Compression** (PNG): `0` to `9`, lossless; higher is slower and smaller.
*   **Progressive** (JPEG): renders in passes while it downloads.
*   **Input ICC**: treats an untagged source as this profile (primaries only; a LUT profile's input curves still apply).
*   **Export profile**: the space the file is converted to and tagged with: `Same as Source` (Adobe RGB for an untagged scan), `sRGB`, `Adobe RGB`, `ProPhoto RGB`, `P3 D65`, `Rec 2020`, `Grayscale` (true B&W), or an imported printer or paper ICC, embedded in the file. A warning shows when the soft proof targets a different profile than the export.
*   **Import ICC**: copies a `.icc`/`.icm` into `~/NegPy/icc/`. A file named after a built-in space (`sRGB.icc`) replaces that space everywhere, after a confirmation.
*   **Paper Aspect Ratio**: final print ratio, or *Original* (no resize).
*   **Resolution**: *Original* (full resolution), *Print* (long-edge **Size** in cm plus **DPI**) or *Pixels* (**Long edge** in px). The DPI tag is your value (*Print*), the value the long edge implies (*Pixels*), or the source's, else the **DPI** field (*Original*).
*   **Sharpening** (0.0 to 1.0, *Print* and *Pixels*): sharpens the export after the resize, to restore the edge contrast that scaling down removes. It adds to the Lab **Sharpening** and does not show in the preview.
*   **Destination**: **Filename Pattern** (a Jinja2 template; see [TEMPLATING.md](TEMPLATING.md)), **Overwrite Existing Files**, and the location: subfolder of source (default, `export`), same as source, or an **Export Path**. A roll with no single source folder exports under its own folder in NegPy's data folder.

### Export button

**Export** stays at the bottom of every sub-tab. Its chevron picks the scope: current frame (Ctrl+E), selected frames or all visible frames. For several formats or sizes in one run, use Export Presets. A batch with unedited frames asks first, since they may not match their thumbnails. After the batch, a warning names exports that rendered almost black with no crop set, where the bright scan border drove automatic levels.

<!-- panel:export_presets -->
### Presets

Saved Format/Size/Color Management/**Destination**/filename recipes. Each preset is a toggle; **Manage** edits them. **Export Presets** renders the frames with every preset turned on, each to its own destination. Presets are off while the output intent is Linear.

<!-- panel:export_alongside -->
### Alongside Exports

Three jobs beside the print, each with a switch on the left and a one-shot action on the right. Linear output has no bake and no sidecars.

*   **Printing Notes**: the printer's record for this frame, as described under Dodge & Burn. **Preview** shows it on the canvas (**Shift+N**); **Export Notes** writes it as an image beside the print.
*   **Auto Density / Grade**: **Bake on Export** is an app-wide switch, the same on every frame: when on, every export freezes Auto Density and Auto Grade into fixed values for the frames it has metered, so the saved edit does not re-run the meters. **Bake to Roll** freezes them for every visible frame now, metering a frame it has not seen first. A frame with both helpers already off, or a composite or a roll fork, keeps its edit.
*   **Edit Sidecars**: **Save on Export** writes a `.negpy` sidecar next to each source on export. **Export Sidecars** writes them for all visible frames at once. Edits always stay in the database too. A frame with no edit in the database takes its sidecar when its folder opens. **Load Edit from Sidecar…** (right-click a frame) replaces the frame's edit with a chosen `.negpy`, as one undo step.

<!-- panel:contact_sheet -->
### Contact Sheet

On the **Alongside Exports** tab.

A darkroom proof of the roll: every visible frame at true size, as cut film strips on photographic paper, in capture order. The rebate, perforations and edge print follow the frames' **Film stock** and **Format** metadata.

*   **Path**: the folder for the sheets. Empty follows the export destination.
*   **Contact Sheet…**: opens the proof. Drag an edge or corner of the paper to resize it; a size near an Ilford sheet snaps to it.
*   **Format**: 35mm, 35mm Half Frame or 120. **Frame size** sets the 120 camera's frame (6×4.5 to 6×17).
*   **Paper**: an Ilford sheet size, or Custom. The default, 24 × 30.5 cm, holds a whole 36-exposure roll.
*   **Width** / **Height**: the paper size, 50–610 mm.
*   **DPI**: 150, 300 or 600, tagged so the sheet prints at true size.
*   **Order**: **Date**, or **Scene**, where each scene starts a new strip.
*   **Print**: **As Edited**, or **Straight Proof**: the whole roll at one exposure on grade 2 from its Roll Analysis baseline, so thin and dense negatives print light and dark. It needs the roll scanned at one exposure.
*   **Pick Frames**: click a frame to leave it out or put it back; rejected frames start out.
*   **Edge Print**: the maker's markings on the film edge (stock name, frame numbers, DX barcode). A built-in stock prints its own codes and DX number where they are known, a cine stock or its respool its KEYKODE numbers and barcode; other stocks get the maker's usual layout with the stock name.
*   **Roll Label**: the roll name, film, developer, camera and date above the strips.
*   **White Paper**: white paper in place of the darkroom black, to save ink on a home printer.
*   **Film Base** (on): prints the film base black, as a darkroom contact print. Off prints it as paper with the strip outlined, to save more ink.

Sheets are JPEGs named `contact_sheet.jpg` (`contact_sheet_1of2.jpg` and on when the roll needs more sheets), with the **JPEG Quality** and **Progressive** settings of the File tab.

<!-- panel:soft_proof -->
### Soft Proof

The **Proof** tab. Preview only; exports are never proofed. Paper is dimmer and has a smaller gamut than a screen, so a correct proof looks worse than the plain preview.

*   **Proof on Screen** (`Shift+P`, on by default): master switch.
*   **Preset**: a saved printer and paper setup; **None** proofs the export target with no paper simulation.
*   **Profile**: follows the **Export profile** until you pick a printer or paper, so you can proof a print while you export a web JPEG.
*   **Intent**: **Relative Colorimetric** keeps printable colors and clips the rest. **Perceptual** compresses everything so color relations survive; try it on saturated frames. **Saturation** is for charts, not photographs.
*   **Black Point Compensation** (off): maps the darkest tone to the paper's black in place of clipping.
*   **Simulate Paper White** (off): shows the paper's white and tint.
*   **Simulate Ink Black** (off): shows the paper's real black; shadows lift.
*   **Gamut Warning**: shows unprintable colors as gray.
*   **Display**: the monitor profile, auto-detected; set it by hand if detection fails.

---

## 13. Scan tab

Capture film directly into NegPy. The **Scanner** card picks the scanner; the tab shows its cards, the shared **Output** card and the **Scan** button.

<!-- panel:scan_source -->
### Scanner

*   **Scanner** (Camera by default): **Film Scanner** drives a dedicated film scanner (Device, Film & Quality, Framing); **Camera** drives a camera on a copy stand (Camera, Preset).

<!-- panel:scan_device -->
### Device

**Backend**: **SANE** (Linux/macOS), **Nikon Coolscan (nkscan)** (Linux, Windows, macOS) or **pyOpticfilm (Plustek)** (all three OSes). Controls follow what the device reports.

*   **Device**: the scanner; the arrows refresh the list. The eject menu holds **Eject Now** and, on a strip feeder, **Eject When Done** (on by default), which returns the strip after a batch. Off keeps it loaded with its picks and previews. A strip the scanner returns by itself counts as an eject: insert it again, then **Detect frames**. After 9 minutes with no scanner activity NegPy measures the strip again.
*   **Debug log** (nkscan; Off, Debug, Trace): writes `nkscan.log` in the NegPy folder. For a bug report, set Trace, reproduce the problem and attach the file.
*   **Sleep**: while a scan runs, NegPy keeps macOS and Windows from going to sleep. On Linux, turn off automatic suspend before a long roll.

**pyOpticfilm (Plustek)**: the **OpticFilm 8200i SE** (`07b3:1825`), **8100 V2** (`07b3:1824`), **8300i SE** (`07b3:181f`) and **7600i v1** (`07b3:0c3b`) scan; for other models try **SANE** on Linux and macOS. Needs pyopticfilm **1.3.6** or later. **IR** comes in the same pass (on the 7600i v1, at 3600 and 7200 dpi only). Multi-Pass and Prescan are on the GL128 models. On Windows, bind the device to **WinUSB** with Zadig first ([PLUSTEK_WINDOWS.md](PLUSTEK_WINDOWS.md)). From source, install with `uv sync --group plustek` or `pip install negpy[plustek]`.

**Nikon Coolscan (nkscan)**: needs no SANE and ships in the release builds; from source, see [CONTRIBUTING.md](../CONTRIBUTING.md). On Linux, USB needs a udev rule for vendor `04b0`; FireWire/SCSI needs the `sg` module.

<!-- panel:scan_quality -->
### Film & Quality

*   **Film**: Color negative, B&W negative, Slide or Kodachrome. Sets frame detection, metering and whether IR and ICE are offered (not for B&W or Kodachrome).
*   **Film format**: frame length (135, 66, 645 and so on). **Auto** where the holder narrows it; set it for loose film in a masked carrier.
*   **Resolution**, **Bit depth**: the scan's dpi and bits per channel; type a resolution between the listed stops.
*   **Scan mode** (Plustek; Single-Pass by default): **Single-Pass**, **Multi-Pass** (stacks repeated exposures to cut noise; **Passes** 2 to 9), **Adaptive Multi-Exposure** (fuses a short and a long exposure for more range) or **Adaptive Multi-Pass** (both). Multi-Pass excludes IR.
*   **Samples** (nkscan): reads per line averaged (1 to 16). Less shadow noise, proportionally slower.
*   **IR**: a separate infrared plane for Retouch's dust removal. **ICE** (nkscan): infrared dust and scratch removal baked into the file, color film only. **ICE** and **IR** exclude each other.
*   **Superfine** (nkscan): one line per pass. Slower, with no host-side line registration.
*   **Autofocus**, **Auto-exposure**: run on the scanner before the scan.
*   **Exposure** (µs): shown when the scanner has `scan-exposure-time`; off while Auto-exposure is on.

<!-- panel:scan_framing -->
### Framing

*   **Frames**: `1-6`, `1,2,5`, or empty for all. The strip preview writes its picks here.
*   **Batch** / **Window**: on a feeder, **Preview strip…** previews every frame, to set windows and pick frames; with a manual holder, **Preview…** sets one crop window. **Clear** resets it. **Detect frames** reads the strip again after the film moves.
*   **Exposure lock** (**Meter Frame…** / **Unlock**, nkscan): nkscan meters each frame alone, so an end frame can scan in a different color. **Meter Frame…** meters one frame inside the strip (such as frame 2), and every later scan reuses that exposure, across strips and restarts, until **Unlock**. Meter again for each roll.
*   **Crop** (**Prescan…**, Plustek): a 1200 dpi full-window preview; drag a crop, and the next scan reads only that area. **Clear** scans the full window.

<!-- panel:scan_camera -->
### Camera

Copy-stand capture with a camera in **PC Remote** mode over USB (macOS/Linux): with a NegPy **Scanlight**, R/G/B triplets or one exposure with the three LEDs lit together, else one white-light exposure. Needs `python-gphoto2` (`pip install gphoto2`; no Windows build). Setup and troubleshooting: CAMERA_SCANNING.md.

*   **Camera** / **Light**: connection status, found automatically; the light turns amber once it runs warm. On Linux, the Scanlight's serial port needs your user in the `dialout` group (`sudo usermod -aG dialout $USER`, then log out and back in).
*   **Live View**: click the image to aim the focus magnifier. Turn the focus ring past best focus, then back until the **Focus meter** reads **at peak**. ISO, shutter and aperture are set from its toolbar or from the card; both follow the camera. With a Scanlight, Scan shoots the whole triplet into the next frame and never touches an existing file. **R**, **G** and **B** pick which exposures Retake shoots again over the current frame's, replacing those files; **IR**, on a light with infrared LEDs, is the Infrared setting for both. A frame whose three visible exposures exist stays one triplet. An `_IR` file stays its own frame in the Film Strip.
*   **Histogram** and **Zebras**: the frame's RGB histogram, and hatching on pixels at the top (red) and bottom (blue) of the preview range. The preview clips before the RAW does, so a zebra is an early warning.
*   **Meter**: one RAW probe sets the shutter so the region that must not clip (a negative's clear base, a slide's brightest highlights) lands just under clipping. The white-light preset's film type decides which. An RGB preset meters its base under the scan light, and the metered shutter replaces the preset's until you pick the preset again. A negative with no clear base in frame, or a base the probe cannot read unclipped, meters its thinnest picture instead and says so. A white-light frame imports with the camera's white balance, so its target allows for that gain. A clipped picture steps down two stops; meter again.
*   **Scan** and **Retake**: **Scan** shoots the next frame, auto-numbered, and imports it; **Retake** (the redo arrow beside **Live View**) shoots the last frame again. In the Live View window, `Space` or `S` scans and `R` retakes.
*   **Capture Delay** (off, or 0.1 to 10 s on a log scale, default off): **Scan** and **Retake** wait this long before the first exposure, so a table that shakes when you let go can settle. The box takes two decimals. The panel counts down; **Stop** ends the wait. The same delay is a stepper beside **Scan** in the Live View window, in rungs of 0.1, 0.25, 0.5, 1, 2.5, 5 and 10 s.
*   **Keep Light On** (the bulb beside **Retake**, off by default): the Scanlight goes dark after each scan; this lights it again with the framing light, so you can frame the next shot on the camera's screen. Live View lights it again without this toggle.
*   **Narrowband**: RGB-lit scans render more saturated than white light; a **Print stock** other than *Digital* prints them through real dyes.

<!-- panel:scan_light -->
### Preset

Shown while a Scanlight is connected. The LED levels, the camera exposure and the infrared row sit on a rail under the preset dropdown: they are the preset's values. Channel Delay, below the rail, is a setting of the rig.

*   **Preset**: forces its RGB levels, ISO, shutter and aperture each frame. The list holds your own presets and the built-ins you have added; empty, it reads "Click + to add a preset". **+** offers three ways to add one. **Built-in Presets**, which need no calibration: **White Light** (B&W, Color Negative or Slide, autodetected or named), **White Light + IR, Color Negative**, **White Light + IR, Slide**, **Trichrome, Color Negative** and **Trichrome + IR, Color Negative**; picking one adds it to the list and selects it, and the trash removes it from the list again. Every built-in shoots at the camera's exposure: ISO, Shutter and Aperture are live steppers and the meter sets the shutter; the Trichrome ones light the LEDs at full power. **Calibrate on the Film Base…**: place the rectangle on clear film base, name it, run it; it solves a shutter and LED levels just under clipping. **Set by Hand**: unlocks the sliders and steppers; Scan uses them as they stand, and the save button keeps them as a preset. The White Light presets show only on a Scanlight with a white LED (v4 and Big Scanlight); on a v1 to v3, a Single Capture preset lights R, G and B together instead.
*   **Red**, **Green**, **Blue**, **White** (0 to 255): LED levels, editable while you build a manual preset. **Light Off** turns every channel off.
*   **Capture mode**: **Triplet** shoots one exposure per LED and merges them; **Single Capture** shoots one exposure with all three lit and imports it as an ordinary RAW. A selected Triplet preset lights a dimmed framing mix, raised per channel on an RGB-only Scanlight (v1 to v3) so it stays visible; the scan uses the preset's own levels. Hidden under a white-light preset, which shoots one exposure.
*   **Create Sensor Profile** (Single Capture only, default on): also saves a sensor profile under the preset's name; a roll scanned with the preset takes it and turns Linear RAW on. Other rolls do not get it.
*   **ISO**, **Shutter**, **Aperture**: the preset's exposure, live under any preset; a step overrides the recipe until you pick the preset again.
*   **Aperture Priority Meter** (the gauge beside CAMERA EXPOSURE): the Live View **Meter**, from the card. Opens Live View when it is closed.
*   **IR Shutter** (with infrared LEDs): the infrared exposure's own shutter, stepped through the camera's choices while Live View runs. Set it by hand; calibration does not solve it. A preset saves it.
*   **Infrared** (the LED beside IR Shutter): ends every Scan with an infrared exposure at the IR Shutter, saved as `_IR` beside the frame; the camera returns to its own shutter afterwards. A preset recalls it. Color film passes infrared; silver grain does not, so there is no B&W + IR. Needs a light with infrared LEDs and a camera that passes 850 nm, a full-spectrum or IR-converted body: a stock camera's IR-cut filter leaves the infrared frame at noise. Set the lens to manual focus: autofocus hunts on the dark infrared frame and times out.
*   **Channel Delay** (0 to 5000 ms): pauses between R, G and B for bodies that lock up. Triplet presets only.

<!-- panel:scan_output -->
### Output

Shared by both scanners.

*   **Folder**: where frames are written.
*   **Scan as Roll** (on by default): the output folder opens as a roll in the Library, so Half Frame, the Roll tab and Roll Analysis apply. Frames load as they are written.
*   **Folder as Roll** (on by default): frames go into the output folder itself, which is the roll. Off writes into a **Roll** subfolder, and a new Roll name starts a new roll. A camera frame's file name starts with the roll name.
*   **New Roll** (**+** beside Roll): steps the Roll name to the next one that has no subfolder yet. A trailing number that is zero-padded or follows `_`, `-`, a space or `.` counts up (`Roll001` to `Roll002`, `portra400_1` to `portra400_2`); any other name gets `_2`.
*   **Format**, **Filename** (Film Scanner): `TIFF` or `TIFF (mono)` (one 16-bit gray plane, for B&W negatives), and the file name as a Jinja2 template of `{{ date }}` and `{{ seq }}`.

<!-- panel:scan_strip -->
### Strip preview

Dialogs end with **Cancel**, **Apply** (keep the framing) and **Scan**. During a preview **Cancel** reads **Stop Preview** and keeps the tiles read so far. Negatives preview inverted. On nkscan, **Offset** (±10 mm) and **Drift** cut the tiles again with no new scan.

*   **Cropping**: drag on a frame. **Clear Crops** removes all.
*   **Frame outline**: red box on the detected frame; offsets are measured from it.
*   **Offset**: moves every frame along the film to clear the gap. The shaded band is film the transport cannot deliver; a feeder goes one way only.
*   **Drift**: offset that grows (or shrinks) per frame position.
*   **Per-frame offset**: the slider under a tile, on top of Offset and Drift.
*   **Size**: tile size.
*   **Which frames**: tick tiles, or **All** / **None**. Eject or a restart clears ticks, crops and per-frame offsets.
*   **Preview frame**: scans that frame again.

---

## 14. Preferences

Application-wide settings: **⋯** menu → **Preferences…** or `Ctrl + ,`. Changes apply at once; startup rows show a restart notice.

### Interface

*   **Language** (default System Default): English, Simplified Chinese, Japanese or Korean; restart to apply. Other system languages use English. Panel guides use the selected language and fall back to English when a translation is missing.
*   **UI scale** (80% to 120%): after a restart.
*   **Canvas background**: black, dark gray, mid gray (neutral for judging, the default), light gray or white (a print on a light table). The Film Strip and the Light Table lie on it too.
*   **Film edges** (on by default): draws the perforations and edge print on the film of the Film Strip and the Light Table. Off leaves the film blank, in the rebate tone.
*   **Sticky zoom**: keeps the zoom when you switch frames.
*   **Reverse scroll zoom**: scroll up zooms out.
*   **Customize Shortcuts…**, **Edit Toolbar…**, **Reset Panel Layout**: shortcut editor, toolbar picker, default panel layout.

### Accessibility

*   **Color vision** (default **Standard**): colors for marks told apart by color alone (dust overlay, dodge and burn masks, Zone Overlay, clipping overlay). *Protanopia / deuteranopia*, *Tritanopia* and *Achromatopsia* use colors from the Okabe–Ito palette.

### Performance

*   **GPU acceleration**: renders on the GPU. Off uses the slower CPU pipeline, same image. If the GPU fails at launch, an amber line here says so.
*   **Multi-core CPU rendering**: runs CPU rendering on all cores; it helps exports and machines without a usable GPU. On by default except on macOS, where it can end the app; after such a crash NegPy offers to turn it off. `cpu_parallel` in `override.toml` overrides it.
*   **Search by meaning**: find frames by description (§2).
*   **Preview size** (512 to 8192 px): canvas long edge; higher is sharper and uses more memory.
*   **Preview cache** and **Preview cache limit**: photos kept decoded, and their memory limit. Lower both on low RAM.
*   **HQ buffers**: full-resolution preview buffers kept in memory.
*   **Rendered frames**: frames kept for going back without a new render.
*   **GPU texture cap**: largest texture dimension; 0 lets the hardware decide. Lower it if exports run out of GPU memory.
*   **Show GPU memory warning**: a message when an HQ preview is downsampled to fit the texture cap.

Rows from **Preview size** down need a restart. A value in `override.toml` wins and grays out its row.

### Session & Storage

*   **Carry settings between frames**: applies your Persistent Settings to each newly opened file.
*   **Persistent Settings…**: which edits carry over (§1).
*   **Manage Database…**: row counts and sizes, clear saved edits, library roots.

### Startup override (`override.toml`)

For crashes on launch or rendering glitches: edit `Documents/NegPy/override.toml` (created on first run) and restart. Its values win over Preferences.

| Setting | Values | Effect |
|---------|--------|--------|
| `rendering.backend` | `"auto"`, `"vulkan"`, `"dx12"`, `"metal"`, `"cpu"` | GPU backend for image processing. `"cpu"` disables the GPU. |
| `display.qt_rhi_backend` | `"auto"`, `"vulkan"`, `"d3d12"`, `"metal"`, `"opengl"`, `"software"` | Qt UI rendering backend. |
| `display.qt_platform` | `"auto"`, `"xcb"`, `"wayland"` | Window system plugin (Linux only). |
| `performance.force_hq_preview` | `true` / `false` (or absent) | Overrides the saved HQ preview toggle. |
| `performance.cpu_parallel` | `true` / `false` (or absent) | Multi-core CPU rendering. On by default, except on macOS. |
| `logging.level` | `"debug"`, `"info"`, `"warning"`, `"error"` | Log verbosity. Use `"debug"` when you report issues. |

`max_texture_size`, `preview_render_size`, `preview_cache_max_bytes`, `preview_cache_max_entries`, `preview_cache_max_full_res_entries` and `render_memo_max_entries` take the same values as their Preferences rows.

**Common fixes:**

*   **Crashes immediately on Linux** → `backend = "cpu"` or `qt_rhi_backend = "opengl"`.
*   **Black or blank preview on Windows** → `backend = "dx12"` or `qt_rhi_backend = "software"`.
*   **Wayland rendering issues** → `qt_platform = "xcb"` to force X11.
*   **GPU out-of-memory during export** → `max_texture_size = 4096`.

---

## 15. Updating NegPy

NegPy checks GitHub once at startup. A new release adds **Update to vX.Y.Z…** to the **⋯** menu, marked with a green dot; it opens the release notes and the install button. **Check for Updates…** checks by hand.

**Install Update** downloads the build for this install type, closes NegPy, installs and reopens. Nothing is replaced until NegPy exits, so a failure leaves your install as it was.

| Install | What NegPy fetches | How it installs |
|---------|--------------------|-----------------|
| **Windows** | the `-Setup.exe` installer | Runs it silently. Approve the administrator prompt *before* NegPy closes. |
| **macOS** | the `.dmg` for your chip (Apple silicon or Intel) | Replaces the `NegPy.app` bundle where it is, then reopens it. |
| **Linux** | the `.AppImage` | Replaces the AppImage file you launched and relaunches it. |

Edits, presets, settings and library live in `Documents/NegPy` and the database, so updates do not touch them.

The button reads **"Open Releases Page"** when NegPy cannot update itself: a source checkout, no build for your platform, an app moved out of its installer layout, or an app folder you cannot write to.

---

## Additional Info

*   **Database**: edits live in a local SQLite database keyed by file hash, so files can move or be renamed. Optional `.negpy` sidecars mirror them.
*   **Saving edits**: written on export, on frame switch, or on save; closing mid-edit before any of these loses unsaved changes.
*   **Keyboard shortcuts**: [KEYBOARD.md](KEYBOARD.md)
*   **Filename templating**: [TEMPLATING.md](TEMPLATING.md)
*   **The pipeline in depth**: [PIPELINE.md](PIPELINE.md)
