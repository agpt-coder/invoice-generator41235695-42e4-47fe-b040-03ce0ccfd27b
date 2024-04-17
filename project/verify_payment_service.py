from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class VerifyPaymentResponse(BaseModel):
    """
    The response provides details on the verified payment transaction, including its current status.
    """

    transactionId: str
    status: str
    errorMessage: Optional[str] = None


async def verify_payment(transactionId: str) -> VerifyPaymentResponse:
    """
    Verifies the status of a payment transaction.

    Args:
        transactionId (str): The unique identifier for the payment transaction to be verified.

    Returns:
        VerifyPaymentResponse: The response provides details on the verified payment transaction,
        including its current status.

    This function queries the database for a payment transaction matching the provided transactionId.
    It then verifies the status of the transaction and returns details including the transaction status
    and any error message if the transaction failed.
    """
    payment_record = await prisma.models.Payment.prisma().find_unique(
        where={"transactionId": transactionId}
    )
    if not payment_record:
        return VerifyPaymentResponse(
            transactionId=transactionId,
            status="Failed",
            errorMessage="Transaction not found",
        )
    status = (
        "Completed"
        if payment_record.amount and payment_record.paymentDate
        else "Pending"
    )
    errorMessage = None if status == "Completed" else "Payment is pending or incomplete"
    return VerifyPaymentResponse(
        transactionId=transactionId, status=status, errorMessage=errorMessage
    )
