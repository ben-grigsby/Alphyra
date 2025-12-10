import matplotlib.pyplot as plt
import numpy as np

# Constants
initial_investment = 50000
interest_rate = 0.10
years = np.arange(0, 31)  # Plot for 30 years

# Compound interest formula
future_value = initial_investment * (1 + interest_rate) ** years

# Plot
plt.figure(figsize=(10, 6))
plt.plot(years, future_value, marker='o')
plt.title('Growth of $50,000 at 10% Annual Interest (No Additional Contributions)')
plt.xlabel('Years')
plt.ylabel('Future Value ($)')
plt.grid(True)
plt.tight_layout()
plt.show()