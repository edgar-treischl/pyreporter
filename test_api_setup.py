#!/usr/bin/env python
"""
Simple test script to verify FastAPI setup.
"""

import sys


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✓ Pydantic imported successfully")
    except ImportError as e:
        print(f"✗ Pydantic import failed: {e}")
        return False
    
    try:
        from pyreporter.api import app
        print("✓ API module imported successfully")
    except ImportError as e:
        print(f"✗ API module import failed: {e}")
        return False
    
    return True


def test_api_structure():
    """Test that API has expected endpoints."""
    print("\nTesting API structure...")
    
    try:
        from pyreporter.api import app
        
        routes = [route.path for route in app.routes]
        
        expected = [
            "/",
            "/health",
            "/api/v1/raw-data",
            "/api/v1/prepared-data",
            "/api/v1/plot",
            "/api/v1/report",
            "/api/v1/plots/list"
        ]
        
        for endpoint in expected:
            if endpoint in routes:
                print(f"✓ Endpoint {endpoint} exists")
            else:
                print(f"✗ Endpoint {endpoint} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ API structure test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("PyReporter API Setup Test")
    print("="*60)
    
    tests = [
        ("Import Test", test_imports),
        ("API Structure Test", test_api_structure)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print("="*60)
        result = test_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("Test Results")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
        if not result:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✅ All tests passed! API is ready to use.")
        print("\nStart the server with:")
        print("  make api-dev")
        print("\nThen visit:")
        print("  http://localhost:8000/docs")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
