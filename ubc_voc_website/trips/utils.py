from trips.models import TripSignupTypes

def is_signup_type_change_valid(current_signup_type, new_signup_type, valid_signup_types):
    """
        Not every combination of current/new signup type is valid. The following are the valid types,
        assuming the destination list is currently open for signups:

        If currently INTERESTED:
            - upgrade to COMMITTED
            - upgrade to GOING
            - downgrade to NO_LONGER_INTERESTED

        If currently COMMITTED:
            - upgrade to GOING
            - downgrade to BAILED_FROM_COMMITTED

        If currently GOING:
            - downgrade to NO_LONGER_GOING

        If currently NO_LONGER_INTERESTED:
            - upgrade to INTERESTED
            - upgrade to COMMITTED
            - upgrade to GOING

        If currently BAILED_FROM_COMMITTED:
            - upgrade to INTERESTED
            - upgrade to COMMITTED
            - upgrade to GOING

        If currently NO_LONGER_GOING:
            - upgrade to INTERESTED
            - upgrade to COMMITTED
            - upgrade to GOING

        This function considers these valid pairs, as well as whether the destination list for the trip is open
        It returns True if the SignupType change is valid, False otherwise
    """
    if current_signup_type == TripSignupTypes.INTERESTED:
        if new_signup_type == TripSignupTypes.INTERESTED: # protect people from moving themselves to the back of the current list
            return False
        elif new_signup_type == TripSignupTypes.COMMITTED:
            return TripSignupTypes.COMMITTED in valid_signup_types
        elif new_signup_type == TripSignupTypes.GOING:
            return TripSignupTypes.GOING in valid_signup_types
        elif new_signup_type == TripSignupTypes.NO_LONGER_INTERESTED:
            return True
        else: # BAILED_FROM_COMMITTED and NO_LONGER_GOING don't make sense
            return False
    elif current_signup_type == TripSignupTypes.COMMITTED:
        if new_signup_type == TripSignupTypes.INTERESTED or new_signup_type == TripSignupTypes.COMMITTED:
            return False
        elif new_signup_type == TripSignupTypes.GOING:
            return TripSignupTypes.GOING in valid_signup_types
        elif new_signup_type == TripSignupTypes.BAILED_FROM_COMMITTED:
            return True
        else:
            return False
    elif current_signup_type == TripSignupTypes.GOING:
        if new_signup_type == TripSignupTypes.NO_LONGER_GOING:
            return True
        else:
            return False
    else:
        if new_signup_type == TripSignupTypes.INTERESTED:
            return TripSignupTypes.INTERESTED in valid_signup_types
        elif new_signup_type == TripSignupTypes.COMMITTED:
            return TripSignupTypes.COMMITTED in valid_signup_types
        elif new_signup_type == TripSignupTypes.GOING:
            return TripSignupTypes.GOING in valid_signup_types
        else:
            return False
