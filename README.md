# Ivy_homes
# Autocomplete API Name Extractor

This project provides a solution for extracting all possible names from an autocomplete API running at `http://35.200.185.69:8000`. It systematically explores the API using a breadth-first search approach and handles various constraints including rate limits.

## Features

- Extracts all names from the autocomplete API
- Supports multiple API versions (v1, v2, v3)
- Implements breadth-first search algorithm for optimal exploration
- Handles rate limiting through adaptive request intervals
- Tracks statistics for requests made and names found
- Supports pagination through limit parameters
- Efficiently prunes the search space to minimize requests

## How It Works

The extractor uses a breadth-first search algorithm to systematically explore all possible name prefixes:

1. Starts with single character prefixes (a-z and 0-9)
2. For each prefix, makes a request to the API
3. If a full page of results is received, adds more specific prefixes to the queue
4. Continues until all possible prefixes have been explored
5. Tracks all unique names discovered in the process

## Requirements

- Python 3.6+
- `requests` library (`pip install requests`)

## Usage

### Extract names from all API versions:

```bash
python autocomplete_extractor.py --all-versions
```

### Extract names from a specific API version:

```bash
python autocomplete_extractor.py --version v1
```

## Implementation Details

### Breadth-First Search

The solution implements breadth-first search, starting with short prefixes and exploring more specific ones only when necessary. This approach:

- Minimizes the number of API requests needed
- Handles pagination efficiently
- Avoids duplicate requests
- Prunes branches that wouldn't yield new results

### Rate Limit Handling

The script adaptively handles rate limits by:
- Implementing progressive delays between requests
- Providing retry logic with exponential backoff
- Tracking and adjusting request interval based on server responses

### Results Handling

The extracted names are:
- Deduplicated using a set
- Saved to JSON files for further analysis
- Reported in a concise summary with metrics

## API Exploration Findings

During exploration, I discovered several important aspects of the API:

1. **Multiple Versions**: The API supports different versions (v1, v2, v3) with varying results
2. **Response Format**: The API returns JSON data that may be structured as a list or dictionary
3. **Pagination**: Results are paginated, with a default limit that can be modified
4. **Rate Limiting**: The API has rate limiting in place to prevent excessive requests
5. **Prefix Matching**: The API performs prefix matching, allowing exploration via BFS
6. **Name Structure**: Names may be returned directly or within nested fields

## Challenges Faced

1. **Discovering API Structure**: Without documentation, I had to discover the API's behavior through testing
2. **Optimizing Requests**: Finding the right balance between thoroughness and efficiency
3. **Handling Rate Limits**: Implementing adaptive strategies to work within API constraints
4. **Response Format Variations**: Accommodating different response formats across versions
5. **Search Space Pruning**: Developing heuristics to minimize unnecessary requests

## Optimizations

The solution includes several optimizations:
- Uses a session object to maintain connection
- Implements early termination for branches that won't yield new results
- Prunes the search space intelligently based on result counts
- Deduplicates results to avoid redundant storage

## Future Improvements

Potential improvements include:
- Parallel exploration for faster extraction
- More sophisticated backoff strategies for rate limiting
- Better heuristics for search space pruning
- Support for additional API parameters

## Author

Meemansha Singh
