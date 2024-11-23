import json
import logging
from pydriller import Repository
from collections import Counter
from itertools import combinations

# Configure logging to output INFO level messages
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO to see INFO messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

""" 
    Analyze logical coupling in a Git repository and return top file pairs.
    Returns: list of Top file pairs committed together with their frequencies.
"""
def analyzeLogicalCoupling(repo_path, top_n=3):  

    filePairs = Counter()

    # Traverse repository commits
    for commit_counter, commit in enumerate(Repository(repo_path).traverse_commits(), start=1):
        logging.info(f"Date: {commit.committer_date} | {commit.hash} by {commit.author.name}")
        javaScriptFiles = [mod.new_path for mod in commit.modified_files if mod.new_path and mod.new_path.endswith('.js')]

        if len(javaScriptFiles) > 1:
            sortedJsFiles = sorted(javaScriptFiles)
            allPossibleCombination = combinations(sortedJsFiles,2)
            filePairs.update(allPossibleCombination)

    # Get top file pairs
    return filePairs

""" Generate logical coupling data in the required JSON format. """
def generateLogicalCouplingReport(filePairs):
    results = [
        {
            "file_pair": list(pair),
            "commits": count
        }
        for pair, count in filePairs.items()
    ]
    return results

""" Extract the top N logical couplings. """
def extractTopCouplings(filePairs, top_n=3):
    topCouplings = filePairs.most_common(top_n)
    return [{"file_pair": list(pair), "commits": count} for pair, count in topCouplings]

""" Save data to a JSON file. """
def saveToJson(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    repo_path = "./react"  # Path to the repository
    raw_output_file = "Task2.2 - Logical Coupling - Raw.json"
    top_output_file = "Task2.2 - Logical Coupling - Top3.json"

    print("Analyzing logical coupling...")
    filePairs = analyzeLogicalCoupling(repo_path)

    # Save all results before filtering
    raw_results = generateLogicalCouplingReport(filePairs)
    saveToJson(raw_results, raw_output_file)
    print(f"Full results saved to {raw_output_file}")

    # Save top 3 results
    top_results = extractTopCouplings(filePairs, top_n=3)
    saveToJson(top_results, top_output_file)
    print(f"Top 3 results saved to {top_output_file}")

if __name__ == "__main__":
    main()
