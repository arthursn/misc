# XKCD Scraper

A simple command-line tool to download and view comics from [xkcd.com](https://xkcd.com).

## Features

- Download comics by issue number
- Support for downloading ranges of comics (e.g., 100-105)
- Get the latest comic with the "latest" keyword
- Save images locally
- Option to open images after downloading

## Installation

This script requires Python 3 and the following dependencies:
- `requests`
- `BeautifulSoup4`

### Option 1: Install dependencies only

```
pip install requests beautifulsoup4
```

### Option 2: Install as a package

You can install the package directly from the project directory:

```
pip install .
```

This will make the `xkcd-scraper` command available in your environment.

## Usage

### If installed with pip:

```
xkcd-scraper [OPTIONS] ISSUE [ISSUE...]
```

### If running the script directly:

```
python xkcd_scraper.py [OPTIONS] ISSUE [ISSUE...]
```

### Arguments

- `ISSUE`: Issue number(s) to scrape. Can be:
  - A single issue (e.g., "123")
  - A range of issues (e.g., "100-105")
  - The keyword "latest" to get the most recent comic

### Options

- `-s, --save`: Save the comic image locally
- `-o, --open`: Open the comic image after downloading
- `-h, --help`: Show help message

### Examples

Download and display information about comic #1000:

```
xkcd-scraper 1000
```

Download and save comics #1000 through #1005:

```
xkcd-scraper 1000-1005 --save
```

Download, save, and open the latest comic:

```
xkcd-scraper latest --save --open
```

## Output

The script outputs JSON metadata for each comic, including:
- Title
- Image URL
- Alt text
- Local file path (if saved)

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for personal use only. Please respect the [xkcd license](https://xkcd.com/license.html) when using the downloaded content.
