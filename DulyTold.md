# DulyTold.md

## Project Overview

**DulyTold** is the interactive "side" of the DulyNoted ecosystem. It transforms traditional note-taking into a dynamic experience by recording and replaying the creative process. While maintaining the core security and minimalist principles of the project, DulyTold focuses on the "how" of writing, capturing the rhythm and flow of diary entries through keystroke logs.

### Main Technologies
- **Backend:** [Flask](https://flask.palletsprojects.com/) (Python 3.x)
- **Database:** [MongoDB](https://www.mongodb.com/) (Unified storage with DulyNoted)
- **Frontend:** [Jinja2](https://jinja.palletsprojects.com/) templates with an interactive JavaScript recording engine.
- **Authentication:** Shared session-based authentication with DulyNoted.

### Architecture
- `server/routes/dulytold.py`: Modular blueprint for the DulyTold side.
    - Handles the `/dulytold` landing page.
    - Manages the `/diary` interface redirection.
    - Provides API endpoints for specialized diary settings.
- `templates/dulytold.html`: The landing page for the DulyTold side.
- `templates/notes.html`: A context-aware unified editor used by both sides.
- **Data Model:** Diary entries are stored in the same MongoDB collections as notes but can include an optional `events` array containing timestamped HTML snapshots for playback.

---

## Core Features

### Keystroke Recording
DulyTold includes a specialized recording engine built into the editor. When activated via the **Start Recording** button, the application captures every change to the editor's state, pairing each "event" with a relative timestamp. This creates a high-fidelity log of the writing session.

### Interactive Playback
The **View Logs** button allows users to re-experience their writing. Clicking it triggers an automated replay where the editor's content is reconstructed event-by-event, effectively "typing out" the entry exactly as it was originally created.

### Side-Switching Logic
The application implements a "two-sided" UI. Users can toggle between the secure, static environment of **DulyNoted** and the interactive world of **DulyTold** by simply clicking the page title on either homepage. This transition updates the entire application context, including navigation links and UI terminology.

---

## Development Conventions

### Terminology & Context
- **Linguistic Shift:** The UI is designed to be context-sensitive. When the `side` variable is set to `dulytold`, all instances of "note" are automatically replaced with "diary" via Jinja2 logic and frontend filters.
- **Unified Sidebar:** Both static entries and interactive recordings are presented in a single, uniform list to maintain a clean aesthetic.

### Styling & UI
- **Visual Feedback:** Recording sessions are indicated by a pulsing animation on the recording button, styled in `beaut/ooo.css`.
- **Minimalism:** DulyTold adheres strictly to the Monkeytype-inspired palette and layout of the parent project.

---

## Roadmap & Notes
- **Advanced Playback:** Future updates may include playback speed controls (1x, 2x, etc.).
- **Exporting Logs:** Development is underway to support exporting interactive recordings as standalone JSON files for external playback.
