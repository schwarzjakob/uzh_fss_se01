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

def extract_and_sort_commits(repo_path):
    """
    Extract commits from the repository and sort them by timestamp.
    Only include `.js` files.
    """
    logging.info("Starting repository mining...")
    commits = [
        {
            "timestamp": commit.committer_date,
            "files": {mf.new_path for mf in commit.modified_files if mf.new_path and mf.new_path.endswith('.js')}
        }
        for commit in pydriller.Repository(repo_path).traverse_commits()
    ]
    # Remove commits with no `.js` files
    commits = [commit for commit in commits if commit["files"]]
    commits.sort(key=lambda x: x["timestamp"])
    logging.info(f"Total commits with `.js` files: {len(commits)}")
    return commits

def analyze_window(start_index, commits, time_windows):
    """
    Analyze temporal coupling for a subset of commits.
    """
    coupling_counts = {tw: defaultdict(int) for tw in time_windows}
    total_commits = len(commits)

    for idx, current_commit in enumerate(commits[start_index:], start=start_index):
        for tw in time_windows:
            time_limit = current_commit["timestamp"] + timedelta(hours=tw)
            current_files = current_commit["files"]

            for next_commit in commits[idx + 1:]:
                if next_commit["timestamp"] > time_limit:
                    break

                for file1 in current_files:
                    for file2 in next_commit["files"]:
                        if file1 != file2:
                            file_pair = tuple(sorted([file1, file2]))
                            coupling_counts[tw][file_pair] += 1
    return coupling_counts

def process_commit_pairing(commits, time_windows):
    """
    Process commit pairing sequentially.
    """
    global_counts = {tw: defaultdict(int) for tw in time_windows}

    for i in range(len(commits)):
        local_counts = analyze_window(i, commits, time_windows)
        for tw in local_counts:
            for pair, count in local_counts[tw].items():
                global_counts[tw][pair] += count

    return global_counts

def extract_top_couplings(coupling_counts, top_n=3):
    """
    Extract the top N file pairs with the highest degree of temporal coupling for each time window.
    """
    results = {}
    for tw, counts in coupling_counts.items():
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        results[tw] = [{"files": list(pair), "count": count} for pair, count in sorted_counts]
    return results

def save_results_to_json(results, output_file):
    """
    Save the temporal coupling results to a JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    logging.info(f"Results saved to {output_file}")

def main():
    """
    Main function to coordinate the temporal coupling analysis.
    """
    repo_path = r"C:\Users\Mrbh\OneDrive\Mrbh\University\2 - Master\Curriculum\1st Semester - 5 Courses - 24 ECTS\Fundemental of Software Systems\Assignments\SE I - Repo\react"
    output_file = "temporal_coupling_js_only.json"
    time_windows = [24, 48, 72]

    logging.info("Starting temporal coupling analysis...")
    commits = extract_and_sort_commits(repo_path)
    coupling_counts = process_commit_pairing(commits, time_windows)
    results = extract_top_couplings(coupling_counts)
    save_results_to_json(results, output_file)
    logging.info("Analysis complete.")

if __name__ == "__main__":
    main()
