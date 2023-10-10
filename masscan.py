import os
import subprocess
import time
import re

# Check if "sitelist.txt" exists
if not os.path.exists("sitelist.txt"):
    print("Error: The 'sitelist.txt' file does not exist. You need to create a 'sitelist.txt' file containing a list of sites to scan.")
    exit(1)

# Create the "output" folder if it doesn't exist
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# Read the list of sites from "sitelist.txt" into an array, ignoring lines starting with '#'
sites = []
with open("sitelist.txt", "r") as file:
    for line in file:
        line = line.strip()
        if not line.startswith('#'):
            # Add "https://" if missing
            if not line.startswith("https://") and not line.startswith("http://"):
                line = "https://" + line
            sites.append(line)

# API Token for WPScan (replace with your actual API token)
api_token = "NeQNvGFt6kl7URZZWVYawWsAz5ewWCsX0Sas1agQWoQ"

# Function to remove non-ASCII characters from a string, preserving newlines
def remove_non_ascii(text):
    return ''.join(char if 32 <= ord(char) < 127 or char == '\n' else '' for char in text)

# Calculate the total number of sites for progress tracking
total_sites = len(sites)

# Iterate through the array and run WPScan for each site
for i, site in enumerate(sites, start=1):
    try:
        # Define the WPScan command with --random-user-agent and --api-token
        wpscan_command = ["wpscan", "--url", site, "--random-user-agent", "--api-token", api_token]
        
        # Generate the filename based on the site URL
        site_name = site.split("//")[1].replace("/", "_").replace(".", "_")
        output_file = os.path.join(output_folder, f"{site_name}_wpscan.txt")
        
        # Run WPScan and redirect the output to the file
        with open(output_file, "w") as output_file:
            process = subprocess.Popen(wpscan_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if stdout:
                # Remove the banner and version information
                cleaned_output = remove_non_ascii(stdout)
                output_file.write(cleaned_output)
            if stderr:
                output_file.write(remove_non_ascii(stderr))
        
        # Check if API limit message is present in the output
        if "Scan Aborted: Your API limit has been reached" in stdout or "Scan Aborted: Your API limit has been reached" in stderr:
            print("API Limit Reached. Please run again in 24 hours.")
            break
        
        # Comment out the scanned site in the sitelist
        with open("sitelist.txt", "r") as infile:
            lines = infile.readlines()
        with open("sitelist.txt", "w") as outfile:
            for line in lines:
                if line.strip() == site:
                    outfile.write(f"# {line}")
                else:
                    outfile.write(line)
        
        # Calculate the progress percentage
        progress = (i / total_sites) * 100
        
        # Print the progress with a simple progress bar
        progress_bar = "#" * int(progress / 10)
        spaces = " " * (10 - len(progress_bar))
        print(f"Scanning progress: [{progress_bar}{spaces}] {int(progress)}%")
        print(f"WPScan completed for {site}. Output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"WPScan failed for {site}. Error: {e}")
    except Exception as e:
        print(f"Error running WPScan for {site}: {str(e)}")

# If the loop completes without hitting the API limit message, you can wait for 24 hours
if i == total_sites:
    print("Scanning completed. You can run again in 24 hours.")
    time.sleep(24 * 3600)  # Wait for 24 hours (in seconds) before running again
