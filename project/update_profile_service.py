from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class UserProfileModel(BaseModel):
    """
    The structured data of a user's profile, including personal and billing information.
    """

    firstName: str
    lastName: str
    companyName: Optional[str] = None
    address: str
    taxId: Optional[str] = None


class UserProfileUpdateResponse(BaseModel):
    """
    The response model for the 'update_profile' endpoint, confirming the update was successful and providing the updated profile data.
    """

    success: bool
    message: str
    updatedProfile: Optional[UserProfileModel] = None


async def update_profile(
    firstName: Optional[str],
    lastName: Optional[str],
    companyName: Optional[str],
    address: Optional[str],
    taxId: Optional[str],
) -> UserProfileUpdateResponse:
    """
    Updates user's profile information.

    Args:
    firstName (Optional[str]): The user's first name.
    lastName (Optional[str]): The user's last name.
    companyName (Optional[str]): The name of the company the user is associated with.
    address (Optional[str]): The user's current address.
    taxId (Optional[str]): The tax identification number of the user or their company.

    Returns:
    UserProfileUpdateResponse: The response model for the 'update_profile' endpoint, confirming the update was successful and providing the updated profile data.
    """
    userId = "current_authenticated_user_id"
    updated_profile = await prisma.models.UserProfile.prisma().update(
        where={"userId": userId},
        data={
            "firstName": firstName,
            "lastName": lastName,
            "companyName": companyName,
            "address": address,
            "taxId": taxId,
        },
    )
    if updated_profile:
        updated_user_profile_model = UserProfileModel(
            firstName=updated_profile.firstName,
            lastName=updated_profile.lastName,
            companyName=updated_profile.companyName,
            address=updated_profile.address,
            taxId=updated_profile.taxId,
        )
        return UserProfileUpdateResponse(
            success=True,
            message="User profile updated successfully.",
            updatedProfile=updated_user_profile_model,
        )
    else:
        return UserProfileUpdateResponse(
            success=False, message="Failed to update user profile.", updatedProfile=None
        )
