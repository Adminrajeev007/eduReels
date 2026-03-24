#!/usr/bin/env python3
"""
Test script to verify that the API generates unique questions each time
Run this script to test 10 consecutive generations and verify no duplicates
"""

import requests
import json
from collections import defaultdict

API_URL = "http://localhost:8000/generate"

def test_unique_questions(count=10, degree="Computer Science"):
    """
    Generate multiple questions and check for duplicates
    """
    print(f"🔬 Testing unique question generation ({count} requests)...")
    print(f"📚 Degree: {degree}\n")
    
    questions = []
    topics = []
    
    for i in range(1, count + 1):
        try:
            response = requests.post(
                API_URL,
                json={
                    "degree": degree,
                    "skip_cache": True  # Force fresh generation
                },
                headers={
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                question = data.get("reel_question", "")
                topic = data.get("topic", "")
                
                questions.append(question)
                topics.append(topic)
                
                print(f"✅ Request {i}/{count}")
                print(f"   Topic: {topic}")
                print(f"   Question: {question[:80]}...")
                print()
            else:
                print(f"❌ Request {i} failed with status {response.status_code}")
                print(f"   Response: {response.text}\n")
        except Exception as e:
            print(f"❌ Request {i} error: {str(e)}\n")
    
    # Check for duplicates
    print("\n" + "="*80)
    print("📊 UNIQUENESS ANALYSIS")
    print("="*80 + "\n")
    
    unique_questions = len(set(questions))
    total_questions = len(questions)
    
    print(f"Total questions generated: {total_questions}")
    print(f"Unique questions: {unique_questions}")
    print(f"Duplicates: {total_questions - unique_questions}")
    print(f"Uniqueness rate: {(unique_questions/total_questions)*100:.1f}%\n")
    
    unique_topics = len(set(topics))
    print(f"Unique topics: {unique_topics}")
    print(f"Topics: {', '.join(set(topics))}\n")
    
    # Check for repeating pairs
    print("Checking for consecutive duplicates...")
    has_consecutive_duplicates = False
    for i in range(len(questions) - 1):
        if questions[i] == questions[i + 1]:
            print(f"⚠️ DUPLICATE FOUND: Requests {i+1} and {i+2} generated the same question!")
            has_consecutive_duplicates = True
    
    if not has_consecutive_duplicates:
        print("✅ No consecutive duplicates found!\n")
    
    # Summary
    print("="*80)
    if unique_questions == total_questions:
        print("🎉 SUCCESS! All questions are unique!")
    else:
        print("⚠️ WARNING! Some questions were repeated.")
    print("="*80)

if __name__ == "__main__":
    test_unique_questions(10, "Computer Science")
