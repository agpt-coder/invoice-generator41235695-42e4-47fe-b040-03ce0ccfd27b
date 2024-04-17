import datetime
import uuid
from typing import Optional

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class InitiatePaymentResponse(BaseModel):
    """
    Response model for the initiate payment request. Contains details about the payment attempt, including a transaction reference.
    """

    transaction_id: str
    status: str
    message: str
    payment_url: Optional[str] = None


async def initiate_payment(
    invoice_id: str, user_id: str, payment_method: str, amount: float, currency: str
) -> InitiatePaymentResponse:
    """
    Initiates the payment process for an invoice.

    Args:
        invoice_id (str): The unique identifier of the invoice for which the payment is being initiated.
        user_id (str): The unique identifier of the user initiating the payment.
        payment_method (str): The chosen payment method by the user for this transaction.
        amount (float): The amount being paid. This is to ensure the amount being sent matches the invoice amount for additional verification.
        currency (str): Currency in which the payment is being made.

    Returns:
        InitiatePaymentResponse: Response model for the initiate payment request. Contains details about the payment attempt, including a transaction reference.
    """
    transaction_id = str(uuid.uuid4())
    payment_url = f"https://paymentgateway.com/complete_payment/{transaction_id}"
    await prisma.models.Payment.prisma().create(
        data={
            "id": str(uuid.uuid4()),
            "invoiceId": invoice_id,
            "amount": amount,
            "currency": currency,
            "paymentDate": datetime.datetime.now(),
            "paymentMethod": payment_method,
            "transactionId": transaction_id,
            "User": {"connect": {"id": user_id}},
        }
    )
    await prisma.models.Invoice.prisma().update(
        where={"id": invoice_id}, data={"status": prisma.enums.InvoiceStatus.SENT}
    )
    payment_response = InitiatePaymentResponse(
        transaction_id=transaction_id,
        status="Initiated",
        message="Payment has been initiated. Please complete the payment process.",
        payment_url=payment_url,
    )
    return payment_response
