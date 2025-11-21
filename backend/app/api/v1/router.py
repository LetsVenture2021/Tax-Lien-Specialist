"""API v1 router assembling domain specific route modules."""

from fastapi import APIRouter


router = APIRouter()

# TODO: include domain routers (auth, investors, properties, liens, analysis, portfolios, documents,
# notifications, agents, reasoning explorer) once implemented.
