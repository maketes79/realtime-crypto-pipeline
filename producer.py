import json
import websocket
from kafka import KafkaProducer

# CONFIGURATION
# 1. Binance WebSocket URL for Bitcoin/USDT trades
#    'btcusdt@trade' means we subscribe to the trade stream for the BTC/USDT pair.
BINANCE_WS_URL = 'wss://stream.binance.com:9443/ws/btcusdt@trade'

# 2. Kafka Configuration
#    'localhost:29092' is the port we opened in docker-compose for external access.
KAFKA_BOOTSTRAP_SERVERS = 'localhost:29092'
KAFKA_TOPIC_NAME = 'crypto_trades'

def on_message(ws, message):
    """
    Callback function triggered whenever a new message arrives from Binance.
    """
    # 1. Parse the raw string message into a JSON object
    data = json.loads(message)
    
    # 2. Extract only the useful fields (Data Cleaning at Source)
    #    e = Event Type, E = Event Time, s = Symbol, p = Price, q = Quantity
    #    We rename them to be more readable.
    trade_data = {
        'symbol': data['s'],
        'price': float(data['p']),
        'quantity': float(data['q']),
        'timestamp': data['E']
    }
    
    # 3. Send to Kafka
    #    We must send bytes, so we encode our JSON back to a string, then to bytes.
    print(f"Sending data: {trade_data}") # Print to console for verification
    producer.send(KAFKA_TOPIC_NAME, value=json.dumps(trade_data).encode('utf-8'))

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### Connection Closed ###")

def on_open(ws):
    print("### Connection Opened - Streaming Data ###")

if __name__ == "__main__":
    # Initialize Kafka Producer
    print("Connecting to Kafka...")
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    print("Connected to Kafka!")

    # Initialize WebSocket App
    ws = websocket.WebSocketApp(
        BINANCE_WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Run the WebSocket forever (blocking loop)
    ws.run_forever()