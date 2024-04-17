from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class UserRegistrationResponse(BaseModel):
    """
    Confirms the successful registration of a new user, potentially returning an identifier or a token.
    """

    user_id: str
    message: str


async def register_user(
    email: str,
    password: str,
    first_name: Optional[str],
    last_name: Optional[str],
    company_name: Optional[str],
    address: Optional[str],
    tax_id: Optional[str],
) -> UserRegistrationResponse:
    """
    Registers a new user to the application.

    This function creates a new user record in the Users table with the provided email and password. It also creates an associated UserProfile with the provided personal and company details. If the email is already used, the registration fails.

    Args:
        email (str): Email address of the user. Must be unique.
        password (str): Password for the user account. Should meet security criteria.
        first_name (Optional[str]): First name of the user.
        last_name (Optional[str]): Last name of the user.
        company_name (Optional[str]): The name of the company the user represents or owns.
        address (Optional[str]): Physical address of the user or their company.
        tax_id (Optional[str]): Tax identification number of the user or their company.

    Returns:
        UserRegistrationResponse: Confirms the successful registration of a new user, potentially returning an identifier or a token.

    Example:
        registration_response = await register_user(email="jane.doe@example.com", password="securePassword123", first_name="Jane", last_name="Doe", company_name="Doe Inc.", address="123 Main St, Anytown, USA", tax_id="123-456-789")
        print(registration_response)
        > UserRegistrationResponse(user_id="uuid_generated_for_new_user", message="User successfully registered.")
    """
    existing_user = await prisma.models.User.prisma().find_unique(
        where={"email": email}
    )
    if existing_user:
        return UserRegistrationResponse(user_id="", message="Email is already in use.")
    new_user = await prisma.models.User.prisma().create(
        data={
            "email": email,
            "password": password,
            "UserProfile": {
                "create": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "companyName": company_name,
                    "address": address,
                    "taxId": tax_id,
                }
            },
        }
    )
    return UserRegistrationResponse(
        user_id=new_user.id, message="User successfully registered."
    )
