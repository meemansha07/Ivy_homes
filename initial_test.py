import requests
import time
import json
import string
import sys
from collections import deque

class AutocompleteExtractor:
    """
    Class for extracting all names from an autocomplete API using a breadth-first search approach
    """
    def __init__(self, base_url="http://35.200.185.69:8000", version="v3", limit=100):
        self.base_url = base_url
        self.version = version
        self.limit = limit
        self.request_count = 0
        self.names = set()
        self.queue = deque()
        self.seen_prefixes = set()
        
        # Configure request parameters
        self.request_interval = 0.1  # 100ms between requests to avoid rate limiting
        self.max_retries = 3
        self.retry_delay = 1
        
        # Characters to use for prefix exploration
        self.chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        
    def make_request(self, query):
        """Make a request to the autocomplete API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                url = f"{self.base_url}/v1/autocomplete?query={query}&version={self.version}&limit={self.limit}"
                response = requests.get(url, timeout=5)
                self.request_count += 1
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = (attempt + 1) * self.retry_delay
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                # If we got a successful response, return the data
                if response.status_code == 200:
                    return response.json()
                
                print(f"Error: Status code {response.status_code}")
                return None
                
            except Exception as e:
                print(f"Request error: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * self.retry_delay
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Max retries exceeded")
                    return None
            
            time.sleep(self.request_interval)
        
        return None
    
    def process_results(self, data, prefix):
        """Process results from API response"""
        results = []
        
        # Handle different response formats
        if isinstance(data, dict):
            results = data.get('results', [])
        elif isinstance(data, list):
            results = data
        
        # Add unique results to our set of names
        new_results = 0
        for result in results:
            # Handle different possible result formats
            name = None
            if isinstance(result, str):
                name = result
            elif isinstance(result, dict):
                # Try common fields that might contain the name
                for field in ['name', 'text', 'value', 'suggestion']:
                    if field in result:
                        name = result[field]
                        break
            
            if name and name not in self.names:
                self.names.add(name)
                new_results += 1
        
        # Return True if we received a full page of results,
        # indicating we should continue exploring this prefix
        return len(results) >= self.limit
    
    def explore_all_names(self):
        """
        Main method to explore and extract all names using breadth-first search
        """
        # Start with single character prefixes
        for char in self.chars:
            self.queue.append(char)
        
        total_prefixes_explored = 0
        
        # Breadth-first search through all possible prefixes
        while self.queue:
            prefix = self.queue.popleft()
            
            # Skip if we've already explored this prefix
            if prefix in self.seen_prefixes:
                continue
            
            self.seen_prefixes.add(prefix)
            total_prefixes_explored += 1
            
            # Periodically report progress
            if total_prefixes_explored % 10 == 0:
                print(f"Exploring prefix '{prefix}' ({total_prefixes_explored} prefixes explored, {len(self.names)} names found, {self.request_count} requests made)")
            
            # Get results for this prefix
            data = self.make_request(prefix)
            
            if data is None:
                continue
            
            # Process the results
            full_page = self.process_results(data, prefix)
            
            # If we got a full page of results or we have a short prefix,
            # add new prefixes to the queue to explore
            if full_page or len(prefix) < 3:
                for char in self.chars:
                    new_prefix = prefix + char
                    if new_prefix not in self.seen_prefixes:
                        self.queue.append(new_prefix)
            
            # Sleep to avoid overwhelming the API
            time.sleep(self.request_interval)
    
    def run(self):
        """Run the extraction process and return statistics"""
        print(f"Starting extraction from {self.base_url} using version {self.version}")
        
        start_time = time.time()
        self.explore_all_names()
        elapsed_time = time.time() - start_time
        
        print(f"\nExtraction complete!")
        print(f"Total requests made: {self.request_count}")
        print(f"Total names found: {len(self.names)}")
        print(f"Time elapsed: {elapsed_time:.2f} seconds")
        
        return {
            "request_count": self.request_count,
            "name_count": len(self.names),
            "names": sorted(list(self.names)),
            "elapsed_time": elapsed_time
        }
    
    def save_results(self, filename="autocomplete_results.json"):
        """Save the results to a JSON file"""
        results = {
            "metadata": {
                "base_url": self.base_url,
                "version": self.version,
                "request_count": self.request_count,
                "total_names": len(self.names)
            },
            "names": sorted(list(self.names))
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {filename}")

def discover_best_version(base_url="http://35.200.185.69:8000"):
    """Test different API versions to determine the optimal one"""
    versions = ["v1", "v2", "v3", "v4", "latest"]
    best_version = "v3"  # Default if nothing better is found
    max_results = 0
    
    print("Testing API versions to find the optimal one...")
    
    for version in versions:
        try:
            response = requests.get(f"{base_url}/v1/autocomplete?query=a&version={version}")
            if response.status_code == 200:
                data = response.json()
                result_count = 0
                
                if isinstance(data, dict):
                    result_count = data.get('count', 0) or len(data.get('results', []))
                elif isinstance(data, list):
                    result_count = len(data)
                
                print(f"Version '{version}': {result_count} results")
                
                if result_count > max_results:
                    max_results = result_count
                    best_version = version
            else:
                print(f"Version '{version}': Status {response.status_code}")
        except Exception as e:
            print(f"Version '{version}': Error - {str(e)}")
    
    print(f"Best version appears to be '{best_version}' with {max_results} results")
    return best_version

def discover_rate_limits(base_url="http://35.200.185.69:8000", version="v3"):
    """Discover rate limits by making rapid requests"""
    print("Testing for rate limits...")
    
    start_time = time.time()
    request_count = 0
    rate_limited = False
    
    for _ in range(50):  # Try 50 rapid requests
        try:
            response = requests.get(f"{base_url}/v1/autocomplete?query=a&version={version}", timeout=2)
            request_count += 1
            
            if response.status_code == 429:
                print(f"Rate limit detected after {request_count} requests")
                rate_limited = True
                break
                
            # No delay to test rate limiting
                
        except Exception as e:
            print(f"Error during rate limit testing: {str(e)}")
            break
    
    elapsed_time = time.time() - start_time
    
    if not rate_limited:
        rate = request_count/elapsed_time
        print(f"Made {request_count} requests in {elapsed_time:.2f} seconds without hitting rate limits")
        print(f"Approximate rate: {rate:.2f} requests per second")
        
        # Recommend a safe request interval (half the observed rate)
        safe_interval = 1 / (rate / 2)
        return min(0.5, safe_interval)  # Cap at 500ms to be extra safe
    else:
        # If rate limited, suggest a conservative interval
        return 1.0  # 1 request per second

def main():
    """Main function to run the autocomplete extractor"""
    base_url = "http://35.200.185.69:8000"
    
    print("=== Autocomplete API Name Extractor ===")
    
    # First, discover the best API version
    best_version = discover_best_version(base_url)
    
    # Then, discover rate limits
    safe_interval = discover_rate_limits(base_url, best_version)
    
    # Create and run the extractor
    extractor = AutocompleteExtractor(base_url=base_url, version=best_version)
    extractor.request_interval = safe_interval
    
    print(f"\nStarting extraction with request interval of {safe_interval:.2f} seconds")
    
    results = extractor.run()
    extractor.save_results()
    
    # Print the first 10 names as a sample
    print("\nSample of extracted names:")
    for name in sorted(list(extractor.names))[:10]:
        print(f"- {name}")
    
    print(f"\nFull results saved to autocomplete_results.json")

if __name__ == "__main__":
    main()