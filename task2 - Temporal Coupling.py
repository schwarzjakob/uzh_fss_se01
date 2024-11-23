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
def extract_and_sort_commits(repo_path):
    
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
def analyze_window(start_index, commits, time_windows):
    coupling_counts = {timeWindow: defaultdict(int) for timeWindow in time_windows}
    total_commits = len(commits)

    for idx, current_commit in enumerate(commits[start_index:], start=start_index):
        for timeWindow in time_windows:
            time_limit = current_commit["timestamp"] + timedelta(hours=timeWindow)
            current_files = current_commit["files"]

            for next_commit in commits[idx + 1:]:
                if next_commit["timestamp"] > time_limit:
                    break

                for file1 in current_files:
                    for file2 in next_commit["files"]:
                        if file1 != file2:
                            file_pair = tuple(sorted([file1, file2]))
                            coupling_counts[timeWindow][file_pair] += 1
    return coupling_counts

""" Process commit pairing sequentially. """
def process_commit_pairing(commits, time_windows):
    totalCounts = {timeWindow: defaultdict(int) for timeWindow in time_windows}

    for i in range(len(commits)):
        local_counts = analyze_window(i, commits, time_windows)
        for timeWindow in local_counts:
            for pair, count in local_counts[timeWindow].items():
                totalCounts[timeWindow][pair] += count
    return totalCounts

""" Extract the top N file pairs with the highest degree of temporal coupling for each time window """
def extract_top_couplings(coupling_counts, top_n=3):
    results = {}
    for timeWindow, counts in coupling_counts.items():
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        results[timeWindow] = [{"files": list(pair), "count": count} for pair, count in sorted_counts]
    return results

""" Save data to a JSON file. """
def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    repo_path = "./react"  # Path to the repository
    output_file = "Task2.1 - Temporal Coupling - JS Only.json"
    time_windows = [24, 48, 72]

    print("Analyzing temporal coupling...")
    commits = extract_and_sort_commits(repo_path)
    coupling_counts = process_commit_pairing(commits, time_windows)
    results = extract_top_couplings(coupling_counts)
    save_to_json(results, output_file)
    logging.info("Analysis complete.")

if __name__ == "__main__":
    main()
