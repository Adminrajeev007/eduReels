#!/usr/bin/env python3
"""
QUICK START: Week 2 Testing Checklist
Run this to validate Week 2 is working correctly
"""

import os
import sys
from pathlib import Path

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def check_file_exists(path: str, description: str = ""):
    """Check if a file exists"""
    exists = os.path.exists(path)
    status = f"{GREEN}✅{RESET}" if exists else f"{RED}❌{RESET}"
    desc = f" - {description}" if description else ""
    print(f"{status} {path}{desc}")
    return exists

def check_directory_exists(path: str, description: str = ""):
    """Check if a directory exists"""
    exists = os.path.isdir(path)
    status = f"{GREEN}✅{RESET}" if exists else f"{RED}❌{RESET}"
    desc = f" - {description}" if description else ""
    print(f"{status} {path}{desc}")
    return exists

def main():
    """Run Week 2 checklist"""
    
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}📋 WEEK 2 IMPLEMENTATION CHECKLIST{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

    project_root = "/Users/rahulkumar/Desktop/edureels"
    os.chdir(project_root)

    all_good = True

    # ====================================================================
    # CHECK DIRECTORIES
    # ====================================================================
    print(f"{BOLD}📁 Directory Structure:{RESET}\n")
    
    directories = [
        ("agents", "Agent implementations"),
        ("tools", "Model connector & cache"),
        ("tests", "Test suite"),
        ("data", "Cache database"),
    ]
    
    for dir_name, desc in directories:
        if not check_directory_exists(f"{project_root}/{dir_name}", desc):
            all_good = False

    # ====================================================================
    # CHECK AGENT FILES
    # ====================================================================
    print(f"\n{BOLD}🤖 Agent Files:{RESET}\n")
    
    agent_files = [
        ("agents/research_agent.py", "Research Agent (finds topics)"),
        ("agents/question_generator.py", "Question Generator (creates questions)"),
        ("agents/quality_checker.py", "Quality Checker (validates questions)"),
        ("agents/orchestrator.py", "Orchestrator (coordinates all agents)"),
    ]
    
    for file_path, desc in agent_files:
        if not check_file_exists(f"{project_root}/{file_path}", desc):
            all_good = False

    # ====================================================================
    # CHECK TEST FILES
    # ====================================================================
    print(f"\n{BOLD}🧪 Test Files:{RESET}\n")
    
    test_files = [
        ("tests/test_agents.py", "Full pytest suite"),
        ("tests/run_tests.py", "Standalone test runner"),
        ("tests/test_mock_agents.py", "Mock tests (no API keys)"),
        ("tests/test_connectivity.py", "Connectivity validator"),
        ("tests/TESTING.md", "Testing documentation"),
    ]
    
    for file_path, desc in test_files:
        if not check_file_exists(f"{project_root}/{file_path}", desc):
            all_good = False

    # ====================================================================
    # CHECK INFRASTRUCTURE FILES
    # ====================================================================
    print(f"\n{BOLD}⚙️  Infrastructure Files:{RESET}\n")
    
    infra_files = [
        ("tools/model_connector.py", "Model connector (ChatGPT + HF)"),
        ("tools/cache_manager.py", "Cache manager (SQLite)"),
        ("tools/prompt_templates.py", "Prompt templates (7 agents)"),
        ("requirements.txt", "Python dependencies"),
        (".env.example", "Environment template"),
        (".gitignore", "Git ignore rules"),
        ("README.md", "Project overview"),
    ]
    
    for file_path, desc in infra_files:
        if not check_file_exists(f"{project_root}/{file_path}", desc):
            all_good = False

    # ====================================================================
    # CHECK DOCUMENTATION
    # ====================================================================
    print(f"\n{BOLD}📚 Documentation Files:{RESET}\n")
    
    doc_files = [
        ("WEEK_2_SUMMARY.md", "Week 2 completion report"),
    ]
    
    for file_path, desc in doc_files:
        if not check_file_exists(f"{project_root}/{file_path}", desc):
            all_good = False

    # ====================================================================
    # FINAL SUMMARY
    # ====================================================================
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}📊 VALIDATION SUMMARY{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

    if all_good:
        print(f"{GREEN}{BOLD}✅ ALL FILES PRESENT - Week 2 is ready!{RESET}\n")
        
        print(f"{BOLD}🚀 Next Steps:{RESET}\n")
        print("1. Run mock tests (no API keys needed):")
        print(f"   {YELLOW}python tests/test_mock_agents.py{RESET}\n")
        
        print("2. For full integration tests:")
        print(f"   {YELLOW}cp .env.example .env{RESET}")
        print("   # Edit .env and add your API keys")
        print(f"   {YELLOW}pip install -r requirements.txt{RESET}")
        print(f"   {YELLOW}python tests/run_tests.py{RESET}\n")
        
        print("3. Review documentation:")
        print(f"   {YELLOW}cat WEEK_2_SUMMARY.md{RESET}")
        print(f"   {YELLOW}cat tests/TESTING.md{RESET}\n")
        
        return 0
    else:
        print(f"{RED}{BOLD}❌ Some files are missing - check above{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
