# Phase 11 Changes

Date: 2026-05-08

## Summary

Phase 11 converted OncoBoard-Edge from an implementation-first prototype into a polished, judge-ready demo package. The focus was deliberately narrow: UI/UX refinement, demo realism, storytelling, documentation quality, deployment readiness, and submission packaging. No random feature expansion was added.

## What Changed

### UI / UX
- Added a medical design system with CSS variables and reusable component styles.
- Styled confidence badges, evidence cards, red flags, alert cards, and clinical notes.
- Improved the Gradio layout for clearer hierarchy and mobile responsiveness.
- Added demo case loading so judges can test realistic oncology scenarios immediately.

### Demo Content
- Added three oncology demo cases:
  - NSCLC adjuvant decision support
  - HER2+ breast cancer neoadjuvant planning
  - MSI-H colorectal cancer surveillance vs adjuvant discussion
- Added synthetic pathology report text for reference.
- Added expected-output references for demo validation.

### Documentation
- Expanded the README with a stronger project summary, benchmark section, deployment guidance, limitations, and roadmap.
- Added a deployment checklist for Hugging Face Spaces, Docker, bare metal, and Kaggle.
- Added hackathon positioning copy with a judge-facing elevator pitch and demo moments.
- Added a Kaggle write-up draft and a W&B media gallery plan.
- Updated architecture and status docs so they reflect the current runtime behavior accurately.

### Model Story
- Gemma 4 remains a supported hosted reasoning provider.
- The default demo path is the deterministic offline fallback, which keeps the project reproducible without secrets.
- The docs now state that distinction explicitly so submission materials match the code.

## Supporting Resources

- [README.md](README.md)
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- [BUGS_AND_GAPS.md](BUGS_AND_GAPS.md)
- [HACKATHON_POSITIONING.md](HACKATHON_POSITIONING.md)
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- [submission/KAGGLE_WRITEUP.md](submission/KAGGLE_WRITEUP.md)
- [submission/WANDB_MEDIA_GALLERY.md](submission/WANDB_MEDIA_GALLERY.md)

## Outcome

The repo now has a coherent submission narrative, a polished demo experience, and supporting docs that explain both the offline fallback and the optional Gemma 4 provider correctly.
