# Alexa Skill — Compliance & Implementation Requirements

*[Station Name] · Live-Stream Passthrough Skill · Prepared for Development · June 28, 2026*

---

## 1. Scope & Governing Principle

This skill is a **pure passthrough**. On invocation it directs an Amazon Echo to play the station's existing public Live365 stream URL through the Alexa AudioPlayer interface. The device connects **directly** to the Live365 stream server; the skill performs no hosting, caching, transcoding, re-streaming, or modification of the audio, embedded advertisements, or metadata.

That passthrough model is the entire basis of compliance: it keeps all listening inside the station's existing Live365 licensing coverage, because the Echo is simply another stream client — equivalent to a web browser or VLC. **Every requirement below exists to preserve that status.** Any design that causes the device to connect to a non-Live365 server, or that alters the stream in transit, moves the activity outside the station's coverage and must not be built.

---

## 2. Hard Compliance Requirements

**Non-negotiable.** A violation of any single item below can cost the station its licensing coverage, trigger advertising-revenue clawback, or result in stream suspension or termination. The "Basis" column cites the governing Live365 Broadcaster T&C provision.

| ID | Requirement | Basis (Live365 T&C) |
| --- | --- | --- |
| **C-1** | **Stream direct to source.** The Echo must connect to the canonical Live365 mount/URL directly. Do not proxy, relay, or re-host the stream through any intermediate server. | Royalty coverage requires the end user to be a "Connected Listener" connected to a Live365 server. A proxy breaks coverage and is prohibited re-hosting. |
| **C-2** | **No audio modification.** Pass the audio bytes through untouched — no transcoding, re-encoding, filtering, normalizing, or splicing. | Branded Player / stream-integrity terms; altering or interfering with stream content is prohibited. |
| **C-3** | **Preserve advertising.** Do not strip, skip, mute, shorten, obscure, or reorder ads or ad markers, and do not modify or disable any ad tags, pixels, or tracking code carried in the stream. | Schedule A, Prohibited Activities (iv)–(vi): altering, obscuring, or interfering with Advertisements or their tags/pixels. |
| **C-4** | **User-initiated playback only.** Playback may begin only on an explicit user request (voice launch or resume). Implement no autoplay or auto-resume that starts the stream without user action. | Schedule A requires ad-bearing content to be user-requested and initiated — no autoplay. |
| **C-5** | **Single-station scope.** Stream only this one station's mount. Do not aggregate other stations, repoint to other mounts, or serve the stream under any other property. | Schedule A, Prohibited Activities (viii): inventory served only on the specific station it came from. |
| **C-6** | **Required credit & metadata.** The now-playing presentation must display a Live365-approved technical credit; **"Powered by Live365"** is approved. Where the platform allows, also show artist and song title. See B-2 for the platform constraint and minimum implementation. | Branded Player created by Broadcaster must display artist, song title, and an approved technical credit. |

---

## 3. Alexa Platform / Technical Requirements

| ID | Requirement | Notes |
| --- | --- | --- |
| **T-1** | **AudioPlayer implementation.** Implement the AudioPlayer interface. On play, issue a Play directive with playBehavior `REPLACE_ALL` targeting the stream URL; treat the source as a continuous live stream with no fixed end. Handle `PlaybackStarted`, `PlaybackStopped`, `PlaybackFailed`, `PlaybackFinished`, `PlaybackNearlyFinished`. | — |
| **T-2** | **Required intents.** Handle `LaunchRequest` plus `AMAZON.PauseIntent`, `AMAZON.ResumeIntent`, `AMAZON.StopIntent`, `AMAZON.CancelIntent`, and `AMAZON.HelpIntent`. Map play/resume to (re)issuing the stream; map pause/stop/cancel to stopping playback. | — |
| **T-3** | **HTTPS with valid certificate.** AudioPlayer requires the stream URL to be HTTPS with a valid, trusted SSL certificate. Confirm Live365 serves the station over a compliant HTTPS mount — plain-HTTP Icecast URLs will not play. **This cannot be solved with a self-hosted HTTPS proxy** (that would violate C-1). If no compliant endpoint is available from the source, escalate before building. | Most likely blocker — see §6. |
| **T-4** | **Supported stream format.** Confirm the codec/container is AudioPlayer-supported (MP3, AAC/MP4, HLS, or a PLS/M3U pointer to one). If the primary mount is unsupported, locate a compatible Live365-provided mount. Do not transcode to work around this (C-2). | — |
| **T-5** | **Stream-URL stability & resilience.** Use the stable, public mount — not a session-scoped or tokenized URL. Follow HTTP redirects (the source may 302 to a delivery node). Implement reconnect/backoff on `PlaybackFailed` and on stream drop so playback recovers without user intervention. | — |

---

## 4. Branding & Metadata Requirements

| ID | Requirement | Notes |
| --- | --- | --- |
| **B-1** | **Authorized station branding.** Skill name, invocation name, icon, and description must use the station's branding and be approved by the station owner. The invocation name should be the spoken station name (e.g., "play [Station]"). | Owner approval required. |
| **B-2** | **Metadata target & constraint.** Populate `audioItem.metadata` (title, subtitle, art, background image) on each Play directive. **Constraint:** AudioPlayer metadata is set per-directive and does not auto-update per track on a continuous live stream; headless Echo devices have no display. **Minimum acceptable:** set now-playing title to the station name and include "Powered by Live365" (subtitle or displayed credit), satisfying C-6's load-bearing credit requirement. Per-track artist/title is best-effort and platform-limited. Do not ship a URL-only handoff that sends no metadata at all. | Satisfies C-6. |
| **B-3** | **Credit placement.** Include the "Powered by Live365" credit in the skill's store description in addition to the now-playing metadata. | Satisfies C-6. |

---

## 5. Certification & Submission Requirements

| ID | Requirement | Notes |
| --- | --- | --- |
| **S-1** | **Skill certification.** The skill must pass Amazon certification (functional + policy review). Music/streaming skills receive additional content-rights scrutiny; keep the station-owner authorization on record to support the rights attestation at submission. | — |
| **S-2** | **Submission artifacts.** Provide the privacy-policy URL, terms-of-use URL (if required), skill icons (108×108 and 512×512), description, example phrases, and category. The invocation name must meet Amazon's naming policy. | — |
| **S-3** | **Duplicative-skill risk.** A first-party Live365 Alexa skill — and per-station skills on certain Live365 packages — already exist. Amazon may flag a new station-specific skill as duplicative. Confirm the approach before investing in submission. | Risk — see §6. |

---

## 6. Dependencies & Risks to Resolve Before Build

Clear these before writing code — the first three gate whether the skill can function at all.

- **HTTPS endpoint (T-3):** Confirm a Live365-served HTTPS stream URL with a valid certificate exists for the station. This is the single most probable blocker, and it **cannot** be engineered around with a self-hosted proxy without breaking compliance (C-1).
- **Stream format (T-4):** Confirm an Alexa-supported codec on that HTTPS mount.
- **Stream-URL type (T-5):** Confirm the mount is stable and public, not tokenized or session-scoped.
- **Duplicative skill (S-3):** Confirm Amazon will accept a station-specific skill given existing first-party coverage.
- **Owner authorization:** Required for branding (B-1) and to support certification's rights review (S-1).
