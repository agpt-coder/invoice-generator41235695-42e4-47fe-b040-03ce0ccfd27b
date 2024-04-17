import datetime
from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class ServiceDetail(BaseModel):
    """
    Details of each service including billable hours and rate id.
    """

    serviceId: str
    hours: float
    rateId: str


class PartDetail(BaseModel):
    """
    Details of each part used including quantity and cost.
    """

    partId: str
    quantity: int
    cost: float


class CreateInvoiceOutput(BaseModel):
    """
    Output model for a newly created invoice, including all details for confirmation.
    """

    invoiceId: str
    status: str
    totalAmount: float


async def create_invoice(
    userId: str,
    services: List[ServiceDetail],
    parts: List[PartDetail],
    taxRateId: str,
    dueDate: str,
) -> CreateInvoiceOutput:
    """
    Creates a new invoice based on input parameters.

    Args:
    userId (str): The user ID of the invoice issuer.
    services (List[ServiceDetail]): List of services provided.
    parts (List[PartDetail]): List of parts used.
    taxRateId (str): Identifier for the applicable tax rate based on jurisdiction.
    dueDate (str): Due date for the invoice payment.

    Returns:
    CreateInvoiceOutput: Output model for a newly created invoice, including all details for confirmation.
    """
    total_service_cost = 0
    for service in services:
        rate = await prisma.models.Rate.prisma().find_unique(
            where={"id": service.rateId}
        )
        if rate:
            total_service_cost += rate.amount * service.hours
    total_parts_cost = 0
    for part in parts:
        part_details = await prisma.models.Part.prisma().find_unique(
            where={"id": part.partId}
        )
        if part_details:
            total_parts_cost += (
                part_details.cost
                + part_details.cost * part_details.markupPercentage / 100
            ) * part.quantity
    tax_rate = await prisma.models.TaxRate.prisma().find_unique(where={"id": taxRateId})
    if tax_rate:
        total_tax = (total_service_cost + total_parts_cost) * (
            tax_rate.percentage / 100
        )
    else:
        total_tax = 0
    total_amount_due = total_service_cost + total_parts_cost + total_tax
    invoice = await prisma.models.Invoice.prisma().create(
        data={
            "userId": userId,
            "dueDate": datetime.datetime.strptime(dueDate, "%Y-%m-%d"),
            "totalAmount": total_amount_due,
            "taxRateId": taxRateId,
            "status": "DRAFT",
        }
    )
    for service in services:
        await prisma.models.BillableItem.prisma().create(
            data={
                "invoiceId": invoice.id,
                "serviceId": service.serviceId,
                "rateId": service.rateId,
                "partId": "",
            }
        )
    for part in parts:
        await prisma.models.BillableItem.prisma().create(
            data={
                "invoiceId": invoice.id,
                "serviceId": "",
                "rateId": "",
                "partId": part.partId,
            }
        )
    return CreateInvoiceOutput(
        invoiceId=invoice.id, status=invoice.status, totalAmount=total_amount_due
    )
