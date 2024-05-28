import asyncio
from typing import List

async def create_invoice(
    userId: str, 
    services: List[ServiceDetail], 
    parts: List[PartDetail], 
    taxRateId: str, 
    dueDate: str
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
    total_parts_cost = 0
    errors = []

    try:
        # Concurrently fetch all rates and parts
        rate_tasks = [prisma.models.Rate.prisma().find_unique(where={"id": service.rateId}) for service in services]
        part_tasks = [prisma.models.Part.prisma().find_unique(where={"id": part.partId}) for part in parts]
        tax_rate_task = prisma.models.TaxRate.prisma().find_unique(where={"id": taxRateId})

        rates, parts_details, tax_rate = await asyncio.gather(
            asyncio.gather(*rate_tasks),
            asyncio.gather(*part_tasks),
            tax_rate_task
        )

        for service, rate in zip(services, rates):
            if rate:
                total_service_cost += rate.amount * service.hours
            else:
                errors.append(f"Rate not found for service ID: {service.rateId}")

        for part, part_detail in zip(parts, parts_details):
            if part_detail:
                total_parts_cost += (
                    part_detail.cost
                    + part_detail.cost * part_detail.markupPercentage / 100
                ) * part.quantity
            else:
                errors.append(f"Part not found for part ID: {part.partId}")

        if tax_rate:
            total_tax = (total_service_cost + total_parts_cost) * (tax_rate.percentage / 100)
        else:
            errors.append(f"Tax rate not found for tax rate ID: {taxRateId}")
            total_tax = 0

        total_amount_due = total_service_cost + total_parts_cost + total_tax

        if errors:
            # Handle the errors as needed, e.g., log them or raise an exception
            print("Errors occurred:", errors)

        return CreateInvoiceOutput(
            userId=userId,
            services=services,
            parts=parts,
            taxRateId=taxRateId,
            dueDate=dueDate,
            totalServiceCost=total_service_cost,
            totalPartsCost=total_parts_cost,
            totalTax=total_tax,
            totalAmountDue=total_amount_due
        )
    except Exception as e:
        # Handle exceptions and log them
        print(f"An error occurred: {e}")
        raise

# Example usage
# invoice = await create_invoice(userId, services, parts, taxRateId, dueDate)