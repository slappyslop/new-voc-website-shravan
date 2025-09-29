import datetime

from .models import Membership

def get_end_date(today):
    """
    Evaluates the custom VOC membership end date logic
    
    If today is between Jan 1 and Apr 30 inclusive, return Sept 30 of the current year
    Otherwise return Sept 30 of the following year
    """
    current_year = today.year
    
    if datetime.datetime(current_year, 1, 1) <= today <= datetime.datetime(current_year, 4, 30):
        return datetime.datetime(current_year, 9, 30)
    
    else:
        return datetime.datetime(current_year + 1, 9, 30)

def is_minor(today, birthdate):
    """
    Determine whether a user is a minor based on their birthdate. This is required to determine 
    whether they are eligible to sign their own waiver or if a parent/guardian must sign on
    their behalf

    Returns True if the user is under 19 years of age
    Returns False if the user is 19 years of age or older
    """
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age < 19

def get_membership_type(user):
    """
    Given a user, return the Membership.MembershipType of their current, active membership
    If the user does not exist, or exists but is not a member return None
    """
    if not user:
        return None
    else:
        memberships = Membership.objects.filter(
            user=user,
            end_date__gte=datetime.date.today(),
            active=True
        )

        if not memberships.exists():
            return None
        else:
            return memberships.first().type
