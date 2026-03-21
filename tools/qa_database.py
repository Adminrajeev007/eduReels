"""
Backup Q&A Database - Stores pre-curated questions and answers
Used as fallback when live content is generating
Provides instant content to users while background generation completes
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import random

logger = logging.getLogger(__name__)


class QADatabaseManager:
    """Manages backup Q&A database for fallback content"""
    
    def __init__(self, db_path: str = "data/backup_qa.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._populate_default_qa()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_qa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    degree TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    analogy TEXT,
                    hook TEXT,
                    examples TEXT,
                    quality_score REAL DEFAULT 8.0,
                    engagement_score REAL DEFAULT 7.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_served TIMESTAMP,
                    serve_count INTEGER DEFAULT 0
                )
            """)
            
            # Create index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_degree_topic 
                ON backup_qa (degree, topic)
            """)
            
            conn.commit()
            logger.info("✅ Backup Q&A Database initialized")
    
    def _populate_default_qa(self):
        """Populate database with default Q&A pairs if empty"""
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM backup_qa").fetchone()[0]
            
            if count == 0:
                logger.info("📚 Populating backup Q&A database with default content...")
                default_qa = self._get_default_qa_data()
                
                for qa in default_qa:
                    conn.execute("""
                        INSERT INTO backup_qa 
                        (degree, topic, question, answer, analogy, hook, examples, quality_score, engagement_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        qa['degree'],
                        qa['topic'],
                        qa['question'],
                        qa['answer'],
                        qa.get('analogy', ''),
                        qa.get('hook', ''),
                        json.dumps(qa.get('examples', [])),
                        qa.get('quality_score', 8.0),
                        qa.get('engagement_score', 7.5)
                    ))
                
                conn.commit()
                logger.info(f"✅ Added {len(default_qa)} backup Q&A pairs to database")
    
    def _get_default_qa_data(self) -> List[Dict[str, Any]]:
        """Return default Q&A data for all degrees"""
        return [
            # Computer Science
            {
                'degree': 'Computer Science',
                'topic': 'Big O Notation',
                'question': 'What is Big O notation and why is it important in algorithms?',
                'answer': 'Big O notation describes how an algorithm\'s performance scales with input size. It helps us compare algorithms and predict how they perform on large datasets. O(1) is constant time, O(n) is linear, O(n²) is quadratic, and O(log n) is logarithmic.',
                'analogy': 'Think of Big O like fuel efficiency in cars - it tells you roughly how much "work" the algorithm does per unit of input.',
                'hook': 'Ever wonder why some apps load instantly while others lag? It\'s all about Big O!',
                'examples': ['Linear search: O(n)', 'Binary search: O(log n)', 'Bubble sort: O(n²)'],
                'quality_score': 8.5,
                'engagement_score': 8.0
            },
            {
                'degree': 'Computer Science',
                'topic': 'Data Structures',
                'question': 'What is the difference between an array and a linked list?',
                'answer': 'Arrays store elements in contiguous memory locations with fast random access but slow insertions/deletions. Linked lists store elements in nodes with pointers, allowing fast insertions/deletions but slower access. Arrays are O(1) for access but O(n) for insertion. Linked lists are O(n) for access but O(1) for insertion if you have a pointer to the location.',
                'analogy': 'An array is like a row of numbered lockers - you can instantly go to locker 5. A linked list is like a treasure hunt - each clue points to the next location.',
                'hook': 'Choosing the right data structure can make your code 100x faster!',
                'examples': ['Array access: O(1)', 'Array insertion: O(n)', 'Linked list insertion: O(1)'],
                'quality_score': 9.0,
                'engagement_score': 8.5
            },
            {
                'degree': 'Computer Science',
                'topic': 'Recursion',
                'question': 'What is recursion and when should you use it?',
                'answer': 'Recursion is when a function calls itself with a simpler version of the problem until reaching a base case. Use recursion for problems naturally structured as smaller subproblems like tree traversal, factorial calculation, and divide-and-conquer algorithms. Always have a base case to avoid infinite loops.',
                'analogy': 'Recursion is like Russian nesting dolls - each doll contains a smaller version until you reach the tiniest doll.',
                'hook': 'To understand recursion, you must first understand recursion!',
                'examples': ['Factorial: n! = n × (n-1)!', 'Tree traversal', 'Binary search'],
                'quality_score': 8.5,
                'engagement_score': 8.0
            },
            {
                'degree': 'Computer Science',
                'topic': 'Databases',
                'question': 'What is SQL and how does it differ from NoSQL?',
                'answer': 'SQL databases use structured tables with predefined schemas and are great for relational data. NoSQL databases are flexible, unstructured, and handle massive scale better. SQL ensures ACID properties. NoSQL prioritizes availability and partition tolerance. Choose SQL for structured data with relationships, NoSQL for flexible, large-scale data.',
                'analogy': 'SQL is like a library catalog with strict rules. NoSQL is like a warehouse where you organize things however you want.',
                'hook': 'Your choice of database can determine if your app scales to millions of users!',
                'examples': ['SQL: PostgreSQL, MySQL', 'NoSQL: MongoDB, Cassandra'],
                'quality_score': 8.0,
                'engagement_score': 7.5
            },
            {
                'degree': 'Computer Science',
                'topic': 'API Design',
                'question': 'What makes a good REST API?',
                'answer': 'A good REST API uses HTTP methods correctly (GET for retrieval, POST for creation, PUT for updates, DELETE for deletion). It has clear, intuitive endpoints, uses proper status codes, includes versioning, provides documentation, and ensures security. URLs should represent resources, not actions.',
                'analogy': 'A REST API is like a restaurant menu - clear items (resources), simple ordering (methods), and predictable outcomes.',
                'hook': 'A well-designed API can make integration 10x easier for developers!',
                'examples': ['GET /users/123', 'POST /users', 'PUT /users/123'],
                'quality_score': 8.5,
                'engagement_score': 8.0
            },
            
            # Electrical Engineering
            {
                'degree': 'Electrical Engineering',
                'topic': 'Ohm\'s Law',
                'question': 'What is Ohm\'s Law and how do you apply it?',
                'answer': 'Ohm\'s Law states that voltage equals current multiplied by resistance: V = I × R. It shows the relationship between voltage (V), current (I), and resistance (R). In a circuit, if you increase voltage, current increases proportionally. If you increase resistance, current decreases.',
                'analogy': 'Think of voltage as water pressure, current as flow rate, and resistance as pipe diameter.',
                'hook': 'Ohm\'s Law is the foundation of understanding how electricity works!',
                'examples': ['5V = 1A × 5Ω', '10V = 2A × 5Ω', 'Double voltage = double current'],
                'quality_score': 9.0,
                'engagement_score': 8.5
            },
            {
                'degree': 'Electrical Engineering',
                'topic': 'Circuit Analysis',
                'question': 'What are series and parallel circuits?',
                'answer': 'In series circuits, components are connected one after another - same current flows through all. The total resistance is the sum of individual resistances. In parallel circuits, components are connected between the same two points - same voltage across all. Total resistance is less than the smallest individual resistance. Series circuits have all-or-nothing operation; parallel circuits are more reliable.',
                'analogy': 'Series is like a string of lights - if one breaks, all go dark. Parallel is like multiple routes - if one is blocked, you can take another.',
                'hook': 'Choosing series vs parallel can determine your circuit\'s reliability!',
                'examples': ['Series: R_total = R1 + R2 + R3', 'Parallel: 1/R_total = 1/R1 + 1/R2 + 1/R3'],
                'quality_score': 8.5,
                'engagement_score': 8.0
            },
            {
                'degree': 'Electrical Engineering',
                'topic': 'Power Systems',
                'question': 'What is power factor and why does it matter?',
                'answer': 'Power factor is the ratio of real power (watts) to apparent power (volt-amperes). It measures how efficiently electrical power is used. A power factor of 1.0 is ideal (purely resistive). Lower power factors indicate reactive power loss. In AC circuits, inductive loads reduce power factor, requiring capacitors for correction.',
                'analogy': 'Power factor is like efficiency - 100% means all energy is useful, less means some energy is wasted as heat.',
                'hook': 'Poor power factor can cost industries hundreds of thousands in wasted electricity!',
                'examples': ['Resistive load: PF = 1.0', 'Inductive load: PF = 0.8', 'With capacitor correction: PF = 0.95'],
                'quality_score': 8.0,
                'engagement_score': 7.5
            },
            {
                'degree': 'Electrical Engineering',
                'topic': 'Transformers',
                'question': 'How do transformers work and what\'s the relationship between primary and secondary voltage?',
                'answer': 'Transformers use electromagnetic induction to convert voltage and current. The turns ratio determines the voltage ratio: V_secondary/V_primary = N_secondary/N_primary. Step-up transformers increase voltage and decrease current. Step-down transformers decrease voltage and increase current. Power is conserved: V1×I1 ≈ V2×I2.',
                'analogy': 'A transformer is like a gear system - more teeth mean higher voltage but lower current.',
                'hook': 'Transformers made long-distance power transmission possible!',
                'examples': ['2:1 turns ratio = 2x voltage increase and 0.5x current', 'Step-down: 120V to 12V'],
                'quality_score': 8.5,
                'engagement_score': 8.0
            },
            {
                'degree': 'Electrical Engineering',
                'topic': 'Semiconductors',
                'question': 'What is the difference between conductors, semiconductors, and insulators?',
                'answer': 'Conductors have low resistance and allow current to flow easily (copper, aluminum). Insulators have high resistance and block current flow (rubber, plastic). Semiconductors have intermediate resistance that can be controlled (silicon, germanium). Semiconductors form the basis of diodes and transistors by doping with impurities.',
                'analogy': 'Conductors are like highways for electrons. Insulators are walls. Semiconductors are adjustable gates.',
                'hook': 'All modern electronics depend on semiconductor properties!',
                'examples': ['Conductors: Copper, Silver', 'Semiconductors: Silicon, Germanium', 'Insulators: Rubber, Glass'],
                'quality_score': 8.5,
                'engagement_score': 8.0
            },
            
            # Mechanical Engineering
            {
                'degree': 'Mechanical Engineering',
                'topic': 'Newton\'s Laws',
                'question': 'What are Newton\'s three laws of motion?',
                'answer': 'First Law: Objects at rest stay at rest unless acted upon by force. Second Law: F = ma (force equals mass times acceleration). Third Law: Every action has an equal and opposite reaction. These laws form the foundation of classical mechanics and explain how objects move and interact.',
                'analogy': 'First law is like inertia. Second law explains why heavier cars need more force to accelerate. Third law is why rockets move forward.',
                'hook': 'Understanding Newton\'s laws explains everything from car crashes to rocket launches!',
                'examples': ['Seatbelts prevent you from moving (First Law)', 'F=ma determines acceleration', 'Recoil from firing a gun'],
                'quality_score': 9.0,
                'engagement_score': 8.5
            },
            {
                'degree': 'Mechanical Engineering',
                'topic': 'Thermodynamics',
                'question': 'What are the first and second laws of thermodynamics?',
                'answer': 'The first law states that energy cannot be created or destroyed, only converted from one form to another (conservation of energy). The second law states that entropy of an isolated system always increases (disorder increases). These laws govern all energy conversions and explain why perpetual motion machines are impossible.',
                'analogy': 'First law: Money can\'t be created or destroyed, only moved. Second law: Things naturally get messier over time.',
                'hook': 'These laws explain why perpetual motion machines will never work!',
                'examples': ['Heat engine efficiency is limited by second law', 'Refrigerator requires work input to transfer heat'],
                'quality_score': 8.5,
                'engagement_score': 8.0
            },
            {
                'degree': 'Mechanical Engineering',
                'topic': 'Stress and Strain',
                'question': 'What is the difference between stress and strain?',
                'answer': 'Stress is the internal force per unit area (F/A) - measured in Pascals. It\'s what you apply to a material. Strain is the deformation resulting from stress (ΔL/L) - it\'s dimensionless. Stress causes strain. Young\'s modulus relates them: Stress = E × Strain. Understanding both is crucial for material selection.',
                'analogy': 'Stress is like pushing on a rubber band. Strain is how much it stretches.',
                'hook': 'Engineers use stress-strain curves to design structures that won\'t fail!',
                'examples': ['Tensile stress pulls material apart', 'Compressive stress squeezes material', 'Shear stress causes sliding'],
                'quality_score': 8.5,
                'engagement_score': 8.0
            },
            {
                'degree': 'Mechanical Engineering',
                'topic': 'Fluid Mechanics',
                'question': 'What is Bernoulli\'s principle and how does it apply to real-world scenarios?',
                'answer': 'Bernoulli\'s principle states that as fluid speed increases, pressure decreases (along a streamline with constant energy). Mathematically: P + ½ρv² + ρgh = constant. This explains how airplanes generate lift, how water flowing through a narrower pipe moves faster, and how perfume atomizers work.',
                'analogy': 'Bernoulli\'s principle is like a magic trick - faster flow creates lower pressure.',
                'hook': 'Bernoulli\'s principle is why airplanes can fly!',
                'examples': ['Airplane wings: fast air on top = lower pressure = lift', 'Water atomizer: fast air creates low pressure'],
                'quality_score': 8.5,
                'engagement_score': 8.0
            },
            {
                'degree': 'Mechanical Engineering',
                'topic': 'Machine Design',
                'question': 'What factors should you consider when selecting bearings for a mechanical system?',
                'answer': 'Key factors include: load capacity (axial and radial), speed rating, lubrication requirements, operating temperature, space constraints, and cost. Ball bearings handle mixed loads well. Roller bearings handle higher radial loads. Needle bearings save space. Thrust bearings handle axial loads. Proper selection ensures reliability and longevity.',
                'analogy': 'Selecting bearings is like choosing shoes - different types for different activities.',
                'hook': 'Bearing failure is one of the most common mechanical failures!',
                'examples': ['High-speed spindle: angular contact bearing', 'Heavy load: cylindrical roller bearing', 'Radial space-constrained: needle bearing'],
                'quality_score': 8.0,
                'engagement_score': 7.5
            }
        ]
    
    def get_random_qa(self, degree: str) -> Optional[Dict[str, Any]]:
        """Get a random Q&A pair for a degree"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                result = conn.execute("""
                    SELECT * FROM backup_qa 
                    WHERE degree = ?
                    ORDER BY RANDOM()
                    LIMIT 1
                """, (degree,)).fetchone()
                
                if result:
                    # Update serve count and last served time
                    conn.execute("""
                        UPDATE backup_qa 
                        SET serve_count = serve_count + 1, last_served = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (result['id'],))
                    conn.commit()
                    
                    # Convert to dictionary
                    qa = dict(result)
                    qa['examples'] = json.loads(qa['examples'] or '[]')
                    
                    return qa
        except Exception as e:
            logger.error(f"❌ Error retrieving random Q&A: {e}")
        
        return None
    
    def get_by_topic(self, degree: str, topic: str) -> Optional[Dict[str, Any]]:
        """Get a specific Q&A pair by topic"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                result = conn.execute("""
                    SELECT * FROM backup_qa 
                    WHERE degree = ? AND topic = ?
                """, (degree, topic)).fetchone()
                
                if result:
                    qa = dict(result)
                    qa['examples'] = json.loads(qa['examples'] or '[]')
                    return qa
        except Exception as e:
            logger.error(f"❌ Error retrieving Q&A by topic: {e}")
        
        return None
    
    def get_all_topics(self, degree: str) -> List[str]:
        """Get all available topics for a degree"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                topics = conn.execute("""
                    SELECT DISTINCT topic FROM backup_qa 
                    WHERE degree = ?
                    ORDER BY topic
                """, (degree,)).fetchall()
                
                return [t[0] for t in topics]
        except Exception as e:
            logger.error(f"❌ Error retrieving topics: {e}")
        
        return []
    
    def add_custom_qa(self, degree: str, topic: str, question: str, answer: str,
                     analogy: str = '', hook: str = '', examples: List[str] = None,
                     quality_score: float = 8.0, engagement_score: float = 7.5) -> bool:
        """Add a custom Q&A pair to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO backup_qa 
                    (degree, topic, question, answer, analogy, hook, examples, quality_score, engagement_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    degree,
                    topic,
                    question,
                    answer,
                    analogy,
                    hook,
                    json.dumps(examples or []),
                    quality_score,
                    engagement_score
                ))
                conn.commit()
                logger.info(f"✅ Added custom Q&A for {degree}/{topic}")
                return True
        except Exception as e:
            logger.error(f"❌ Error adding custom Q&A: {e}")
            return False
    
    def get_stats(self, degree: str) -> Dict[str, Any]:
        """Get statistics for a degree"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = conn.execute("""
                    SELECT 
                        COUNT(*) as total_questions,
                        COUNT(DISTINCT topic) as unique_topics,
                        SUM(serve_count) as total_serves,
                        AVG(quality_score) as avg_quality
                    FROM backup_qa 
                    WHERE degree = ?
                """, (degree,)).fetchone()
                
                if stats:
                    return {
                        'total_questions': stats[0],
                        'unique_topics': stats[1],
                        'total_serves': stats[2] or 0,
                        'avg_quality': round(stats[3] or 0, 2)
                    }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
        
        return {'total_questions': 0, 'unique_topics': 0, 'total_serves': 0, 'avg_quality': 0}
