from rest_framework.exceptions import ValidationError


class PasswordsAreNotEqualError(ValidationError):
    code = "passwords_are_not_equal"
    detail = "Password is not not equal with duplicate password"


class UsernameAlreadyExistsError(ValidationError):
    code = "username_already_exists"
    detail = "Username Already exists"
