#!/usr/bin/env python
"""Test all API endpoints with Makefile default values."""

import requests
import json
import sys

API_BASE = "http://localhost:8000"

# Makefile defaults
DEFAULTS = {
    "snr": "0001",
    "stype": "gy",
    "audience": "leh",  # Note: Makefile default is 'leh', not 'sus'
    "ubb": False,
    "ganztag": False,
    "has_N": ["sus", "leh"],
    "year": "2025"
}

def test_health():
    """Test 1: Health check."""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    try:
        response = requests.get(f"{API_BASE}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Response: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_list_plots():
    """Test 2: List available plots."""
    print("\n" + "="*70)
    print("TEST 2: List Available Plots")
    print("="*70)
    try:
        params = {
            "snr": DEFAULTS["snr"],
            "stype": DEFAULTS["stype"],
            "audience": DEFAULTS["audience"],
            "ubb": DEFAULTS["ubb"],
            "ganztag": DEFAULTS["ganztag"]
        }
        print(f"Request: GET /api/v1/plots/list")
        print(f"Params: {json.dumps(params, indent=2)}")
        
        response = requests.get(f"{API_BASE}/api/v1/plots/list", params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Report: {data['report']}")
        print(f"✓ Plots count: {data['count']}")
        print(f"✓ First 5 plots: {data['plots'][:5]}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def test_raw_data():
    """Test 3: Fetch raw data."""
    print("\n" + "="*70)
    print("TEST 3: Fetch Raw Data")
    print("="*70)
    try:
        payload = {
            "snr": DEFAULTS["snr"],
            "stype": DEFAULTS["stype"],
            "audience": DEFAULTS["audience"],
            "ubb": DEFAULTS["ubb"],
            "ganztag": DEFAULTS["ganztag"],
            "has_N": DEFAULTS["has_N"],
            "use_cache": True
        }
        print(f"Request: POST /api/v1/raw-data")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{API_BASE}/api/v1/raw-data", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Message: {data['message']}")
        print(f"✓ Rows: {data['rows']}")
        print(f"✓ Year: {data['syear']}")
        print(f"✓ Sample size: {data['result_n']}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def test_prepared_data():
    """Test 4: Prepare data."""
    print("\n" + "="*70)
    print("TEST 4: Prepare Data")
    print("="*70)
    try:
        payload = {
            "snr": DEFAULTS["snr"],
            "stype": DEFAULTS["stype"],
            "audience": DEFAULTS["audience"],
            "ubb": DEFAULTS["ubb"],
            "ganztag": DEFAULTS["ganztag"],
            "has_N": DEFAULTS["has_N"],
            "use_cache": True
        }
        print(f"Request: POST /api/v1/prepared-data")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{API_BASE}/api/v1/prepared-data", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Message: {data['message']}")
        print(f"✓ School: {data['sname']}")
        print(f"✓ Year: {data['syear']}")
        print(f"✓ Report: {data['report_name']}")
        print(f"✓ Plots count: {data['plots_count']}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def test_plot():
    """Test 5: Generate a single plot."""
    print("\n" + "="*70)
    print("TEST 5: Generate Single Plot")
    print("="*70)
    try:
        # First get available plots
        params = {
            "snr": DEFAULTS["snr"],
            "stype": DEFAULTS["stype"],
            "audience": DEFAULTS["audience"],
            "ubb": DEFAULTS["ubb"],
            "ganztag": DEFAULTS["ganztag"]
        }
        list_response = requests.get(f"{API_BASE}/api/v1/plots/list", params=params)
        list_response.raise_for_status()
        available_plots = list_response.json()['plots']
        
        if not available_plots:
            print("✗ No plots available to test")
            return False
        
        plot_name = available_plots[0]
        
        payload = {
            "snr": DEFAULTS["snr"],
            "stype": DEFAULTS["stype"],
            "audience": DEFAULTS["audience"],
            "plot_name": plot_name,
            "ubb": DEFAULTS["ubb"],
            "ganztag": DEFAULTS["ganztag"],
            "has_N": DEFAULTS["has_N"],
            "use_cache": True
        }
        print(f"Request: POST /api/v1/plot")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{API_BASE}/api/v1/plot", json=payload)
        response.raise_for_status()
        
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Content-Type: {response.headers.get('content-type')}")
        print(f"✓ PDF size: {len(response.content)} bytes")
        
        # Save to file
        output_file = f"test_plot_{plot_name}.pdf"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✓ Saved to: {output_file}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response text: {e.response.text[:500]}")
        return False

def test_report():
    """Test 6: Generate complete report."""
    print("\n" + "="*70)
    print("TEST 6: Generate Complete Report")
    print("="*70)
    try:
        payload = {
            "snr": DEFAULTS["snr"],
            "stype": DEFAULTS["stype"],
            "audience": DEFAULTS["audience"],
            "ubb": DEFAULTS["ubb"],
            "ganztag": DEFAULTS["ganztag"],
            "has_N": DEFAULTS["has_N"],
            "year": DEFAULTS["year"],
            "duration": "2",
            "use_cache": True
        }
        print(f"Request: POST /api/v1/report")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("(This may take a minute...)")
        
        response = requests.post(f"{API_BASE}/api/v1/report", json=payload, timeout=300)
        response.raise_for_status()
        
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Content-Type: {response.headers.get('content-type')}")
        print(f"✓ PDF size: {len(response.content)} bytes")
        
        # Save to file
        output_file = f"test_report_{DEFAULTS['audience']}.pdf"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✓ Saved to: {output_file}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response text: {e.response.text[:1000]}")
        return False

def main():
    """Run all tests."""
    print("="*70)
    print("API ENDPOINT TESTS (Makefile Defaults)")
    print("="*70)
    print(f"Using defaults: {json.dumps(DEFAULTS, indent=2)}")
    
    tests = [
        ("Health Check", test_health),
        ("List Plots", test_list_plots),
        ("Fetch Raw Data", test_raw_data),
        ("Prepare Data", test_prepared_data),
        ("Generate Plot", test_plot),
        ("Generate Report", test_report),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
