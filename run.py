import subprocess
import sys

def main():
    print("=== Starting Hiver Challenge Pipeline ===")
    
    print("\n--- Step 1: Generating Replies ---")
    subprocess.run([sys.executable, "generator.py"], check=True)
    
    print("\n--- Step 2: Evaluating Replies ---")
    subprocess.run([sys.executable, "evaluator.py"], check=True)
    
    print("\n=== Pipeline Complete ===")
    print("Please check evaluation_report.json for the final results.")

if __name__ == "__main__":
    main()
