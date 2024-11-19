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

def extract_commits_with_js(repo_path):
    """
    Extract commits from the repository.
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
    logging.info(f"Total commits with `.js` files: {len(commits)}")
    return commits

def analyze_temporal_coupling(commits, time_windows):
    """
    Analyze temporal coupling by identifying file pairs changed together within a time window.
    """
    coupling_counts = {tw: defaultdict(int) for tw in time_windows}

    for idx, current_commit in enumerate(commits):
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

def analyze_logical_coupling(commits):
    """
    Analyze logical coupling by identifying file pairs frequently committed together.
    """
    coupling_counts = defaultdict(int)

    for commit in commits:
        commit_files = list(commit["files"])
        # Count every unique pair of files in the same commit
        for i in range(len(commit_files)):
            for j in range(i + 1, len(commit_files)):
                file_pair = tuple(sorted([commit_files[i], commit_files[j]]))
                coupling_counts[file_pair] += 1

    return coupling_counts

def extract_top_couplings(coupling_counts, top_n=3):
    """
    Extract the top N file pairs with the highest degree of coupling.
    """
    if isinstance(coupling_counts, dict):  # For temporal coupling (multi-window)
        results = {}
        for tw, counts in coupling_counts.items():
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
            results[tw] = [{"files": list(pair), "count": count} for pair, count in sorted_counts]
        return results
    else:  # For logical coupling (single dictionary)
        sorted_counts = sorted(coupling_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [{"files": list(pair), "count": count} for pair, count in sorted_counts]

def save_results_to_json(results, output_file):
    """
    Save the coupling results to a JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    logging.info(f"Results saved to {output_file}")

def main():
    """
    Main function to coordinate both temporal and logical coupling analyses.
    """
    repo_path = r"C:\Users\Mrbh\OneDrive\Mrbh\University\2 - Master\Curriculum\1st Semester - 5 Courses - 24 ECTS\Fundemental of Software Systems\Assignments\SE I - Repo\react"

    temporal_output_file = "temporal_coupling.json"
    logical_output_file = "logical_coupling.json"
    time_windows = [24, 48, 72]

    logging.info("Starting coupling analysis...")
    commits = extract_commits_with_js(repo_path)

    # Temporal Coupling Analysis
    logging.info("Starting temporal coupling analysis...")
    temporal_coupling_counts = analyze_temporal_coupling(commits, time_windows)
    temporal_results = extract_top_couplings(temporal_coupling_counts)
    save_results_to_json(temporal_results, temporal_output_file)

    # Logical Coupling Analysis
    logging.info("Starting logical coupling analysis...")
    logical_coupling_counts = analyze_logical_coupling(commits)
    logical_results = extract_top_couplings(logical_coupling_counts)
    save_results_to_json(logical_results, logical_output_file)

    logging.info("Coupling analysis complete.")

if __name__ == "__main__":
    main()