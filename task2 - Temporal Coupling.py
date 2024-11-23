import json
import logging
from datetime import timedelta
from collections import defaultdict
import pydriller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

""" Extract commits with `.js` files from the repository and sort them by timestamp. """
def extractAndSortCommits(repo_path):
    
    logging.info("Starting repository mining...")
    commits = []

    for commit in pydriller.Repository(repo_path).traverse_commits():
        jsFiles = {mf.new_path for mf in commit.modified_files if mf.new_path and mf.new_path.endswith('.js')}
        if jsFiles:  # Only add commits with .js files
            commitRecord = { "timestamp": commit.committer_date, "files": jsFiles }
            commits.append(commitRecord)

    commits.sort(key=lambda x: x["timestamp"])
    logging.info(f"Total commits with `.js` files: {len(commits)}")
    return commits

""" Analyze temporal coupling for a subset of commits. """
def analyzeTemporalCoupling(commits, time_windows):
    coupling_counts = {timeWindow: defaultdict(int) for timeWindow in time_windows}

    for index, current_commit in enumerate(commits):
        for timeWindow in time_windows:
            time_limit = current_commit["timestamp"] + timedelta(hours=timeWindow)
            current_files = current_commit["files"]

            for next_commit in commits[index + 1:]:
                if next_commit["timestamp"] > time_limit:
                    break

                for file1 in current_files:
                    for file2 in next_commit["files"]:
                        if file1 != file2:
                            file_pair = tuple(sorted([file1, file2]))
                            coupling_counts[timeWindow][file_pair] += 1
    return coupling_counts

""" Extract the top N file pairs with the highest degree of temporal coupling for each time window """
def extractTopCouplings(coupling_counts, topN=3):
    results = {}
    for timeWindow, counts in coupling_counts.items():
        sortedCounts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:topN]
        results[timeWindow] = [{"files": list(pair), "count": count} for pair, count in sortedCounts]
    return results

def generateCouplingReport(coupling_counts):
    results = []
    for timeWindow, counts in coupling_counts.items():
        for file_pair, commit_count in counts.items():
            # Add data in the required format
            results.append({
                "file_pair": list(file_pair),
                "coupled_commits": {
                    "time_window": timeWindow,
                    "commit_count": commit_count
                }
            })
    return results

""" Save data to a JSON file. """
def saveToJson(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    repo_path = "./react"  # Path to the repository
    raw_output_file = "Task2.1 - Temporal Coupling - Raw.json"
    top_output_file = "Task2.1 - Temporal Coupling - Top3.json"
    time_windows = [24, 48, 72]

    # Temporal Coupling Analysis
    logging.info("Starting temporal coupling analysis...")
    commits = extractAndSortCommits(repo_path)
    coupling_counts = analyzeTemporalCoupling(commits, time_windows)

    # Save all results before limiting
    full_results = generateCouplingReport(coupling_counts)
    saveToJson(full_results, raw_output_file)
    logging.info(f"Full temporal coupling results saved to {raw_output_file}.")

    # Limit to top 3 and save separately
    temporal_results = extractTopCouplings(coupling_counts, topN=3)
    saveToJson(temporal_results, top_output_file)
    logging.info(f"Top 3 temporal coupling results saved to {top_output_file}.")

    logging.info("Analysis complete.")

if __name__ == "__main__":
    main()
