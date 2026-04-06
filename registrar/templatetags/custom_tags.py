import datetime
from django import template

register = template.Library()

@register.filter
def calculate_age(dob):
    """Calculate age from date of birth (dob)"""
    if not dob:
        return "N/A"  # Handle cases where dob is missing
    
    today = datetime.date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    return age
