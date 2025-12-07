import csv
from datetime import datetime, timedelta
import random

def gen(out_path="data.csv", seconds=600):
    start = datetime.utcnow()
    price = 100.0
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "price", "volume"])
        for i in range(seconds):
            price += random.uniform(-0.3, 0.3)
            volume = random.randint(50, 300)
            # occasional spike
            if random.random() < 0.01:
                price *= random.choice([0.5, 1.5, 2.0])
                volume *= 5
            writer.writerow([ (start + timedelta(seconds=i)).isoformat(), round(price,4), volume])

if __name__ == "__main__":
    gen("data.csv", seconds=300)
    print("generated data.csv")
