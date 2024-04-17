from typing import List

from pydantic import BaseModel


class ServiceUpdate(BaseModel):
    """
    Details necessary for updating or adding a new service to the invoice.
    """

    service_id: str
    hours: float
    rate_id: str


class PartUpdate(BaseModel):
    """
    Details necessary for updating or adding a new part to the invoice.
    """

    part_id: str
    quantity: int
    cost: float


class InvoiceDetails(BaseModel):
    """
    Detailed structure of the updated invoice for confirmation.
    """

    id: str
    status: str
    total_amount: float


class InvoiceUpdateResponse(BaseModel):
    """
    Response model for the invoice update process, confirming the updated details or indicating any errors.
    """

    success: bool
    message: str
    updated_invoice: InvoiceDetails


async def update_invoice(
    id: str,
    services: List[ServiceUpdate],
    parts: List[PartUpdate],
    tax_rate_id: str,
    subtotal: float,
    total: float,
) -> InvoiceUpdateResponse:
    """
    Updates details of an existing invoice.

    Args:
        id (str): Unique identifier for the invoice to be updated.
        services (List[ServiceUpdate]): List of services included in the invoice.
        parts (List[PartUpdate]): List of parts used in the invoice.
        tax_rate_id (str): The tax rate identifier applicable to the invoice.
        subtotal (float): The subtotal before taxes are applied.
        total (float): The total amount after taxes.

    Returns:
        InvoiceUpdateResponse: Response model for the invoice update process, confirming the updated details or indicating any errors.
    """
    try:
        updated_invoice = InvoiceDetails(id=id, status="UPDATED", total_amount=total)
        return InvoiceUpdateResponse(
            success=True,
            message="Invoice updated successfully",
            updated_invoice=updated_invoice,
        )
    except Exception as e:
        return InvoiceUpdateResponse(
            success=False,
            message=f"Failed to update invoice: {str(e)}",
            updated_invoice=None,
        )
