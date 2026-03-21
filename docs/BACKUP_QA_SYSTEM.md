# Backup Q&A Database System - Documentation

## Overview

The Backup Q&A Database system provides **instant fallback content** when the pre-generated reel queue is empty or being populated. This ensures users always see educational content immediately while the background generator fills the queue with fresh, AI-generated content.

## Architecture

### System Flow

```
User requests reel
    ↓
Check queue size
    ├─ Queue has reels? → Serve from queue (< 1s) ✅
    └─ Queue empty?
        ├─ Serve from Backup Q&A (instant) ✅
        └─ Background generator continues generating (in background)
```

### Components

#### 1. **QADatabaseManager** (`tools/qa_database.py`)

**Purpose:** Manage the backup Q&A database with full CRUD operations

**Database:** SQLite (`data/backup_qa.db`)

**Tables:**
- `backup_qa`: Stores Q&A pairs with metadata
  - `id`: Primary key
  - `degree`: Computer Science, Electrical Engineering, or Mechanical Engineering
  - `topic`: Topic name (e.g., "Big O Notation")
  - `question`: Full question text
  - `answer`: Detailed answer
  - `analogy`: Analogy to help understand concept
  - `hook`: Engaging hook/teaser
  - `examples`: JSON array of examples
  - `quality_score`: Quality rating (0-10)
  - `engagement_score`: Engagement rating (0-10)
  - `serve_count`: Number of times this Q&A has been served
  - `created_at`: When added to database
  - `last_served`: When last served to user

**Key Methods:**

```python
# Get a random Q&A for a degree
qa = qa_database.get_random_qa("Computer Science")

# Get specific Q&A by topic
qa = qa_database.get_by_topic("Computer Science", "Big O Notation")

# Get all topics for a degree
topics = qa_database.get_all_topics("Computer Science")

# Add custom Q&A
qa_database.add_custom_qa(
    degree="Computer Science",
    topic="Custom Topic",
    question="Your question?",
    answer="Your answer",
    analogy="Helpful analogy",
    hook="Engaging hook",
    examples=["Example 1", "Example 2"],
    quality_score=8.5,
    engagement_score=8.0
)

# Get statistics
stats = qa_database.get_stats("Computer Science")
# Returns: {total_questions, unique_topics, total_serves, avg_quality}
```

## API Endpoints

### 1. `/api/reels` - Main Reel Endpoint (Enhanced)

**Behavior:** Serves reels with intelligent fallback logic

```
GET /api/reels?degree=Computer%20Science&count=1
```

**Response when queue empty:**

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
      "answer": "Arrays store elements in contiguous memory locations...",
      "analogy": "An array is like a row of numbered lockers...",
      "hook": "Choosing the right data structure can make your code 100x faster!",
      "examples": [
        "Array access: O(1)",
        "Array insertion: O(n)",
        "Linked list insertion: O(1)"
      ],
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
    "target_size": 5,
    "total_generated": 0,
    "total_served": 0
  },
  "backup_qa_stats": {
    "total_questions": 5,
    "unique_topics": 5,
    "total_serves": 509,
    "avg_quality": 8.5
  },
  "api_version": "1.0.0"
}
```

**Source Indicators:**
- `"source": "pre-generated-queue"` - Served from background-generated queue
- `"source": "backup-qa-database"` - Served from fallback Q&A database
- `"source": "on-demand-generation"` - Generated on-the-fly (slowest)

---

### 2. `/api/backup-qa/stats` - Database Statistics

**Get complete statistics about the backup Q&A database**

```
GET /api/backup-qa/stats
```

**Response:**

```json
{
  "status": "success",
  "timestamp": "2026-03-21T12:36:19.100791",
  "degrees": {
    "Computer Science": {
      "total_questions": 5,
      "unique_topics": 5,
      "total_serves": 201,
      "avg_quality": 8.5,
      "topics": [
        "API Design",
        "Big O Notation",
        "Data Structures",
        "Databases",
        "Recursion"
      ]
    },
    "Electrical Engineering": {
      "total_questions": 5,
      "unique_topics": 5,
      "total_serves": 0,
      "avg_quality": 8.5,
      "topics": [
        "Circuit Analysis",
        "Ohm's Law",
        "Power Systems",
        "Semiconductors",
        "Transformers"
      ]
    },
    "Mechanical Engineering": {
      "total_questions": 5,
      "unique_topics": 5,
      "total_serves": 0,
      "avg_quality": 8.5,
      "topics": [
        "Fluid Mechanics",
        "Machine Design",
        "Newton's Laws",
        "Stress and Strain",
        "Thermodynamics"
      ]
    }
  },
  "total_backup_questions": 15,
  "message": "Backup Q&A database provides instant content while generating fresh reels",
  "api_version": "1.0.0"
}
```

---

### 3. `/api/backup-qa/{degree}/{topic}` - Get Specific Q&A

**Get a specific Q&A pair by degree and topic**

```
GET /api/backup-qa/Computer%20Science/Big%20O%20Notation
```

**Response:**

```json
{
  "status": "success",
  "qa": {
    "id": 1,
    "degree": "Computer Science",
    "topic": "Big O Notation",
    "question": "What is Big O notation and why is it important in algorithms?",
    "answer": "Big O notation describes how an algorithm's performance scales with input size...",
    "analogy": "Think of Big O like fuel efficiency in cars...",
    "hook": "Ever wonder why some apps load instantly while others lag?",
    "examples": [
      "Linear search: O(n)",
      "Binary search: O(log n)",
      "Bubble sort: O(n²)"
    ],
    "quality_score": 8.5,
    "engagement_score": 8.0,
    "created_at": "2026-03-21 07:05:36",
    "last_served": "2026-03-21 07:06:35",
    "serve_count": 63
  },
  "source": "backup-qa-database",
  "api_version": "1.0.0"
}
```

---

## Backup Q&A Content

### Computer Science (5 Topics)

1. **Big O Notation**
   - How algorithms scale with input size
   - Time complexity analysis
   - O(1), O(n), O(n²), O(log n) comparisons

2. **Data Structures**
   - Arrays vs Linked Lists
   - When to use each
   - Performance characteristics

3. **Recursion**
   - Function calling itself
   - Base cases
   - Tree traversal examples

4. **Databases**
   - SQL vs NoSQL
   - Structured vs flexible data
   - Scaling considerations

5. **API Design**
   - REST principles
   - HTTP methods
   - Endpoint design patterns

### Electrical Engineering (5 Topics)

1. **Ohm's Law**
   - V = I × R relationship
   - Voltage, current, resistance
   - Practical applications

2. **Circuit Analysis**
   - Series vs Parallel circuits
   - Total resistance calculations
   - Reliability implications

3. **Power Systems**
   - Power factor
   - Real vs apparent power
   - Industrial efficiency

4. **Transformers**
   - Electromagnetic induction
   - Turns ratio
   - Voltage/current relationships

5. **Semiconductors**
   - Conductors vs Insulators vs Semiconductors
   - Doping
   - Diodes and transistors

### Mechanical Engineering (5 Topics)

1. **Newton's Laws**
   - Law of inertia
   - F = ma
   - Action-reaction pairs

2. **Thermodynamics**
   - First law (energy conservation)
   - Second law (entropy)
   - Perpetual motion impossibility

3. **Stress and Strain**
   - Internal force vs deformation
   - Young's modulus
   - Material selection

4. **Fluid Mechanics**
   - Bernoulli's principle
   - Pressure-velocity relationship
   - Aerodynamic lift

5. **Machine Design**
   - Bearing selection
   - Load capacity
   - Reliability engineering

## Performance Characteristics

### Response Time Comparison

| Source | Time | Scenario |
|--------|------|----------|
| Pre-generated Queue | < 100ms | Queue has reels (best) |
| Backup Q&A Database | < 50ms | Queue empty, fallback |
| On-demand Generation | 5-10s | All other methods failed |

### When Each Source is Used

1. **Queue is not empty** → Serve from pre-generated queue (fastest)
2. **Queue is empty** → Serve from backup Q&A (fast fallback)
3. **Backup unavailable** → Generate on-demand (slowest, fallback)

## Implementation Details

### Database Auto-Population

When the app starts:
1. If `backup_qa.db` doesn't exist, it's created
2. 15 default Q&A pairs are loaded (5 per degree)
3. Each Q&A includes full content:
   - Question
   - Detailed answer
   - Helpful analogy
   - Engaging hook
   - Practical examples
   - Quality and engagement scores

### Intelligent Serving

The `/api/reels` endpoint logic:

```
1. Check if skip_cache=true OR queue is empty
   ├─ If true → Check backup Q&A
   │   ├─ If available → Serve backup Q&A immediately ✅
   │   └─ If unavailable → Generate fresh (slow) ⚠️
   └─ If false → Serve from queue ✅ (fastest)

2. Always include source indicator in response
3. Log serving source for analytics
4. Track serve counts in database
```

### Adding Custom Q&A

To add more Q&A pairs programmatically:

```python
from tools.qa_database import QADatabaseManager

qa_db = QADatabaseManager()

qa_db.add_custom_qa(
    degree="Computer Science",
    topic="Machine Learning",
    question="What is the difference between supervised and unsupervised learning?",
    answer="Supervised learning uses labeled data... Unsupervised learning finds patterns...",
    analogy="Supervised is like learning with a teacher. Unsupervised is self-discovery.",
    hook="Most AI systems today use one of these approaches!",
    examples=[
        "Supervised: Classification, Regression",
        "Unsupervised: Clustering, Dimensionality Reduction"
    ],
    quality_score=8.5,
    engagement_score=8.0
)
```

## Integration with Frontend

The frontend displays backup Q&A seamlessly:

1. **While generating**: Show backup Q&A with note "Loading fresh content..."
2. **Visual indicator**: Display `source` in UI so users know it's backup content
3. **No loading state needed**: Content appears instantly
4. **Smooth transition**: When queue fills, automatically switches to fresh content

### Example Frontend Response Handling

```javascript
async function loadNextReel(degree) {
    const response = await fetch(`/api/reels?degree=${degree}&count=1`);
    const data = await response.json();
    
    const reel = data.reels[0];
    
    // Display content
    displayQuestion(reel.question);
    displayAnswer(reel.answer);
    
    // Show source indicator
    if (reel.source === 'backup-qa-database') {
        showBadge('Generating fresh content...', 'info');
    } else if (reel.source === 'pre-generated-queue') {
        showBadge('', 'hide'); // No badge for pre-generated
    }
}
```

## Monitoring and Maintenance

### Check System Health

```bash
# View backup Q&A stats
curl http://localhost:8000/api/backup-qa/stats

# View queue status
curl http://localhost:8000/api/reels/status

# Get specific topic
curl "http://localhost:8000/api/backup-qa/Computer%20Science/Big%20O%20Notation"
```

### Database Maintenance

```python
# Get statistics for a degree
stats = qa_database.get_stats("Computer Science")
print(f"Total questions: {stats['total_questions']}")
print(f"Total serves: {stats['total_serves']}")
print(f"Avg quality: {stats['avg_quality']}")

# List all topics
topics = qa_database.get_all_topics("Computer Science")
print(f"Available topics: {topics}")
```

## Benefits

✅ **Instant Content Loading** - Users see content immediately  
✅ **No Loading States** - Seamless experience even with slow generation  
✅ **Fallback System** - Always has content to show  
✅ **Quality Ensured** - Curated, high-quality Q&A pairs  
✅ **Analytics Ready** - Track which backup content is used  
✅ **Easy Expansion** - Add more Q&A pairs programmatically  
✅ **Database Persistent** - Content survives server restarts  

## Future Enhancements

1. **Admin Panel** - Web UI to manage backup Q&A
2. **Bulk Import** - Load Q&A from CSV/Excel files
3. **Community Contributions** - Allow users to suggest Q&A pairs
4. **Smart Rotation** - Track least-served questions, prioritize variety
5. **Difficulty Levels** - Serve beginner, intermediate, or advanced Q&A
6. **Multi-language** - Support Q&A in different languages
7. **Custom Fields** - Add related links, video URLs, or additional resources

---

## Quick Start

```bash
# View all available backup Q&A
curl http://localhost:8000/api/backup-qa/stats

# Get a random CS question (when queue empty)
curl "http://localhost:8000/api/reels?degree=Computer%20Science&count=1"

# Get EE question
curl "http://localhost:8000/api/reels?degree=Electrical%20Engineering&count=1"

# Get ME question  
curl "http://localhost:8000/api/reels?degree=Mechanical%20Engineering&count=1"

# Get specific topic
curl "http://localhost:8000/api/backup-qa/Computer%20Science/Big%20O%20Notation"
```

---

**Created:** March 21, 2026  
**Status:** ✅ Production Ready  
**Tested:** All endpoints verified with backup Q&A serving correctly
