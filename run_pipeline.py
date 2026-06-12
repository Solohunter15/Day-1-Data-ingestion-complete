"""
Bluestock Mutual Fund Analytics Platform - Master Execution Pipeline
Orchestrates the entire platform:
1. Fetches live NAV from mfapi.in API
2. Executes the ETL pipeline (CSV Cleaning and SQLite Database Loading)
3. Computes performance metrics, risk ratios (Sharpe, Sortino, VaR/CVaR), and portfolio HHI
4. Demonstrates recommendation results
"""

import os
import sys
import subprocess

# Determine directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_FOLDER = os.path.join(SCRIPT_DIR, "scripts")

def run_script(script_name: str, args: list = None) -> bool:
    """Runs a Python script as a subprocess and logs its output."""
    script_path = os.path.join(SCRIPTS_FOLDER, script_name)
    print("\n" + "#" * 80)
    print(f" EXECUTING PHASE: {script_name}")
    print("#" * 80)
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
        
    try:
        # Run subprocess and stream output
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print(f"\n[PHASE SUCCESS] Finished executing {script_name} cleanly.\n")
            return True
        else:
            print(f"\n[PHASE FAILURE] {script_name} failed with exit code: {result.returncode}\n")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n[PHASE ERROR] Exception occurred running {script_name}: {e}\n")
        return False

def main():
    print("=" * 80)
    print(" BLUESTOCK MUTUAL FUND ANALYTICS PLATFORM - MASTER PIPELINE RUNNER")
    print("=" * 80)
    
    # Phase 1: Live NAV Ingestion
    # Note: mfapi.in API might be slow or rate-limited. If it fails, the ETL pipeline continues with existing raw files.
    print("\n[Phase 1/4] Ingesting Live NAV from mfapi.in API...")
    run_script("live_nav_fetch.py")
    
    # Phase 2: ETL Pipeline (Cleaning + SQLite Loading)
    print("\n[Phase 2/4] Preprocessing raw data and loadingSQLite relational database...")
    if not run_script("etl_pipeline.py"):
        print("[CRITICAL ERROR] ETL Pipeline failed. Aborting master execution.")
        sys.exit(1)
        
    # Phase 3: Performance & Risk Calculations
    print("\n[Phase 3/4] Computing performance metrics and advanced risk values...")
    if not run_script("compute_metrics.py"):
        print("[CRITICAL ERROR] Performance calculations failed. Aborting master execution.")
        sys.exit(1)
        
    # Phase 4: Recommender System (Demonstration Run)
    print("\n[Phase 4/4] Verifying the Recommender CLI Tool (Test: Moderate Risk)...")
    run_script("recommender.py", ["moderate"])
    
    print("=" * 80)
    print(" MASTER EXECUTION PIPELINE FINISHED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
