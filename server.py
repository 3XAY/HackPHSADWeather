from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# USB Hard Drive mount point (adjust if different)
DATA_DIR = "/mnt/usbdrive/plant_data"
os.makedirs(DATA_DIR, exist_ok=True)

sensor_data = []

@app.route('/plant_data', methods=['POST'])
def receive_plant_data():
    """Receive sensor data from Device 1"""
    try:
        data = request.get_json()
        data['timestamp'] = datetime.now().isoformat()
        
        # Add to memory
        sensor_data.append(data)
        
        # Save to USB hard drive
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"{DATA_DIR}/sensors_{date_str}.jsonl"
        
        with open(filename, 'a') as f:
            f.write(json.dumps(data) + '\n')
        
        print(f"✓ Saved: Moisture={data.get('moisture')}, "
              f"R={data.get('red_light')}, G={data.get('green_light')}, B={data.get('blue_light')}")
        
        # Keep only last 100 in memory
        if len(sensor_data) > 100:
            sensor_data.pop(0)
        
        return jsonify({"status": "success"}), 200
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/latest', methods=['GET'])
def get_latest():
    """Get latest reading for TFT display"""
    if sensor_data:
        return jsonify(sensor_data[-1])
    return jsonify({"status": "no data"}), 404


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    if not sensor_data:
        return jsonify({"status": "no data"}), 404
    
    moistures = [d.get('moisture', 0) for d in sensor_data]
    return jsonify({
        "count": len(sensor_data),
        "avg_moisture": sum(moistures) / len(moistures),
        "min_moisture": min(moistures),
        "max_moisture": max(moistures)
    })


if __name__ == '__main__':
    print("Starting Plant Monitor Server")
    print(f"Data directory: {DATA_DIR}")
    print(f"Server IP: 10.3.141.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)