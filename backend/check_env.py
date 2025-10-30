#!/usr/bin/env python
"""
Quick diagnostic script to check Python environment
"""
import sys
import os

print("=" * 60)
print("PYTHON ENVIRONMENT DIAGNOSTICS")
print("=" * 60)

print(f"\nPython executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

print(f"\nVirtual environment:")
venv = os.environ.get('VIRTUAL_ENV', 'Not activated')
print(f"  VIRTUAL_ENV: {venv}")

print(f"\nCurrent working directory: {os.getcwd()}")

print("\n" + "=" * 60)
print("CHECKING PACKAGE INSTALLATIONS")
print("=" * 60)

packages = ['fastapi', 'uvicorn', 'pydantic', 'pandas', 'numpy', 'yfinance', 'sklearn']

for package in packages:
    try:
        module = __import__(package)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package}: {version}")
    except ImportError as e:
        print(f"❌ {package}: NOT FOUND - {e}")

print("\n" + "=" * 60)
