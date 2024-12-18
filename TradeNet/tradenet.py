from flask import Flask, request, jsonify
import requests
import time
import argparse

# Initialize Flask app
app = Flask(__name__)

# Cache for storing quotes
cache = {}
CACHE_TTL = 10  # Cache Time-To-Live in seconds

# Define the command-line argument parser
parser = argparse.ArgumentParser(description='TradeNet Node')
parser.add_argument('--port', type=int, default=1983, help='Port to bind the server to')

# Parse the arguments
args = parser.parse_args()
PORT = args.port

@app.route('/get_quote', methods=['GET'])
def get_quote():
    input_mint = request.args.get('input_mint')
    output_mint = request.args.get('output_mint')
    amount = request.args.get('amount')

    # Create a unique cache key for this request
    cache_key = f"{input_mint}_{output_mint}_{amount}"

    # Check if the cache has a valid entry
    current_time = time.time()
    if cache_key in cache:
        cached_response, timestamp = cache[cache_key]
        if current_time - timestamp < CACHE_TTL:
            return jsonify(cached_response)

    # If not in cache or expired, make the external API call
    quote_url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_mint}&outputMint={output_mint}&amount={amount}&onlyDirectRoutes=true"
    response = requests.get(quote_url)

    if response.status_code == 200:
        # Cache the response
        cache[cache_key] = (response.json(), current_time)
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch quote"}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
