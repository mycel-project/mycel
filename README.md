# Mycel

## Setup

- Ensure **Python** and **git** are installed on your system.
- Clone this repo : `git clone https://github.com/mycel-project/mycel`
- Depending on your OS, run setup.bat (windows, can be named just "setup") or setup.sh (linux/macOS). Don't forget to make the script executable if needed.
   
### Running the app

After installation, use the provided launch scripts: 

- run.bat (or just "run") for Windows 
- run.sh for Linux/macOS.

### Updating Mycel
Run `git pull` to get the last stable release of Mycel.

*Note*: Some updates may introduce new configuration options. If so, you might need to manually update your config.json file by referring to the config.example.json template.

## On the safety of your learning data
All your learning data is saved in a SQLite file (default: mycel.db) at the root of your Mycel folder. Updating Mycel with a standard git pull will not erase or modify it.

> [!CAUTION]
> **Back up this file regularly — it contains all your learning data.**
> If it is lost or corrupted, your data cannot be recovered. Mycel does not yet include any built-in versioning or backup system, so you are solely responsible for keeping this file safe.

We **strongly** recommend copying mycel.db to a secure location on a regular basis — whether manually or through an automated backup solution.
