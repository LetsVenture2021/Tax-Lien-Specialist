"""API v1 router assembling domain specific route modules."""

from fastapi import APIRouter

from app.api.v1 import ai


router = APIRouter()
router.include_router(ai.router)

# Pending: include domain routers (auth, investors, properties, liens, analysis, portfolios, documents,
# notifications, agents, reasoning explorer) once implemented.
