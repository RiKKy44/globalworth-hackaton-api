
import asyncio
import random
import json
from datetime import datetime
from argparse import ArgumentParser
from core.config import settings
from integrations.iot.mqtt_handler import MQTTClient

class SensorSimulator:
    def __init__(self, num_buildings: int = 3):
        self.num_buildings = num_buildings
        self.running = True
        self.buildings = [f"bld-{i+1:03d}" for i in range(num_buildings)]
    
    async def generate_data(self, interval: float = 5.0):
        """Generate mock sensor data"""
        async with MQTTClient() as mqtt:
            while self.running:
                try:
                    for building_id in self.buildings:
                        data = {
                            "timestamp": datetime.utcnow().isoformat(),
                            "co2_kg": round(random.uniform(800, 1500), 2),
                            "energy_kwh": round(random.uniform(2000, 5000), 1),
                            "water_m3": round(random.uniform(50, 200), 1),
                            "waste_kg": round(random.uniform(50, 300), 1),
                            "sensor_status": random.choice(["normal", "warning", "critical"])
                        }
                        
                        # Add occasional spikes
                        if random.random() < 0.1:
                            data["co2_kg"] *= 1.5
                            data["energy_kwh"] *= 1.3
                        
                        await mqtt.publish_esg_data(building_id, data)
                        print(f"Published to {building_id}: {data}")
                    
                    await asyncio.sleep(interval)
                except KeyboardInterrupt:
                    self.running = False
                except Exception as e:
                    print(f"Error: {str(e)}")
                    await asyncio.sleep(1)

if __name__ == "__main__":
    parser = ArgumentParser(description='Mock Sensor Data Generator')
    parser.add_argument('--buildings', type=int, default=3,
                      help='Number of buildings to simulate')
    parser.add_argument('--interval', type=float, default=5.0,
                      help='Data generation interval in seconds')
    
    args = parser.parse_args()
    
    simulator = SensorSimulator(args.buildings)
    try:
        asyncio.run(simulator.generate_data(args.interval))
    except KeyboardInterrupt:
        print("\nStopping sensor simulation...")