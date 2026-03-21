# Backup Q&A System - Quick Reference Card

## System at a Glance

```
User requests reel
    ↓
Check queue (pre-generated)
    ├─ Has content → Serve from queue (< 100ms) ✅
    └─ Empty → Serve from Backup Q&A (< 50ms) ✅
                While background generator fills queue
```

## API Endpoints Quick Reference

### 1. Enhanced /api/reels (Main Endpoint)

```bash
# Get a random question (auto-fallback to backup if queue empty)
curl "http://localhost:8000/api/reels?degree=Computer%20Science&count=1"

# Response includes:
# - "source": "backup-qa-database" OR "pre-generated-queue"
# - Complete Q&A with question, answer, analogy, hook, examples
# - Queue status and statistics
```

### 2. /api/backup-qa/stats (View All Q&A)

```bash
curl http://localhost:8000/api/backup-qa/stats

# Returns:
# - All 15 Q&A pairs organized by degree
# - Topics available
# - Serve counts and quality metrics
```

### 3. /api/backup-qa/{degree}/{topic} (Get Specific Q&A)

```bash
# Example: Get Big O Notation Q&A
curl "http://localhost:8000/api/backup-qa/Computer%20Science/Big%20O%20Notation"

# Returns:
# - Complete Q&A pair
# - Serve history
# - Quality scores
```

## Available Topics

**Computer Science:**

- Big O Notation
- Data Structures
- Recursion
- Databases
- API Design

**Electrical Engineering:**

- Ohm's Law
- Circuit Analysis
- Power Systems
- Transformers
- Semiconductors

**Mechanical Engineering:**

- Newton's Laws
- Thermodynamics
- Stress and Strain
- Fluid Mechanics
- Machine Design

## Adding Custom Content

```python
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()

qa_db.add_custom_qa(
    degree="Computer Science",
    topic="Your Topic",
    question="Your question here?",
    answer="Detailed answer here...",
    analogy="Helpful comparison...",
    hook="Engaging teaser...",
    examples=["Example 1", "Example 2", "Example 3"],
    quality_score=8.5,
    engagement_score=8.0
)
```

## Python Examples

### Get Random Q&A

```python
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()
qa = qa_db.get_random_qa("Computer Science")

print(f"Q: {qa['question']}")
print(f"A: {qa['answer']}")
print(f"Hook: {qa['hook']}")
```

### Get Specific Topic

```python
qa = qa_db.get_by_topic("Computer Science", "Big O Notation")
```

### Get All Topics

```python
topics = qa_db.get_all_topics("Computer Science")
print(topics)
```

### Get Statistics

```python
stats = qa_db.get_stats("Computer Science")
print(f"Total questions: {stats['total_questions']}")
print(f"Total serves: {stats['total_serves']}")
print(f"Avg quality: {stats['avg_quality']}")
```

## Performance Comparison

| Metric        | Backup Q&A  | Queue         | On-Demand      |
| ------------- | ----------- | ------------- | -------------- |
| Response Time | < 50ms      | < 100ms       | 5-10s          |
| Data Source   | Database    | Pre-generated | Generated live |
| Scenario      | Queue empty | Queue filled  | Fallback       |

## Database Location

```
data/backup_qa.db
```

SQLite database with:

- Table: `backup_qa` (15 rows)
- Auto-created on startup
- Auto-populated with default content

## File Organization

```
edureels/
├── tools/
│   └── qa_database.py           ← Main module
├── api/
│   └── main.py                  ← API endpoints
├── data/
│   └── backup_qa.db             ← Database
└── docs/
    ├── BACKUP_QA_QUICKSTART.md  ← This guide
    ├── BACKUP_QA_SYSTEM.md      ← Complete docs
    ├── BACKUP_QA_MANAGEMENT.md  ← Operations
    └── BACKUP_QA_SUMMARY.md     ← Details
```

## Response Format

```json
{
	"status": "success",
	"count": 1,
	"degree": "Computer Science",
	"reels": [
		{
			"id": 1,
			"degree": "Computer Science",
			"topic": "Data Structures",
			"question": "What is the difference between an array and a linked list?",
			"answer": "Arrays store elements in contiguous memory...",
			"analogy": "An array is like a row of numbered lockers...",
			"hook": "Choosing the right data structure can make your code 100x faster!",
			"examples": ["Array access: O(1)", "Insertion: O(n)"],
			"quality_score": 9.0,
			"engagement_score": 8.5,
			"cached": false,
			"timestamp": "2026-03-21T07:05:36",
			"source": "backup-qa-database"
		}
	],
	"message": "Serving from backup Q&A database while generating fresh content",
	"queue_status": {
		"queue_size": 0,
		"target_size": 5
	},
	"api_version": "1.0.0"
}
```

## Common Tasks

### Check What's Available

```bash
curl http://localhost:8000/api/backup-qa/stats | jq '.degrees'
```

### Get CS Question

```bash
curl "http://localhost:8000/api/reels?degree=Computer%20Science&count=1"
```

### Get EE Question

```bash
curl "http://localhost:8000/api/reels?degree=Electrical%20Engineering&count=1"
```

### Get ME Question

```bash
curl "http://localhost:8000/api/reels?degree=Mechanical%20Engineering&count=1"
```

### Get Specific Topic

```bash
curl "http://localhost:8000/api/backup-qa/Computer%20Science/Recursion"
```

## Monitoring

### View Current Stats

```bash
curl http://localhost:8000/api/backup-qa/stats
```

### Check Serve Counts

```bash
curl http://localhost:8000/api/backup-qa/stats | jq '.degrees[].total_serves'
```

### See Queue Status

```bash
curl http://localhost:8000/api/reels/status | jq '.degrees'
```

## Key Metrics

- **Total Q&A Pairs:** 15
- **Average Quality Score:** 8.5/10
- **Average Engagement Score:** 8.0/10
- **Response Time (Backup):** < 50ms
- **Response Time (Queue):** < 100ms
- **Database Size:** ~50KB

## Troubleshooting

**Q&A not loading?**

```bash
curl http://localhost:8000/api/backup-qa/stats
```

Check if database exists and has content.

**Getting wrong data?**

```bash
curl http://localhost:8000/api/backup-qa/stats | jq '.degrees.["Computer Science"].topics'
```

Verify available topics.

**Slow response?**
Check `source` field - should be "backup-qa-database" (< 50ms) or "pre-generated-queue" (< 100ms).

## Integration Notes

- ✅ Works with existing API
- ✅ No frontend changes needed
- ✅ Transparent fallback
- ✅ All source data included in response
- ✅ Statistics available via API

## Status

**Current:** ✅ Production Ready  
**Database:** ✅ 15 default Q&A loaded  
**API:** ✅ All endpoints working  
**Tests:** ✅ All passing  
**Performance:** ✅ Verified < 50ms

---

**For detailed documentation:** See `BACKUP_QA_SYSTEM.md`  
**For management guide:** See `BACKUP_QA_MANAGEMENT.md`  
**For implementation details:** See `BACKUP_QA_SUMMARY.md`
