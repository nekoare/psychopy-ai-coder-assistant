#!/usr/bin/env python3
"""
Test runner script for PsychoPy AI Coder Assistant
"""

import sys
import os
import unittest
import subprocess
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def run_tests():
    """Run all test suites."""
    print("Running PsychoPy AI Coder Assistant Tests")
    print("=" * 50)
    
    # Discover and run tests
    test_dir = project_root / 'tests'
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return 1

def run_linting():
    """Run code linting."""
    print("\nRunning code quality checks...")
    print("-" * 30)
    
    try:
        # Check if flake8 is available
        subprocess.run(['flake8', '--version'], capture_output=True, check=True)
        
        # Run flake8 on source code
        result = subprocess.run([
            'flake8', 
            str(project_root / 'src'),
            '--max-line-length=88',
            '--extend-ignore=E203,W503'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Code quality checks passed!")
        else:
            print("❌ Code quality issues found:")
            print(result.stdout)
            return 1
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  flake8 not available, skipping linting")
    
    return 0

def run_type_checking():
    """Run type checking."""
    print("\nRunning type checking...")
    print("-" * 25)
    
    try:
        # Check if mypy is available
        subprocess.run(['mypy', '--version'], capture_output=True, check=True)
        
        # Run mypy on source code
        result = subprocess.run([
            'mypy',
            str(project_root / 'src'),
            '--ignore-missing-imports'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Type checking passed!")
        else:
            print("❌ Type checking issues found:")
            print(result.stdout)
            return 1
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  mypy not available, skipping type checking")
    
    return 0

def main():
    """Main test runner."""
    exit_code = 0
    
    # Run tests
    exit_code |= run_tests()
    
    # Run code quality checks if available
    exit_code |= run_linting()
    exit_code |= run_type_checking()
    
    print("\n" + "=" * 50)
    if exit_code == 0:
        print("🎉 All checks passed! Ready for release.")
    else:
        print("❌ Some checks failed. Please fix issues before release.")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())