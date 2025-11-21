"""Geographic and property domain models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import AuctionSaleType, CountyAuctionType, PropertyType
from app.models.mixins import BaseModel, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover
    from app.models.analysis import AnalysisRun
    from app.models.lien import Lien


class County(TimestampMixin, BaseModel):
    __tablename__ = "counties"

    state_code: Mapped[str] = mapped_column(String(2), nullable=False)
    county_name: Mapped[str] = mapped_column(String(255), nullable=False)
    auction_type: Mapped[CountyAuctionType] = mapped_column(
        Enum(CountyAuctionType, name="county_auction_type"), nullable=False
    )
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    data_source_url: Mapped[Optional[str]] = mapped_column(String(512))

    properties: Mapped[list["Property"]] = relationship(back_populates="county")
    auctions: Mapped[list["Auction"]] = relationship(back_populates="county")
    analysis_runs: Mapped[list["AnalysisRun"]] = relationship(back_populates="target_county")


class Property(BaseModel):
    __tablename__ = "properties"

    county_id: Mapped[PyUUID] = mapped_column(ForeignKey("counties.id", ondelete="CASCADE"), nullable=False)
    apn: Mapped[str] = mapped_column(String(128), nullable=False)
    street_address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False)
    lat: Mapped[Optional[float]] = mapped_column(Float)
    lng: Mapped[Optional[float]] = mapped_column(Float)
    property_type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType, name="property_type"), nullable=False
    )
    land_sqft: Mapped[Optional[int]] = mapped_column(Integer)
    building_sqft: Mapped[Optional[int]] = mapped_column(Integer)
    year_built: Mapped[Optional[int]] = mapped_column(Integer)
    zoning: Mapped[Optional[str]] = mapped_column(String(120))
    last_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    county: Mapped[County] = relationship(back_populates="properties")
    liens: Mapped[list["Lien"]] = relationship(back_populates="property")
    valuations: Mapped[list["PropertyValuation"]] = relationship(back_populates="property")
    comps: Mapped[list["PropertyComp"]] = relationship(back_populates="property")


class Auction(TimestampMixin, BaseModel):
    __tablename__ = "auctions"

    county_id: Mapped[PyUUID] = mapped_column(ForeignKey("counties.id", ondelete="CASCADE"), nullable=False)
    auction_name: Mapped[str] = mapped_column(String(255), nullable=False)
    auction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    auction_type: Mapped[AuctionSaleType] = mapped_column(
        Enum(AuctionSaleType, name="auction_sale_type"), nullable=False
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    county: Mapped[County] = relationship(back_populates="auctions")
    liens: Mapped[list["Lien"]] = relationship(back_populates="auction")


class PropertyValuation(BaseModel):
    __tablename__ = "property_valuations"

    property_id: Mapped[PyUUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    valuation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    avm_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    low_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    high_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    valuation_source: Mapped[Optional[str]] = mapped_column(String(64))
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)

    property: Mapped[Property] = relationship(back_populates="valuations")


class PropertyComp(BaseModel):
    __tablename__ = "property_comps"

    property_id: Mapped[PyUUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    comp_property_address: Mapped[str] = mapped_column(String(255), nullable=False)
    comp_sale_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    comp_sale_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    distance_miles: Mapped[Optional[float]] = mapped_column(Float)
    similarity_score: Mapped[Optional[float]] = mapped_column(Float)
    source: Mapped[Optional[str]] = mapped_column(String(120))

    property: Mapped[Property] = relationship(back_populates="comps")
