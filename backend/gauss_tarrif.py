import math

def gaussian(x, mean, sigma=2):
    """
    Gaussian function matching your JavaScript implementation.
    
    Parameters:
    x (float): Input value
    mean (float): Mean of the Gaussian
    sigma (float): Standard deviation of the Gaussian
    
    Returns:
    float: Gaussian value
    """
    return math.exp(-0.5 * math.pow((x - mean) / sigma, 2))

def hourly_consumption(hour):
    """
    Evaluate electricity consumption at a given hour using two Gaussian peaks.
    
    Parameters:
    hour (float): Hour of the day (0-24)
    
    Returns:
    float: Consumption value (scaled 0-100)
    """
    # Calculate the two Gaussian peaks
    morning_peak = gaussian(hour, 9, 2)    # Morning peak centered at 9:00, sigma=2
    evening_peak = gaussian(hour, 19, 2.5) # Evening peak centered at 19:00, sigma=2.5
    
    # Combine the peaks (you might want to scale these)
    total_consumption = morning_peak + evening_peak
    
    return total_consumption

if __name__ == "__main__":
    # Test the function for each hour of the day
    for hour in range(24):
        consumption = hourly_consumption(hour)*500*0.15 + 500*0.85
        print(f"Hour {hour}: Consumption {consumption:.4f}")