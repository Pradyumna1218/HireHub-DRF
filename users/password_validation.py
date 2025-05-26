from rest_framework import serializers

def validate_strong_password(password: str) -> str:
    """
    Validates the strength of a password.

    Criteria:
        - At least 8 characters long
        - At least one lowercase letter
        - At least one uppercase letter
        - At least one digit
        - At least one special character (!@#$%^&*()-+)
        - No adjacent repeated characters

    Raises:
        serializers.ValidationError: If any condition is not met.
    """

    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long.")

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()-+" for c in password)
    no_adjacent_duplicates = all(password[i] != password[i + 1] for i in range(len(password) - 1))

    if not all([has_lower, has_upper, has_digit, has_special, no_adjacent_duplicates]):
        raise serializers.ValidationError(
            "Password must contain at least one lowercase, one uppercase, one digit, "
            "one special character (!@#$%^&*()-+), and no adjacent repeated characters."
        )

    return password