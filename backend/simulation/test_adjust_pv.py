import adjust_pv_module

def main():
	input_value = 100.0
	adjusted = adjust_pv_module.adjust_pv_estimate(input_value)
	print(f"Adjusted PV estimate: {input_value} to {adjusted:.2f}")  # Formats to two decimal places

if __name__ == "__main__":
	main()