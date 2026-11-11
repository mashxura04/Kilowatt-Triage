from src.main import calculate_after_insulation

savings = {
    1: {"gas": 82432, "coal": 95727},
    2: {"gas": 131653, "coal": 152887},
    3: {"gas": 162685, "coal": 188924},
    4: {"gas": 170859, "coal": 198417},
}

print("BOILER SAVINGS AS A PERCENTAGE OF POST-INSULATION HEATING")
print("-" * 65)

for zone in range(1, 5):
    remaining = calculate_after_insulation(zone)["heating_after_kwh"]

    gas_percentage = savings[zone]["gas"] / remaining * 100
    coal_percentage = savings[zone]["coal"] / remaining * 100

    print(
        f"Zone {zone}: "
        f"Gas = {gas_percentage:.2f}% | "
        f"Coal = {coal_percentage:.2f}%"
    )