#!/usr/bin/env python3
"""
Quick structure validation - no heavy dependencies needed
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that core modules can be imported"""
    print("Testing imports...")
    
    try:
        from utils import config, watchlist
        print("  ✓ utils package")
        
        # Test config
        params = config.load_default_params()
        print(f"  ✓ config loads ({len(params)} params)")
        
        # Test watchlist
        coins = watchlist.get_all()
        print(f"  ✓ watchlist loads ({len(coins)} coins: {coins})")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_structure():
    """Test that expected directories exist"""
    print("\nTesting structure...")
    
    expected_dirs = [
        "agents", "dataflows", "graph", "llm_clients",
        "state", "data", "logs", "reports", "scripts",
        "config", "docs", "utils", "watchlist"
    ]
    
    all_exist = True
    for dir_name in expected_dirs:
        dir_path = project_root / dir_name
        exists = dir_path.exists()
        symbol = "✓" if exists else "✗"
        print(f"  {symbol} {dir_name}/")
        if not exists:
            all_exist = False
    
    return all_exist


def test_config_files():
    """Test that config files exist and are valid"""
    print("\nTesting config files...")
    
    config_files = [
        "config/default_params.yaml",
        "config/thresholds.yaml",
        "config/coin_params/BTC.yaml.example"
    ]
    
    all_valid = True
    for config_file in config_files:
        config_path = project_root / config_file
        exists = config_path.exists()
        symbol = "✓" if exists else "✗"
        print(f"  {symbol} {config_file}")
        if not exists:
            all_valid = False
    
    return all_valid


def main():
    print("=" * 80)
    print("Trading Agents - Structure Validation")
    print("=" * 80)
    print()
    
    results = []
    
    results.append(("Structure", test_structure()))
    results.append(("Config Files", test_config_files()))
    results.append(("Imports", test_imports()))
    
    print()
    print("=" * 80)
    print("Results:")
    print("=" * 80)
    
    all_passed = True
    for name, passed in results:
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✓ ALL VALIDATIONS PASSED")
        print()
        print("Phase 1.1 (Project Setup) - COMPLETE")
        print("Phase 1.2 (Data Fetchers) - Code written, needs testing with dependencies")
        print()
        print("Next steps:")
        print("  1. Run: bash scripts/setup.sh")
        print("  2. Copy .env.example to .env")
        print("  3. Test data fetchers: python scripts/test_data_fetchers.py")
        return 0
    else:
        print("✗ SOME VALIDATIONS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
