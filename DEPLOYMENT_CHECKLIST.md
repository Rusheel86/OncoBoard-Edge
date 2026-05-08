# Deployment Checklist & Pre-Release Validation

**Phase 11 Deployment Readiness**  
**Last Updated**: May 2026  
**Status**: Ready for HF Spaces + Local deployment  

---

## 🎯 Pre-Release Validation Checklist

### Code Quality
- [x] All tests passing (`pytest tests/`)
- [x] No unused imports or dead code
- [x] Type hints complete on public functions
- [x] Docstrings present on all modules/classes
- [x] No hardcoded secrets or API keys in code
- [x] Error messages are user-friendly (no stack traces exposed)
- [x] Consistent code style (snake_case for functions, PascalCase for classes)

### Dependencies & Requirements
- [x] All dependencies pinned in requirements.txt
  - `transformers>=4.44.0,<=4.48.3` (Unsloth compatibility)
  - `bitsandbytes>=0.43.3,<0.44.0`
  - `langgraph>=0.2.30,<0.3.0`
- [x] No unused packages (minimized bloat)
- [x] requirements.txt tested on clean environment
- [x] Optional dependencies clearly documented
- [x] `.env.example` created with all required variables

### Security & Safety
- [ ] No API keys in git history (use `.gitignore`)
- [ ] File uploads validated (type + size checks)
- [ ] Input sanitization on user text fields
- [ ] Error messages don't leak internal paths
- [ ] No PHI logging by default (audit logging optional)
- [ ] Timeouts set for long-running operations
- [ ] Malware scanning recommended for production (out of scope for Phase 1)

### UI & UX
- [x] CSS loads without errors
- [x] Confidence badges render with correct colors
- [x] Evidence cards display properly (not JSON code blocks)
- [x] Loading states visible during analysis
- [x] Responsive design tested (mobile, tablet, desktop)
- [x] Accessibility: keyboard navigation works, ARIA labels present
- [x] Demo cases load and run successfully
- [x] Error messages helpful and user-facing

### Testing
- [x] Unit tests pass: `pytest tests/ -v`
- [x] Integration test (full pipeline): passes
- [x] Benchmark tests: run without errors
- [x] Test coverage >80% on core modules
- [x] Demo cases produce expected outputs
- [x] Offline mode verified (no API key needed)

### Documentation
- [x] README.md comprehensive and up-to-date
- [x] DEPLOYMENT.md step-by-step instructions
- [x] DESIGN_TOKENS.md documented for UI
- [x] Demo cases well-documented
- [x] ARCHITECTURE.md accurate
- [x] LICENSE included (MIT)
- [x] CONTRIBUTING guidelines (optional for Phase 1)

### Performance & Stability
- [ ] Cold start time <10 seconds
- [ ] Analysis runtime <60 seconds for demo cases
- [ ] Memory usage <4GB on demo hardware
- [ ] No memory leaks after 10 consecutive runs
- [ ] Graceful degradation when services unavailable (e.g., ChromaDB)

---

## 🚀 Deployment Paths

### **Path 1: Hugging Face Spaces (Recommended for Demo)**

**Fastest & Easiest — 2 minutes to live**

#### Prerequisites
- Hugging Face account
- This repo cloned/ready to upload

#### Steps
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces/create)
2. Click **"Create new Space"**
3. Choose:
   - Owner: your username
   - Space name: `oncoboard-edge`
   - License: MIT
   - Space SDK: **Gradio**
4. Upload files:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/oncoboard-edge
   cd oncoboard-edge
   cp -r /path/to/OncoBoard-Edge/* .
   git add .
   git commit -m "Initial commit: OncoBoard-Edge Phase 11"
   git push
   ```
5. Set secrets (if using hosted Gemma):
   - Go to Space Settings → Secrets
   - Add: `GOOGLE_API_KEY=your_key`
   - Add: `ONCO_LLM_PROVIDER=google` (optional, defaults to offline)
6. Wait ~2 minutes for build
7. Space goes live at: `https://huggingface.co/spaces/YOUR_USERNAME/oncoboard-edge`

#### Verification
- [ ] Space builds without errors
- [ ] Gradio UI loads at public URL
- [ ] Demo case runs successfully
- [ ] Report renders with confidence badges
- [ ] Evidence cards display (not JSON)

---

### **Path 2: Local Docker (Optional for Reproducibility)**

**Recommended for local development with containerization**

#### Prerequisites
- Docker installed
- This repo cloned

#### Steps
```bash
# Build image
docker build -t oncoboard:latest .

# Run container
docker run --rm \
  -p 7860:7860 \
  -v $(pwd)/.oncoedge:/app/.oncoedge \
  oncoboard:latest

# Access at http://localhost:7860
```

#### Environment Variables (Optional)
```bash
docker run --rm \
  -p 7860:7860 \
  -e GOOGLE_API_KEY=your_key \
  -e ONCO_LLM_PROVIDER=google \
  -v $(pwd)/.oncoedge:/app/.oncoedge \
  oncoboard:latest
```

#### Verification
- [ ] Image builds successfully
- [ ] Container starts without errors
- [ ] Gradio UI accessible at localhost:7860
- [ ] Demo case runs and produces output
- [ ] Volume persistence works (files survive container restart)

---

### **Path 3: Bare Metal (Local Development)**

**Simplest for development; no containerization**

#### Prerequisites
- Python 3.11+
- pip

#### Steps
```bash
# Install dependencies
pip install -r requirements.txt

# Run Gradio app
python app.py

# Access at http://localhost:7860
```

#### Verification
- [ ] All dependencies install without errors
- [ ] No import errors on startup
- [ ] Gradio app launches successfully
- [ ] Demo cases run without errors
- [ ] UI renders with CSS styling

---

### **Path 4: Kaggle (Optional)**

**For interactive notebooks + GPU access**

#### Steps
1. Upload repo to Kaggle
2. Run: `python scripts/kaggle_setup.py`
3. Then: `python ui/app.py`
4. Access via Kaggle notebook cell output

---

## 🔍 Post-Deployment Validation

### Live Demo Testing (HF Spaces)

**Test Checklist**
- [ ] Page loads in <5 seconds
- [ ] All input fields render
- [ ] File upload dropzones functional
- [ ] "Run Analysis" button is clickable
- [ ] Demo case 1 (NSCLC) produces output in <10 seconds
- [ ] Report tab shows formatted Markdown (not JSON)
- [ ] Confidence badge visible and colored correctly (🟢/🟡/🔴)
- [ ] Evidence tab shows JSON structure
- [ ] Mobile view is readable (test on phone/tablet)

### Error Handling Testing
- [ ] Invalid input (negative age) → helpful error message
- [ ] Missing required field → field validation warning
- [ ] Very large file (>25MB) → rejection with size explanation
- [ ] No PDF uploaded but PDF expected → graceful handling
- [ ] Network timeout (if Gemma) → fallback to offline mode

### Performance Testing
- [ ] Load time <5s
- [ ] Analysis time <60s for full pipeline
- [ ] Memory doesn't spike excessively
- [ ] No console errors (check browser DevTools)

---

## 🛠️ Troubleshooting Common Issues

### "CSS not loading" / "Styling looks wrong"
- **Check**: `ui/style.css` exists in repo
- **Fix**: Ensure CSS is in same directory as `ui/app.py`
- **Verify**: `python -c "print(open('ui/style.css').read()[:100])"`

### "Demo cases not loading"
- **Check**: `demo/cases.json` exists and is valid JSON
- **Fix**: Validate JSON: `python -m json.tool demo/cases.json`
- **Fallback**: App has built-in demo cases if JSON missing

### "Confidence badges not rendering"
- **Issue**: CSS class not applied
- **Fix**: Check browser DevTools → Inspect element → see classes
- **Verify**: Markdown output includes `<span class="badge badge-high">` HTML

### "App launches but no UI appears"
- **Check**: Python error on startup
- **Fix**: Run `python app.py` in terminal and read output
- **Common**: Missing `ui/style.css` or import error

### "Analysis takes >60 seconds"
- **Issue**: Reasoning step slow (expected first run with Gemma loading)
- **Expected**: First run ~30-60s, subsequent <10s (caching)
- **If persistent**: Check CPU/memory usage, consider smaller model

---

## 📋 Pre-Production Hardening (Phase 2)

These are **not required for Phase 1 demo** but recommended for clinical deployment:

### Authentication & Authorization
- [ ] API key validation on `/analyze` endpoint
- [ ] Role-based access control (admin, clinician, viewer)
- [ ] Session management + token expiry
- [ ] Audit logging of who accessed what and when

### Data Security
- [ ] Encryption at rest for `.oncoedge/` folder
- [ ] Encryption in transit (HTTPS only)
- [ ] Input sanitization (no SQL injection, XSS)
- [ ] Rate limiting to prevent abuse
- [ ] Virus/malware scanning on file uploads

### Compliance & Privacy
- [ ] PHI detection and redaction
- [ ] HIPAA audit logging (if handling real patient data)
- [ ] Data retention policies
- [ ] GDPR compliance review
- [ ] Terms of service + disclaimer

### Monitoring & Logging
- [ ] Structured logging (JSON format)
- [ ] Log aggregation (syslog/CloudWatch/Datadog)
- [ ] Error tracking (Sentry/similar)
- [ ] Performance monitoring (APM)
- [ ] Health checks + alerting

---

## ✅ Release Checklist (Final)

Before announcing public release:

- [ ] All code reviewed
- [ ] Tests passing (100%)
- [ ] README and docs complete
- [ ] Demo cases verified
- [ ] UI tested on 3+ browsers
- [ ] Mobile responsiveness confirmed
- [ ] Offline mode works without errors
- [ ] Performance benchmarks acceptable
- [ ] Security review completed
- [ ] License file included (MIT)
- [ ] GitHub/documentation links working
- [ ] HF Spaces deployment successful
- [ ] Public demo link shared
- [ ] Citation/paper linked in README

---

## 📞 Rollback Plan

If critical issue discovered after release:

1. **HF Spaces**: Delete/disable Space, push fix, re-enable
2. **Docker**: Pull latest image from registry, restart container
3. **GitHub**: Revert commit, tag with `v1.0-hotfix`
4. **Communication**: Post issue note in README + GitHub Discussions

---

## 📊 Deployment Timeline

| Stage | Target | Status |
|-------|--------|--------|
| **Local Dev** | ✓ Complete | Ready |
| **Docker Build** | ✓ Complete | Ready |
| **HF Spaces Test** | ⏳ This week | Next step |
| **Public Demo URL** | ⏳ This week | After Spaces |
| **Production Hardening** | ⏳ Phase 2 | Future |

---

## 📝 Sign-off

- [ ] Code review completed
- [ ] Tests passing
- [ ] Deployment tested on all 3 paths
- [ ] Documentation approved
- [ ] Ready for public release

**Approver**: ___________  
**Date**: ___________

