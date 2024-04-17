import logging
from contextlib import asynccontextmanager
from typing import List, Optional

import project.create_invoice_service
import project.initiate_payment_service
import project.login_user_service
import project.register_user_service
import project.update_invoice_service
import project.update_profile_service
import project.verify_payment_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="Invoice Generator",
    lifespan=lifespan,
    description="To generate comprehensive and transparent invoices that cater to varying services, billable hours, parts used, different rates, and applicable taxes, you must integrate the following practices and information garnered from previous interactions: \n\n1. **Service Details and Billable Hours:** Begin by listing all services provided in the project, such as 'Project Management' (15 hours), 'Software Development' (30 hours), 'Quality Assurance' (20 hours), and 'User Interface Design' (25 hours). For each service, specify the billable hours along with the rate per hour, which may vary based on service complexity, urgency, or specific client agreements. \n\n2. **Parts Used:** Include a clear list of all parts used in the project, detailing the cost for each based on business cost plus a standard markup for profit (usually between 20% to 50%). Ensure to detail parts in a manner that aligns with warranty or return policies that might affect final pricing. \n\n3. **Rates Variation:** Clearly specify if different services or clients are subject to different rates. Highlight the basis for rate variation, whether it be complexity, urgency, or expertise required. \n\n4. **Taxes:** Apply the correct tax rates for services and physical goods as per the local jurisdiction laws. It's critical to understand that services may or may not be taxable, and different items can have varied tax rates. The invoice should clearly itemize the subtotal, the calculated tax, and the total amount due after tax application. \n\n5. **Charge Breakdown:** Provide a detailed breakdown of all charges on the invoice, including each service, part used, tax applied, and the total cost. This ensures transparency and aids in client trust. \n\n6. **Best Practices:** - Utilize a unique invoice number for each invoice for easy tracking. - Include a detailed description for each line item. - Display business tax identification number where required. - Specify payment terms (due date, accepted payment methods). - Use professional formatting that matches your brand. - Consider invoicing software for efficient processing. \n\nThis approach not only enhances the professionalism of your invoices but also ensures compliance and accuracy, facilitating a smoother billing process.",
)


@app.get(
    "/payment/verify/{transactionId}",
    response_model=project.verify_payment_service.VerifyPaymentResponse,
)
async def api_get_verify_payment(
    transactionId: str,
) -> project.verify_payment_service.VerifyPaymentResponse | Response:
    """
    Verifies the status of a payment transaction.
    """
    try:
        res = await project.verify_payment_service.verify_payment(transactionId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/profile/update",
    response_model=project.update_profile_service.UserProfileUpdateResponse,
)
async def api_put_update_profile(
    firstName: Optional[str],
    lastName: Optional[str],
    companyName: Optional[str],
    address: Optional[str],
    taxId: Optional[str],
) -> project.update_profile_service.UserProfileUpdateResponse | Response:
    """
    Updates user's profile information.
    """
    try:
        res = await project.update_profile_service.update_profile(
            firstName, lastName, companyName, address, taxId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/payment/initiate",
    response_model=project.initiate_payment_service.InitiatePaymentResponse,
)
async def api_post_initiate_payment(
    invoice_id: str, user_id: str, payment_method: str, amount: float, currency: str
) -> project.initiate_payment_service.InitiatePaymentResponse | Response:
    """
    Initiates the payment process for an invoice.
    """
    try:
        res = await project.initiate_payment_service.initiate_payment(
            invoice_id, user_id, payment_method, amount, currency
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/register", response_model=project.register_user_service.UserRegistrationResponse
)
async def api_post_register_user(
    email: str,
    password: str,
    first_name: Optional[str],
    last_name: Optional[str],
    company_name: Optional[str],
    address: Optional[str],
    tax_id: Optional[str],
) -> project.register_user_service.UserRegistrationResponse | Response:
    """
    Registers a new user.
    """
    try:
        res = await project.register_user_service.register_user(
            email, password, first_name, last_name, company_name, address, tax_id
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/invoice/{id}/update",
    response_model=project.update_invoice_service.InvoiceUpdateResponse,
)
async def api_put_update_invoice(
    id: str,
    services: List[project.update_invoice_service.ServiceUpdate],
    parts: List[project.update_invoice_service.PartUpdate],
    tax_rate_id: str,
    subtotal: float,
    total: float,
) -> project.update_invoice_service.InvoiceUpdateResponse | Response:
    """
    Updates details of an existing invoice.
    """
    try:
        res = await project.update_invoice_service.update_invoice(
            id, services, parts, tax_rate_id, subtotal, total
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/invoice/create", response_model=project.create_invoice_service.CreateInvoiceOutput
)
async def api_post_create_invoice(
    userId: str,
    services: List[project.create_invoice_service.ServiceDetail],
    parts: List[project.create_invoice_service.PartDetail],
    taxRateId: str,
    dueDate: str,
) -> project.create_invoice_service.CreateInvoiceOutput | Response:
    """
    Creates a new invoice based on input parameters.
    """
    try:
        res = await project.create_invoice_service.create_invoice(
            userId, services, parts, taxRateId, dueDate
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/login", response_model=project.login_user_service.LoginUserOutput)
async def api_post_login_user(
    password: str, email: str
) -> project.login_user_service.LoginUserOutput | Response:
    """
    Authenticates user and returns a token.
    """
    try:
        res = await project.login_user_service.login_user(password, email)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
