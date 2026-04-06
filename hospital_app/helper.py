
def calculate_bmi(weight, height):
    """Calculate BMI based on weight (kg) and height (cm)."""
    if height > 0 and weight > 0:
        height_m = height / 100  # Convert height to meters
        bmi = weight / (height_m ** 2)
        return round(bmi, 2)  # Return BMI rounded to two decimal places
    return None