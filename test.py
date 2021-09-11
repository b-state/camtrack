import os
import datetime

area_path = os.makedirs("./area", exist_ok=True)
print("./area/"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+".area")
print(area_path)