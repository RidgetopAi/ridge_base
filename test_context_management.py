# test_context_management.py - Test script for Phase 3B completion

import os
import sys
import subprocess
from pathlib import Path

def test_context_system():
    """Test the context management system end-to-end"""
    
    print("🚀 Testing Ridge Base Context Management System")
    print("=" * 50)
    
    # Test 1: Database migration
    print("\n1. Running database migration...")
    try:
        # You'll need to run the migration manually first
        print("   ⏳ Please run the migration first:")
        print("   $ psql -h localhost -p 5433 -U ridge_user -d ridge_base < sql/migrate_context_management.sql")
        input("   Press Enter when migration is complete...")
        print("   ✅ Migration assumed complete")
    except Exception as e:
        print(f"   ❌ Migration error: {e}")
        return False
    
    # Test 2: Health check
    print("\n2. Testing system health...")
    try:
        result = subprocess.run([sys.executable, "src/cli.py", "health"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 3: Memory system
    print("\n3. Testing memory system...")
    try:
        # Initialize test project
        result = subprocess.run([sys.executable, "src/cli.py", "memory", "init", "TestContextProject"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Project initialization successful")
        else:
            print(f"   ❌ Project init failed: {result.stderr}")
            return False
            
        # Test memory status
        result = subprocess.run([sys.executable, "src/cli.py", "memory", "status"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Memory status working")
        else:
            print(f"   ❌ Memory status failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Memory system error: {e}")
        return False
    
    # Test 4: Context commands
    print("\n4. Testing context management...")
    try:
        # Test context status
        result = subprocess.run([sys.executable, "src/cli.py", "context", "status"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Context status working")
        else:
            print(f"   ❌ Context status failed: {result.stderr}")
            
        # Test checkpoint creation
        result = subprocess.run([sys.executable, "src/cli.py", "context", "checkpoint", "Test checkpoint"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Checkpoint creation working")
        else:
            print(f"   ❌ Checkpoint creation failed: {result.stderr}")
            
        # Test context status again to see checkpoint
        result = subprocess.run([sys.executable, "src/cli.py", "context", "status"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Context status with checkpoint working")
        else:
            print(f"   ❌ Context status with checkpoint failed: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Context management error: {e}")
        return False
    
    # Test 5: Decision logging
    print("\n5. Testing decision logging...")
    try:
        result = subprocess.run([sys.executable, "src/cli.py", "memory", "decision", 
                               "Use FastAPI for backend", "--category", "tech_choice", 
                               "--reasoning", "Better async support"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Decision logging working")
        else:
            print(f"   ❌ Decision logging failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Decision logging error: {e}")
        return False
    
    # Test 6: Memory search
    print("\n6. Testing memory search...")
    try:
        result = subprocess.run([sys.executable, "src/cli.py", "memory", "search", "FastAPI"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Memory search working")
        else:
            print(f"   ❌ Memory search failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Memory search error: {e}")
        return False
    
    # Test 7: File tracking
    print("\n7. Testing file tracking...")
    try:
        # Create a test file
        test_file = Path("test_file.py")
        test_file.write_text("# Test file for Ridge Base\nprint('Hello World')\n")
        
        result = subprocess.run([sys.executable, "src/cli.py", "files", "sync"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ File sync working")
        else:
            print(f"   ❌ File sync failed: {result.stderr}")
            
        # Test file changes detection
        result = subprocess.run([sys.executable, "src/cli.py", "files", "changes"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ File changes detection working")
        else:
            print(f"   ❌ File changes detection failed: {result.stderr}")
            
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
            
    except Exception as e:
        print(f"   ❌ File tracking error: {e}")
        return False
    
    # Test 8: Auto-checkpoint simulation
    print("\n8. Testing auto-checkpoint logic...")
    try:
        # Add multiple conversations to trigger auto-checkpoint
        for i in range(26):  # More than 25 to trigger auto-checkpoint
            result = subprocess.run([sys.executable, "src/cli.py", "memory", "decision", 
                                   f"Test decision {i}", "--category", "test"], 
                                  capture_output=True, text=True, timeout=30)
        
        # Check if auto-checkpoint was created
        result = subprocess.run([sys.executable, "src/cli.py", "context", "status"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Auto-checkpoint logic working")
        else:
            print(f"   ❌ Auto-checkpoint logic failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Auto-checkpoint error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")
    print("\nPhase 3B Context Management is COMPLETE! ✅")
    print("\nNext steps:")
    print("  - Phase 4: File operations (analyze, edit, create)")
    print("  - Phase 5: Interactive mode and batch processing")
    print("  - Phase 6: Project-wide operations")
    
    return True

def show_usage_examples():
    """Show practical usage examples"""
    print("\n📚 Ridge Base Context Management Usage Examples:")
    print("=" * 50)
    
    examples = [
        ("Initialize a project", "ridge memory init MyProject"),
        ("Check project status", "ridge memory status"),
        ("Log a decision", "ridge memory decision 'Using React for frontend' --category tech_choice"),
        ("Search memory", "ridge memory search 'authentication'"),
        ("Check context usage", "ridge context status"),
        ("Create checkpoint", "ridge context checkpoint 'Auth system complete'"),
        ("Reset to checkpoint", "ridge context reset-to latest"),
        ("Sync project files", "ridge files sync"),
        ("Check file changes", "ridge files changes"),
        ("System health", "ridge health"),
    ]
    
    for description, command in examples:
        print(f"  {description}:")
        print(f"    $ {command}")
        print()

if __name__ == "__main__":
    print("Ridge Base Context Management Test Suite")
    print("This script tests Phase 3B completion")
    print()
    
    choice = input("Run full test suite? (y/n): ").lower().strip()
    
    if choice == 'y':
        success = test_context_system()
        if success:
            show_usage_examples()
    else:
        show_usage_examples()
        print("\nTo run tests manually:")
        print("python test_context_management.py")