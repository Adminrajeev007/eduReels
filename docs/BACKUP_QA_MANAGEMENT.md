# Managing the Backup Q&A Database

## Quick Reference

### View Available Q&A Topics

```bash
curl http://localhost:8000/api/backup-qa/stats | jq '.degrees[].topics'
```

### Get a Specific Q&A

```bash
# Computer Science - Big O Notation
curl "http://localhost:8000/api/backup-qa/Computer%20Science/Big%20O%20Notation"

# Electrical Engineering - Ohm's Law
curl "http://localhost:8000/api/backup-qa/Electrical%20Engineering/Ohm%27s%20Law"

# Mechanical Engineering - Newton's Laws
curl "http://localhost:8000/api/backup-qa/Mechanical%20Engineering/Newton%27s%20Laws"
```

### Add New Q&A Programmatically

```python
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()

# Add a new question
qa_db.add_custom_qa(
    degree="Computer Science",
    topic="Blockchain Technology",
    question="What is blockchain and how does it work?",
    answer="Blockchain is a distributed ledger technology that records transactions in blocks...",
    analogy="Blockchain is like a notebook that everyone has a copy of, and everyone agrees on what's written.",
    hook="Bitcoin uses blockchain to prevent counterfeiting!",
    examples=[
        "Bitcoin: Currency on blockchain",
        "Ethereum: Smart contracts on blockchain",
        "Supply chain: Track product origin"
    ],
    quality_score=8.5,
    engagement_score=8.0
)

print("✅ New Q&A added successfully!")
```

## Database Structure

### backup_qa.db Tables

#### Table: backup_qa

| Column           | Type      | Description                                                         |
| ---------------- | --------- | ------------------------------------------------------------------- |
| id               | INTEGER   | Primary key                                                         |
| degree           | TEXT      | Computer Science, Electrical Engineering, or Mechanical Engineering |
| topic            | TEXT      | Topic name                                                          |
| question         | TEXT      | Full question text                                                  |
| answer           | TEXT      | Detailed answer                                                     |
| analogy          | TEXT      | Helpful analogy                                                     |
| hook             | TEXT      | Engaging hook                                                       |
| examples         | TEXT      | JSON array of examples                                              |
| quality_score    | REAL      | Quality rating (0-10)                                               |
| engagement_score | REAL      | Engagement rating (0-10)                                            |
| created_at       | TIMESTAMP | When added                                                          |
| last_served      | TIMESTAMP | When last served                                                    |
| serve_count      | INTEGER   | Number of times served                                              |

## Current Content Summary

### Computer Science (5 Questions)

- Big O Notation
- Data Structures
- Recursion
- Databases
- API Design

### Electrical Engineering (5 Questions)

- Ohm's Law
- Circuit Analysis
- Power Systems
- Transformers
- Semiconductors

### Mechanical Engineering (5 Questions)

- Newton's Laws
- Thermodynamics
- Stress and Strain
- Fluid Mechanics
- Machine Design

## Scripts for Management

### View All Q&A

```python
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()
degrees = ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]

for degree in degrees:
    print(f"\n{'='*50}")
    print(f"{degree}")
    print(f"{'='*50}")

    topics = qa_db.get_all_topics(degree)
    for topic in topics:
        qa = qa_db.get_by_topic(degree, topic)
        print(f"\n📌 {topic}")
        print(f"   Q: {qa['question']}")
        print(f"   Serves: {qa['serve_count']}")
```

### Statistics Report

```python
from tools.qa_database import QADatabaseManager
from datetime import datetime

qa_db = QADatabaseManager()
degrees = ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]

print(f"\n📊 BACKUP Q&A DATABASE REPORT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}")

total_questions = 0
total_serves = 0

for degree in degrees:
    stats = qa_db.get_stats(degree)
    total_questions += stats['total_questions']
    total_serves += stats['total_serves']

    print(f"\n{degree}:")
    print(f"  Questions: {stats['total_questions']}")
    print(f"  Topics: {stats['unique_topics']}")
    print(f"  Total Serves: {stats['total_serves']}")
    print(f"  Avg Quality: {stats['avg_quality']}/10")

print(f"\n{'='*60}")
print(f"Total Questions: {total_questions}")
print(f"Total Serves: {total_serves}")
print(f"Avg Serves per Q: {total_serves / total_questions:.1f}")
```

### Batch Add Q&A

```python
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()

# Batch add multiple Q&A pairs
new_questions = [
    {
        'degree': 'Computer Science',
        'topic': 'Machine Learning',
        'question': 'What is overfitting in machine learning?',
        'answer': 'Overfitting occurs when a model learns the training data too well...',
        'analogy': 'Like memorizing answers for an exam instead of understanding concepts.',
        'hook': 'Even the smartest model can fail with overfitting!',
        'examples': ['Model has 95% training accuracy, 50% test accuracy'],
        'quality_score': 8.5,
        'engagement_score': 8.0
    },
    {
        'degree': 'Computer Science',
        'topic': 'Distributed Systems',
        'question': 'What is eventual consistency?',
        'answer': 'Eventual consistency means that all replicas will eventually converge to the same state...',
        'analogy': 'Like gossip spreading through a group - eventually everyone knows.',
        'hook': 'Netflix uses eventual consistency to serve billions of users!',
        'examples': ['DNS caches', 'Social media likes', 'Database replication'],
        'quality_score': 8.0,
        'engagement_score': 7.5
    }
]

for qa in new_questions:
    qa_db.add_custom_qa(**qa)
    print(f"✅ Added: {qa['topic']}")
```

## Best Practices

### 1. Quality Q&A Guidelines

When adding new Q&A:

- ✅ Quality score 7.5-10.0
- ✅ Engagement score 7.0-10.0
- ✅ Clear, beginner-friendly answers
- ✅ Helpful analogies included
- ✅ At least 2-3 relevant examples
- ✅ Engaging hook to catch attention

### 2. Answer Format

```
Answer structure:
1. Direct answer to question
2. Key concepts explained
3. Why it matters
4. Common misconceptions cleared
```

### 3. Analogy Guidelines

Good analogies:

- ✅ Relate to everyday items
- ✅ Are easy to understand
- ✅ Maintain technical accuracy
- ✅ Help with memory retention

Bad analogies:

- ❌ Too technical (defeats the purpose)
- ❌ Too simple (lose important details)
- ❌ Incorrect (mislead learners)

### 4. Hook Guidelines

Good hooks:

- ✅ Ask a question
- ✅ Start with "Did you know?"
- ✅ Mention real-world application
- ✅ Create curiosity

## Maintenance Tasks

### Weekly

```bash
# Check database size
du -h data/backup_qa.db

# View serving statistics
curl http://localhost:8000/api/backup-qa/stats | jq '.degrees'
```

### Monthly

```python
# Generate detailed report
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()

for degree in ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]:
    stats = qa_db.get_stats(degree)
    print(f"{degree}: {stats['total_serves']} serves this month")
```

### Quarterly

- Review least-served questions
- Update outdated content
- Add trending topics
- Improve quality scores

## Troubleshooting

### Q&A Not Serving

```python
# Debug: Check if topic exists
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()
topics = qa_db.get_all_topics("Computer Science")
print(f"Available topics: {topics}")

# Check specific Q&A
qa = qa_db.get_by_topic("Computer Science", "Big O Notation")
print(f"Q&A found: {qa is not None}")
```

### Database Corrupted

```bash
# Backup current database
cp data/backup_qa.db data/backup_qa.db.backup

# Delete and recreate
rm data/backup_qa.db

# Restart API - it will recreate with defaults
# Then add custom Q&A back
```

### Statistics Not Updating

```python
# Force refresh serve counts
from tools.qa_database import QADatabaseManager
import sqlite3

qa_db = QADatabaseManager()

# Check last served timestamp
conn = sqlite3.connect('data/backup_qa.db')
result = conn.execute(
    "SELECT topic, serve_count, last_served FROM backup_qa WHERE degree = ?",
    ("Computer Science",)
).fetchall()

for topic, serves, last_served in result:
    print(f"{topic}: {serves} serves, last served: {last_served}")

conn.close()
```

## Integration Examples

### Get Random Q&A for User

```python
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()

# Get random Q&A for a degree
qa = qa_db.get_random_qa("Computer Science")

if qa:
    print(f"Question: {qa['question']}")
    print(f"Answer: {qa['answer']}")
    print(f"Hook: {qa['hook']}")
    print(f"Analogy: {qa['analogy']}")
    print(f"Examples: {qa['examples']}")
```

### API Usage Pattern

```javascript
// Frontend: Load reel with backup fallback
async function loadReel(degree) {
	const response = await fetch(`/api/reels?degree=${degree}&count=1`);
	const data = await response.json();

	const reel = data.reels[0];

	// Display based on source
	if (reel.source === "pre-generated-queue") {
		showBadge("Fresh Content", "success");
	} else if (reel.source === "backup-qa-database") {
		showBadge("Loading Fresh Content...", "info");
	} else if (reel.source === "on-demand-generation") {
		showBadge("Generating...", "warning");
	}

	displayReel(reel);
}
```

## Export/Import

### Export Q&A to CSV

```python
import csv
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()
degrees = ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]

with open('backup_qa_export.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'degree', 'topic', 'question', 'answer', 'analogy', 'hook',
        'examples', 'quality_score', 'engagement_score'
    ])
    writer.writeheader()

    for degree in degrees:
        topics = qa_db.get_all_topics(degree)
        for topic in topics:
            qa = qa_db.get_by_topic(degree, topic)
            writer.writerow({
                'degree': qa['degree'],
                'topic': qa['topic'],
                'question': qa['question'],
                'answer': qa['answer'],
                'analogy': qa['analogy'],
                'hook': qa['hook'],
                'examples': str(qa['examples']),
                'quality_score': qa['quality_score'],
                'engagement_score': qa['engagement_score']
            })

print("✅ Exported to backup_qa_export.csv")
```

---

**Last Updated:** March 21, 2026  
**Status:** ✅ Production Ready
