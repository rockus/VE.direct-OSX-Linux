from get_miner_data import get_miner_power
from get_pannel_data import scan_charge_controller


miner_power = get_miner_power()
pannel_data = scan_charge_controller()

print("Miner Data:", miner_power)
print("Pannel Data:", pannel_data)
