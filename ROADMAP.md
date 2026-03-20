# Educational Reels AI Agents Platform — Complete Roadmap

**Project:** Multi-Agent AI Educational Platform for B.Tech Students  
**Budget:** $0 (GitHub Education Pack)  
**Duration:** 4 weeks  
**Target Users:** Engineering students (Computer Science, Electrical, Mechanical)

---

## 🎯 Project Overview

### Mission

Build a reels-style educational platform powered by specialized AI agents that generate engaging, quality-assured technical questions with simplified answers for engineering students.

### Core Constraints

- ✅ GitHub Education Pack tools only (Copilot Pro, Codespaces)
- ✅ Free-tier AI models (ChatGPT + Hugging Face backup)
- ✅ Multi-agent architecture (not single API calls)
- ✅ $0 budget (completely free)

### Success Criteria

- Uncached response time: < 12 seconds
- Cached response time: < 2 seconds
- Average quality score: ≥ 7.5/10
- Content format: 10-20 word question, 30-50 word answer

---

## 📋 Week 1: Foundation & Setup

### Week 1 Goals

✅ Verify all prerequisites  
✅ Create project structure  
✅ Set up development environment  
✅ Validate model connectivity

### Week 1 Tasks

#### Day 1–2: Prerequisites & Planning

- [ ] Verify GitHub Student Pack approval
- [ ] Claim Copilot Pro (1 year free)
- [ ] Claim Codespaces free hours
- [ ] Create GitHub Pro account features list
- [ ] Create OpenAI account (ChatGPT free tier)
- [ ] Create Hugging Face account
- [ ] Create Render.com account (for Week 4 deployment)
- [ ] Finalize supported branches: Computer Science, Electrical, Mechanical
- [ ] Lock MVP output schema
  - reel_question (10-20 words)
  - reel_answer (30-50 words)
  - hook
  - share_appeal
  - quality_score
  - metadata (topic, model_used, cached, timestamp)

#### Day 3–4: Project Structure

- [ ] Initialize Git repository
- [ ] Create directory structure:
  ```
  educational-reels-agent/
  ├── agents/
  │   ├── __init__.py
  │   ├── orchestrator.py
  │   ├── research_agent.py
  │   ├── question_generator.py
  │   ├── quality_checker.py
  │   ├── answer_simplifier.py
  │   ├── example_finder.py
  │   └── engagement_optimizer.py
  ├── tools/
  │   ├── __init__.py
  │   ├── model_connector.py
  │   ├── prompt_templates.py
  │   └── cache_manager.py
  ├── api/
  │   ├── __init__.py
  │   ├── app.py
  │   └── routes.py
  ├── frontend/
  │   ├── index.html
  │   └── reels.html
  ├── tests/
  │   └── test_agents.py
  ├── data/
  │   └── .gitkeep
  ├── .env.example
  ├── requirements.txt
  ├── README.md
  └── agent_workflow.md
  ```
- [ ] Create `requirements.txt` with dependencies:
  ```
  fastapi==0.104.1
  uvicorn==0.24.0
  python-dotenv==1.0.0
  openai==1.3.0
  huggingface-hub==0.17.0
  requests==2.31.0
  pydantic==2.5.0
  ```
- [ ] Create `.env.example`:
  ```
  OPENAI_API_KEY=your_key_here
  HUGGINGFACE_TOKEN=your_token_here
  ENVIRONMENT=development
  ```
- [ ] Set up Python virtual environment
  ```bash
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

#### Day 5: Model Connectivity

- [ ] Create `tools/model_connector.py` with:
  - ChatGPT primary model path
  - Hugging Face fallback model path
  - Error handling + retry logic (1-2 retries)
  - Async support
- [ ] Create `tools/prompt_templates.py` with:
  - All 7 agent prompt templates
  - Centralized prompt management
  - Easy update mechanism
- [ ] Create `tools/cache_manager.py` with:
  - SQLite cache interface
  - Cache hit/miss tracking
  - TTL policy (3-7 days for common requests)
- [ ] Test model connector:
  ```bash
  python -c "from tools.model_connector import ModelConnector; m = ModelConnector(); print(m.test_connection())"
  ```

### Week 1 Deliverables

- ✅ Project structure created and Git initialized
- ✅ All Python dependencies installed
- ✅ Model connector working with fallback
- ✅ Prompt templates centralized
- ✅ Cache manager interface ready
- ✅ First successful test call to model

### Week 1 Exit Criteria

- [ ] Run `python -m pytest tests/test_connectivity.py` → PASS
- [ ] One test prompt returns parseable JSON output
- [ ] Cache manager can store and retrieve test data

---

## 🤖 Week 2: Core Agent Pipeline (Research → Question → Quality)

### Week 2 Goals

✅ Implement the question generation pipeline  
✅ Add quality validation loop  
✅ Wire orchestrator to coordinate agents

### Week 2 Tasks

#### Day 6–7: Research Agent

- [ ] Create `agents/research_agent.py`:
  - Input: degree name
  - Output: 3 interesting topics with scores
  - Constraints: intermediate level, real-world applicable, thought-provoking
  - JSON schema validation
- [ ] Add test cases:
  - Happy path (known degree)
  - Edge case (unknown degree)
  - Schema validation
- [ ] Verify output for all 3 branches:
  - Computer Science ✓
  - Electrical Engineering ✓
  - Mechanical Engineering ✓

#### Day 8–9: Question Generator Agent

- [ ] Create `agents/question_generator.py`:
  - Input: degree, topic, research context
  - Output: engaging question (non-"What is" format)
  - Enforce patterns: Why/How/What-if/Compare
  - JSON schema validation
- [ ] Add test cases:
  - Happy path (good topic)
  - Edge case (vague topic)
  - Format enforcement
- [ ] Verify questions follow anti-patterns:
  - ❌ NOT "What is..."
  - ❌ NOT "Define..."
  - ❌ NOT "List the..."
  - ✅ YES "Why does..."
  - ✅ YES "What would happen if..."

#### Day 10–11: Quality Check Agent

- [ ] Create `agents/quality_checker.py`:
  - Input: degree, question
  - Output: quality_score (0-10), pass/fail, suggestions
  - Check 5 criteria (basic-ness, engagement, relevance, interest, learning point)
  - Threshold: score < 7 → suggest improvements
- [ ] Add regeneration path:
  - If quality fails → ask Question Generator to regenerate
  - Max 2 regeneration attempts
- [ ] Add test cases:
  - Happy path (good question)
  - Edge case (bad question)
  - Regeneration path test

#### Day 12: Orchestrator (Core Loop)

- [ ] Create `agents/orchestrator.py`:
  - Input: degree
  - Sequence: Research → Generator → Quality Check
  - Cache check before generation
  - Fallback on model failure
  - Logging for each stage
- [ ] Add JSON validation + retry policy:
  - Validate output from each agent
  - Retry 1-2 times on malformed output
  - Log all failures
- [ ] Wire all three agents:
  ```python
  orchestrator = EducationalReelsOrchestrator()
  result = await orchestrator.generate_question("Computer Science")
  ```

### Week 2 Testing

- [ ] Unit tests for each agent
- [ ] Integration test: Research → Generator → Quality
- [ ] Cache mechanism test
- [ ] Fallback model test

### Week 2 Deliverables

- ✅ 3 agents implemented (Research, Generator, Quality)
- ✅ Orchestrator wiring all three agents
- ✅ Quality validation loop working
- ✅ Fallback + retry logic implemented
- ✅ Per-agent logging enabled

### Week 2 Exit Criteria

- [ ] Generate question for all 3 branches → all return valid JSON
- [ ] Quality check rejects low-quality questions
- [ ] Regeneration path works on quality failure
- [ ] Cache successfully stores and retrieves generated question
- [ ] Test suite: `pytest tests/ -v` → all pass

---

## 🧠 Week 3: Answer Quality & Engagement

### Week 3 Goals

✅ Add answer simplification with analogies  
✅ Add real-world examples  
✅ Optimize for reels format

### Week 3 Tasks

#### Day 13–14: Answer Simplifier Agent

- [ ] Create `agents/answer_simplifier.py`:
  - Input: question, technical answer
  - Output: simple_answer (with analogy), analogy_used, key_takeaway
  - Rules: < 50 words, everyday analogies, memorable, connected to question
  - Examples: RAM vs SSD as desk vs filing cabinet
- [ ] Generate raw answer first:
  - Create answer generation logic in orchestrator
  - Input: degree, question
  - Output: technical answer from model
- [ ] Test with different question types:
  - Memory hierarchy questions ✓
  - Electrical circuit questions ✓
  - Mechanical engineering questions ✓

#### Day 15–16: Example Finder Agent

- [ ] Create `agents/example_finder.py`:
  - Input: topic, simple_answer
  - Output: real_world_example, why_it_works, enhanced_answer
  - Constraint: must be relatable to students (daily life)
  - Examples: laptop slowdown for RAM concept
- [ ] Combine with answer simplifier:
  - Enhance simplified answer with example
  - Keep total length manageable

#### Day 17–18: Engagement Optimizer Agent

- [ ] Create `agents/engagement_optimizer.py`:
  - Input: question, enhanced_answer
  - Output: reel_question (10-20 words), reel_answer (30-50 words), hook, share_appeal
  - Compress while maintaining engagement
  - Add "aha moment" to answer
  - Create curiosity gap in question
- [ ] Test reels format constraints:
  - Question length ✓ (10-20 words max)
  - Answer length ✓ (30-50 words max)
  - Hook present ✓
  - Payoff clear ✓

#### Day 19: End-to-End Pipeline

- [ ] Wire all 9 agents in orchestrator:
  - Research → Generator → Quality → Answer Gen → Simplifier → Example → Optimizer
- [ ] Test full pipeline:
  ```python
  result = await orchestrator.generate_reel_content("Computer Science")
  # Output: complete reel payload with all stages logged
  ```
- [ ] Add comprehensive logging
- [ ] Performance profiling:
  - Uncached: should be < 12s
  - Cached: should be < 2s

### Week 3 Testing

- [ ] Agent-level tests (each of 3 new agents)
- [ ] Integration tests (full pipeline)
- [ ] Output quality validation
- [ ] Length constraint validation
- [ ] Performance tests

### Week 3 Deliverables

- ✅ 3 new agents (Simplifier, Example, Optimizer)
- ✅ Raw answer generation logic
- ✅ Full end-to-end pipeline working
- ✅ Output meets reels format constraints
- ✅ Performance targets met

### Week 3 Exit Criteria

- [ ] Full pipeline generates reel from degree input
- [ ] All output fields present and valid
- [ ] Question length 10-20 words ✓
- [ ] Answer length 30-50 words ✓
- [ ] Average generation time < 12s (uncached) ✓
- [ ] Cached response time < 2s ✓

---

## 🌐 Week 4: API + Frontend + Deployment

### Week 4 Goals

✅ Expose orchestrator via REST API  
✅ Build minimal frontend UI  
✅ Deploy to Render free tier  
✅ Conduct pilot validation

### Week 4 Tasks

#### Day 20–21: FastAPI Backend

- [ ] Create `api/app.py`:
  - Initialize FastAPI app
  - Setup CORS for frontend
  - Load environment variables
  - Initialize orchestrator
- [ ] Create `api/routes.py`:
  - `POST /generate` endpoint:
    - Input: `{ "degree": "Computer Science" }`
    - Output: complete reel payload
    - Error handling with appropriate status codes
  - `GET /health` endpoint:
    - Check model connectivity
    - Return service status
  - `GET /metrics` endpoint:
    - Return: questions_generated, avg_quality_score, cache_hit_rate, avg_response_time
- [ ] Add request validation:
  - Pydantic models for input/output
  - Error handling and logging
- [ ] Test endpoints locally:
  ```bash
  python -m uvicorn api.app:app --reload
  # Test: curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d '{"degree": "Computer Science"}'
  ```

#### Day 22–23: Frontend UI

- [ ] Create `frontend/index.html`:
  - Degree input (dropdown or text)
  - Generate button
  - Loading state
  - Redirect to `/reels.html` after generation
- [ ] Update `frontend/reels.html`:
  - Fullscreen reel card display
  - Show: hook, question, answer, example, share_appeal
  - "Generate another" button
  - "Share" buttons (social integration)
  - Mobile-responsive design
- [ ] Connect to backend:
  ```javascript
  const response = await fetch("http://localhost:8000/generate", {
  	method: "POST",
  	headers: { "Content-Type": "application/json" },
  	body: JSON.stringify({ degree: selectedDegree }),
  });
  ```
- [ ] Add error handling and UI feedback

#### Day 24: Deployment Setup

- [ ] Create `render.yaml`:
  ```yaml
  services:
    - type: web
      name: educational-reels-agent
      env: python
      buildCommand: pip install -r requirements.txt
      startCommand: uvicorn api.app:app --host 0.0.0.0 --port $PORT
      envVars:
        - key: OPENAI_API_KEY
          sync: false
        - key: HUGGINGFACE_TOKEN
          sync: false
  ```
- [ ] Create `.github/workflows/deploy.yml` for CI/CD (optional)
- [ ] Test production setup locally:
  ```bash
  gunicorn -w 4 -b 0.0.0.0:8000 api.app:app
  ```

#### Day 25–26: Deploy to Production

- [ ] Push code to GitHub
- [ ] Connect Render.com:
  - Link GitHub repo
  - Set environment variables
  - Deploy
- [ ] Test live endpoints:
  ```bash
  curl https://your-app.onrender.com/health
  curl -X POST https://your-app.onrender.com/generate -H "Content-Type: application/json" -d '{"degree": "Computer Science"}'
  ```
- [ ] Test frontend on mobile browser
- [ ] Collect live URL

#### Day 27–28: Pilot & Feedback

- [ ] Share live URL with 5–10 students
- [ ] Create feedback form:
  - Interest score (1-10)
  - Clarity score (1-10)
  - Would you share? (Yes/No)
  - Any suggestions?
- [ ] Collect feedback:
  - At least 70% should find content useful + engaging
- [ ] Track metrics:
  - Total questions generated
  - Average quality score
  - Cache hit rate
  - Most popular branch

### Week 4 Testing

- [ ] API endpoint tests (Postman/curl)
- [ ] Frontend interaction tests
- [ ] End-to-end flow (input → output → display)
- [ ] Mobile responsiveness tests
- [ ] Production deployment tests

### Week 4 Deliverables

- ✅ FastAPI backend with 3 endpoints
- ✅ Frontend UI (index + reels)
- ✅ Deployment configuration
- ✅ Live deployment on Render
- ✅ Pilot feedback collected
- ✅ Metrics dashboard data

### Week 4 Exit Criteria

- [ ] `POST /generate` returns valid reel in < 12s (uncached)
- [ ] `GET /health` returns 200 OK
- [ ] `GET /metrics` returns metrics object
- [ ] Frontend displays reel correctly
- [ ] Mobile browser works (tested on phone)
- [ ] ≥ 70% pilot users rate as useful + engaging
- [ ] All 3 branches generate content successfully
- [ ] Cache hit rate > 30% (after repeat requests)

---

## 📊 Success Metrics Dashboard

Track these throughout the project:

```
WEEK 1:
- Project setup: 100% ✓
- Model connectivity: PASS ✓
- Test coverage: baseline established

WEEK 2:
- Questions generated: 50+
- Avg quality score: 7.5+/10
- Cache hit rate: N/A (first run)
- Fallback model usage: < 10%

WEEK 3:
- Full pipeline generation time: < 12s (uncached)
- Cached generation time: < 2s
- Output format compliance: 100%
- User readability: 15 seconds for full answer

WEEK 4:
- Live URL: Active ✓
- API endpoints: All functional ✓
- Pilot users: 5-10
- Satisfaction score: ≥ 70%
- Questions generated (total): 100+
```

---

## ⚠️ Risk Management

### Risk 1: Free-tier API rate limits

**Probability:** High  
**Impact:** Generation slowdown  
**Mitigation:**

- Aggressive caching (key: degree)
- Use Hugging Face backup when ChatGPT rate limited
- Keep prompts short (< 500 tokens)

### Risk 2: Malformed model outputs

**Probability:** Medium  
**Impact:** Pipeline breaks  
**Mitigation:**

- Strict JSON schema validation
- Retry logic (1-2 retries)
- Fallback to template answers if all fails

### Risk 3: Low engagement content

**Probability:** Medium  
**Impact:** Users don't find it useful  
**Mitigation:**

- Quality threshold at each stage (min score 7)
- User feedback loop
- Continuous prompt tuning

### Risk 4: Deployment failure

**Probability:** Low  
**Impact:** Platform unavailable  
**Mitigation:**

- Test locally before deploy
- Use free tier with backup provider
- Monitor uptime via Render dashboard

---

## 🔄 Next Steps After Week 4

### If Pilot is Successful (≥70% satisfaction):

1. **Week 5+: Expansion**
   - Add more branches (Civil, Chemical, Electronics)
   - Implement user authentication
   - Add question history/favorites
   - Build admin dashboard

2. **Performance Optimization**
   - Upgrade to MongoDB Atlas (better caching)
   - Add question pre-generation for popular branches
   - Implement vector search for similar questions

3. **Monetization (Optional)**
   - Premium features (custom branches, export)
   - Sponsored placement (educational content)
   - B2B licensing to colleges

### If Pilot Feedback is Mixed:

1. **Quick Fixes:**
   - Adjust quality thresholds
   - Refine engagement optimizer prompts
   - Add more real-world examples

2. **Iterate:**
   - Collect more targeted feedback
   - Adjust agent prompts based on user comments
   - Run second pilot wave

---

## 📝 How to Use This Roadmap

1. **Print or bookmark** this file: `ROADMAP.md`
2. **Track progress** with checkboxes (check off as completed)
3. **Share with team** if collaborating
4. **Review weekly** and adjust if needed
5. **Reference during development** for clarity on requirements

---

## 🚀 Quick Start Command

When ready to begin:

```bash
# Week 1 kickoff
cd /Users/rahulkumar/Desktop/edureels
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Then ask me: "Create Week 1 foundation files"
```

---

**Last Updated:** 20 March 2026  
**Status:** Ready to start Week 1  
**Next Action:** Confirm prerequisites complete → Begin Week 1 tasks
