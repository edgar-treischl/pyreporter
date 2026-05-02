#!/usr/bin/env python
"""
Example client script demonstrating how to use the PyReporter API.

This script shows how to interact with all API endpoints programmatically.
"""

import requests
import json
from pathlib import Path


# API base URL
API_BASE = "http://localhost:8000"


def check_health():
    """Check if the API is running."""
    print("🔍 Checking API health...")
    try:
        response = requests.get(f"{API_BASE}/health")
        response.raise_for_status()
        print(f"✓ API is healthy: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ API is not reachable: {e}")
        print("Make sure to start the API with: make api-dev")
        return False


def list_available_plots():
    """List available plots for a configuration."""
    print("\n📋 Listing available plots...")
    
    params = {
        "snr": "0001",
        "stype": "gy",
        "audience": "sus",
        "ubb": False,
        "ganztag": False
    }
    
    response = requests.get(f"{API_BASE}/api/v1/plots/list", params=params)
    response.raise_for_status()
    
    data = response.json()
    print(f"✓ Found {data['count']} plots for report '{data['report']}'")
    print(f"  Plots: {', '.join(data['plots'][:5])}...")
    
    return data


def fetch_raw_data():
    """Fetch raw survey data."""
    print("\n📡 Fetching raw data...")
    
    payload = {
        "snr": "0001",
        "stype": "gy",
        "audience": "sus",
        "ubb": False,
        "ganztag": False,
        "has_N": ["sus", "leh"],
        "use_cache": True
    }
    
    response = requests.post(f"{API_BASE}/api/v1/raw-data", json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"✓ Fetched {data['rows']} rows for year {data['syear']}")
    print(f"  Sample size: {data['result_n']}")
    print(f"  Columns: {', '.join(data['columns'][:5])}...")
    
    return data


def prepare_data():
    """Prepare plot-ready data."""
    print("\n🔧 Preparing data...")
    
    payload = {
        "snr": "0001",
        "stype": "gy",
        "audience": "sus",
        "ubb": False,
        "ganztag": False,
        "has_N": ["sus", "leh"],
        "use_cache": True
    }
    
    response = requests.post(f"{API_BASE}/api/v1/prepared-data", json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"✓ Prepared data for '{data['sname']}'")
    print(f"  Report: {data['report_name']}")
    print(f"  Plots available: {data['plots_count']}")
    
    return data


def generate_plot(plot_name="A12"):
    """Generate a single plot."""
    print(f"\n📊 Generating plot '{plot_name}'...")
    
    payload = {
        "snr": "0001",
        "stype": "gy",
        "audience": "sus",
        "plot_name": plot_name,
        "ubb": False,
        "ganztag": False,
        "has_N": ["sus", "leh"],
        "use_cache": True
    }
    
    response = requests.post(f"{API_BASE}/api/v1/plot", json=payload)
    response.raise_for_status()
    
    # Save the PDF
    output_file = Path(f"example_plot_{plot_name}.pdf")
    with open(output_file, "wb") as f:
        f.write(response.content)
    
    print(f"✓ Plot saved to: {output_file}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")
    
    return output_file


def create_report():
    """Generate complete PDF report."""
    print("\n📄 Creating complete report...")
    
    payload = {
        "snr": "0001",
        "stype": "gy",
        "audience": "sus",
        "ubb": False,
        "ganztag": False,
        "has_N": ["sus", "leh"],
        "year": "2025",
        "duration": "2",
        "use_cache": True
    }
    
    print("  (This may take a minute or two...)")
    response = requests.post(f"{API_BASE}/api/v1/report", json=payload)
    response.raise_for_status()
    
    # Save the PDF
    output_file = Path("example_report.pdf")
    with open(output_file, "wb") as f:
        f.write(response.content)
    
    print(f"✓ Report saved to: {output_file}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")
    
    return output_file


def main():
    """Run all examples."""
    print("="*70)
    print("PyReporter API Client Examples")
    print("="*70)
    
    # Check if API is running
    if not check_health():
        return 1
    
    try:
        # Example 1: List available plots
        list_available_plots()
        
        # Example 2: Fetch raw data
        fetch_raw_data()
        
        # Example 3: Prepare data
        prepare_data()
        
        # Example 4: Generate a single plot
        # Uncomment to test plot generation:
        # generate_plot("A12")
        
        # Example 5: Create complete report
        # Uncomment to test report generation (requires LimeSurvey credentials):
        # create_report()
        
        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70)
        print("\nNotes:")
        print("  - Plot and report generation are commented out by default")
        print("  - Uncomment them in the script to test full pipeline")
        print("  - Make sure .env file is configured with LimeSurvey credentials")
        
        return 0
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
