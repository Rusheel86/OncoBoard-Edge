# 🚀 Deploying OncoBoard-Edge to Hugging Face Spaces with Gemma 4

This guide walks you through deploying OncoBoard-Edge to **Hugging Face Spaces** with **Gemma 4 as the primary reasoning engine**. The deployment takes ~5 minutes and requires no Docker setup.

---

## 📋 Prerequisites

You'll need:
- ✅ **Hugging Face account** (free at [huggingface.co](https://huggingface.co))
- ✅ **Google API key** with access to Gemma 4 (get free credits at [Google AI Studio](https://aistudio.google.com/app/apikey))
- ✅ **Git** (or use HF web interface to upload files)
- ✅ **This repository** (already set up locally)

---

## 🎯 Step-by-Step Deployment

### Step 1: Create a New Space on Hugging Face

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `oncoboard-edge` (or your preferred name)
   - **License**: MIT
   - **Space SDK**: **Gradio** (critical!)
   - **Visibility**: Public or Private (your choice)
4. Click **"Create Space"**

You'll be redirected to your new Space. Note the URL: `https://huggingface.co/spaces/{your-username}/oncoboard-edge`

---

### Step 2: Upload Repository Files

You have two options:

#### Option A: Git Push (Recommended)
If you have Git set up:

```bash
# Clone the HF Space (creates a new Git remote)
git clone https://huggingface.co/spaces/{your-username}/oncoboard-edge
cd oncoboard-edge

# Copy OncoBoard-Edge files (from your local repo)
# Copy the following to the HF Space directory:
# - app.py (root)
# - ui/
# - core/
# - demo/
# - requirements.txt
# - runtime.txt

# Commit and push
git add .
git commit -m "Initial OncoBoard-Edge deployment with Gemma 4"
git push

# HF will auto-build (~2-5 minutes)
```

#### Option B: Web Upload (Easier for First-Time Users)
1. In your HF Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"** (or drag-and-drop)
3. Upload:
   - `app.py` (root)
   - Entire `ui/` folder
   - Entire `core/` folder
   - Entire `demo/` folder
   - `requirements.txt`
   - `runtime.txt`

HF will detect `requirements.txt` and `runtime.txt` automatically and start the build.

---

### Step 3: Configure Gemma 4 Secrets

Once your Space is created (Step 1), configure the secrets:

1. Go to your Space's **Settings** (gear icon, top-right)
2. Scroll to **"Repository secrets"**
3. Add:
   - **Secret name**: `GOOGLE_API_KEY`
   - **Secret value**: `sk-...` (your Google API key from [aistudio.google.com](https://aistudio.google.com/app/apikey))
   - Click **"Add secret"**

4. Add another secret (optional, but recommended):
   - **Secret name**: `ONCO_LLM_PROVIDER`
   - **Secret value**: `google`
   - Click **"Add secret"**

The Space will read these secrets from the environment at runtime.

---

### Step 4: Wait for Build & Deploy

1. Your Space will begin building (~2-5 minutes)
2. Watch the **"Build logs"** tab for progress
3. Once complete, you'll see a green checkmark and the app will be live
4. Click **"Open this space in an iframe"** or visit your Space URL

---

### Step 5: Test Live Gemma 4 Deployment

Once your Space is live:

1. **Open the app** at `https://huggingface.co/spaces/{your-username}/oncoboard-edge`
2. **Run Demo Case 1 (NSCLC)**:
   - In the sidebar, select **"NSCLC Adjuvant Therapy"**
   - Click **"Run Analysis"** or equivalent
   - Expected output: Full report with confidence badges, evidence cards, citations
3. **Verify Gemma 4 is active**:
   - Check report text: should be coherent, natural language (not boilerplate)
   - Evidence citations: specific to the NSCLC case, not generic
   - Speed: <5 seconds for full pipeline (retrieval + reasoning)
4. **Check Styling**: 
   - Report tab shows colored badges (🟢 HIGH, 🟡 MEDIUM, 🔴 LOW)
   - Evidence cards have left blue border + clean formatting
   - Mobile view works (test on DevTools 375px width)

---

### Step 6: Share Your Live Demo

Your deployed app is now live! Share the URL:
- **Direct link**: `https://huggingface.co/spaces/{your-username}/oncoboard-edge`
- **Embed code**: HF provides HTML for embedding in blogs/papers
- **Kaggle submission**: Include this link in your Kaggle write-up

---

## 🔍 Troubleshooting

### "Build failed" or "Space didn't start"
- **Check logs**: Click **"Build logs"** tab for error messages
- **Common issues**:
  - Missing `requirements.txt` or `runtime.txt` → upload them
  - Python 3.10 not specified in `runtime.txt` → update to `python-3.11`
  - Typo in package name → check `pip install -r requirements.txt` locally first

### "App starts but no output on demo"
- **Check secrets**: Verify `GOOGLE_API_KEY` is set correctly in Settings → Secrets
- **Check logs**: View Space logs (Settings → Space logs) for runtime errors
- **Test locally first**: Run `python ui/app.py` locally with same GOOGLE_API_KEY to isolate issues

### "Report is empty or generic"
- **Verify Gemma 4**: Check HF logs for google-genai SDK calls (should see API requests)
- **Check fallback**: If GOOGLE_API_KEY is missing/wrong, system falls back to offline deterministic provider
- **Expected behavior**: With Gemma 4, report should be specific to case, not template

### "Styling looks broken (no colors, badges not showing)"
- **CSS file uploaded?** Verify `ui/style.css` is in the Space
- **Check DevTools**: Open browser DevTools → Elements, search for `.badge-high` class
- **Common fix**: Ensure `ui/style.css` is in same directory structure as `ui/app.py`

### "Mobile view is broken"
- **Check responsive CSS**: `ui/style.css` should have `@media (max-width: 768px)` sections
- **Test locally**: Open `http://localhost:7860` in browser DevTools, toggle device toolbar to 375px
- **Common fix**: Ensure CSS file loaded correctly (no 404 errors in DevTools Network tab)

---

## 📊 Verifying Gemma 4 is Active

To confirm Gemma 4 is generating reports (not offline fallback):

1. **Check report content**:
   - Gemma 4: Natural, conversational language with specific citations
   - Offline: More templated, generic structure

2. **Check speed**:
   - Gemma 4: ~2-5 seconds (includes API call + retrieval)
   - Offline: <1 second (all local)

3. **Check evidence cards**:
   - Gemma 4: Should cite specific guidelines + page numbers
   - Offline: May have placeholder or generic citations

4. **Check HF Spaces logs**:
   - Settings → Space logs → search for "google-genai" or "Gemma"
   - Should see API calls if Gemma 4 is active

---

## 🎬 Demo Script for Judges

Once deployed, you can use this script to showcase Gemma 4:

```
"OncoBoard-Edge harnesses Gemma 4 to deliver grounded oncology reasoning 
at the edge—even in low-resource clinics without reliable internet.

Watch as we upload a pathology report PDF, run automated extraction, 
retrieve evidence from local guidelines, and have Gemma 4 generate 
a cited, evidence-backed recommendation—all offline.

[Click Run Analysis on NSCLC case]

In under 5 seconds, Gemma 4 has:
1. Extracted biomarkers (KRAS, PD-L1, TNM stage)
2. Retrieved relevant NCCN and clinical trial guidelines
3. Generated specific recommendations for adjuvant therapy
4. Cited the exact guideline sections supporting each claim
5. Labeled confidence levels so clinicians know what to trust

The green badge means high-confidence, well-sourced. The yellow badges 
mark areas where clinicians should use their judgment. Every single 
recommendation is traceable—click any evidence card to see the full 
guideline quote it's citing.

This is what frontier AI for global health equity looks like: 
powerful, transparent, offline-capable, and deployed to clinics 
that need it most."
```

---

## 🚀 Advanced: Custom Domain (Optional)

If you want a custom domain (e.g., `oncoboard.your-domain.com`):

1. Go to Space Settings → Custom URL
2. Point your domain's CNAME to HF's domain (instructions provided)
3. Update any submission links to the custom domain

---

## 📝 Deployment Checklist

- [ ] HF Space created (Gradio SDK)
- [ ] All files uploaded (app.py, ui/, core/, demo/, requirements.txt, runtime.txt)
- [ ] Build completed successfully (no errors in Build logs)
- [ ] `GOOGLE_API_KEY` secret added and correct
- [ ] `ONCO_LLM_PROVIDER=google` secret added (recommended)
- [ ] Demo Case 1 (NSCLC) runs and shows Gemma 4 report
- [ ] Styling renders correctly (badges visible, colors applied)
- [ ] Mobile view works (DevTools 375px width)
- [ ] Evidence cards show citations with quotes
- [ ] Speed is <5 seconds per analysis
- [ ] Live URL shared in Kaggle write-up and hackathon submission

---

## 📞 Support

- **HF Spaces docs**: [huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)
- **Gradio docs**: [gradio.app/guides](https://gradio.app/guides)
- **Google AI Studio**: [aistudio.google.com](https://aistudio.google.com)
- **Project README**: [README.md](README.md)
- **Deployment checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

**Happy deploying! 🎉**
