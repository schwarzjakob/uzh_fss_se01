import json
import logging
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
        {mf.new_path for mf in commit.modified_files if mf.new_path and mf.new_path.endswith('.js')}
        for commit in pydriller.Repository(repo_path).traverse_commits()
    ]
    # Remove commits with no `.js` files
    commits = [commit for commit in commits if commit]
    logging.info(f"Total commits with `.js` files: {len(commits)}")
    return commits

def analyze_logical_coupling(commits):
    """
    Analyze logical coupling by identifying file pairs frequently committed together.
    """
    coupling_counts = defaultdict(int)

    for commit_files in commits:
        commit_files = list(commit_files)
        # Count every unique pair of files in the same commit
        for i in range(len(commit_files)):
            for j in range(i + 1, len(commit_files)):
                file_pair = tuple(sorted([commit_files[i], commit_files[j]]))
                coupling_counts[file_pair] += 1

    return coupling_counts

def extract_top_couplings(coupling_counts, top_n=3):
    """
    Extract the top N file pairs with the highest degree of logical coupling.
    """
    sorted_counts = sorted(coupling_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    results = [{"files": list(pair), "count": count} for pair, count in sorted_counts]
    return results

def save_results_to_json(results, output_file):
    """
    Save the logical coupling results to a JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    logging.info(f"Results saved to {output_file}")

def main():
    """
    Main function to coordinate the logical coupling analysis.
    """
    repo_path = r"C:\Users\Mrbh\OneDrive\Mrbh\University\2 - Master\Curriculum\1st Semester - 5 Courses - 24 ECTS\Fundemental of Software Systems\Assignments\SE I - Repo\react"
    output_file = "logical_coupling.json"

    logging.info("Starting logical coupling analysis...")
    commits = extract_commits_with_js(repo_path)
    coupling_counts = analyze_logical_coupling(commits)
    results = extract_top_couplings(coupling_counts)
    save_results_to_json(results, output_file)
    logging.info("Analysis complete.")

if __name__ == "__main__":
    main()