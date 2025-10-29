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

def precompute_gaussian_peak():
    total_consumption = []
    for hour in range(24):
        morning_peak = gaussian(hour, 9, 2)    # Morning peak centered at 9:00, sigma=2
        evening_peak = gaussian(hour, 19, 2.5)  # Evening peak centered at 19:00, sigma=2.5
        total_consumption.append(morning_peak + evening_peak)
    return total_consumption

if __name__ == "__main__":
    # Test the function for each hour of the day
    for hour in range(24):
        # The value vary only by 15% as said by expert
        consumption = precompute_gaussian_peak()[hour]*500*0.15 + 500*0.85
        print(f"Hour {hour}: Consumption {consumption:.4f}")