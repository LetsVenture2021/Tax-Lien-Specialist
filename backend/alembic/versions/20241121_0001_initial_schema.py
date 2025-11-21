"""Initial domain schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "20241121_0001"
down_revision = None
branch_labels = None
depends_on = None


USER_ROLE = sa.Enum("investor", "admin", "analyst", name="user_role")
STRATEGY_TYPE = sa.Enum("yield", "equity", "balanced", name="strategy_type")
COUNTY_AUCTION_TYPE = sa.Enum("tax_lien", "tax_deed", "hybrid", name="county_auction_type")
AUCTION_SALE_TYPE = sa.Enum("in_person", "online", "hybrid", name="auction_sale_type")
PROPERTY_TYPE = sa.Enum(
    "sfh", "mfh", "land", "commercial", "industrial", "mixed_use", "other", name="property_type"
)
LIEN_TYPE = sa.Enum("tax_lien", "tax_deed", "other", name="lien_type")
INTEREST_TYPE = sa.Enum("simple", "penalty", "compound", "stepped", name="interest_type")
LIEN_STATUS = sa.Enum("available", "sold", "redeemed", "foreclosed", "canceled", name="lien_status")
ANALYSIS_TYPE = sa.Enum(
    "county_batch", "portfolio_rebalance", "single_lien", "watchlist_refresh", name="analysis_type"
)
ANALYSIS_STATUS = sa.Enum("pending", "running", "completed", "failed", name="analysis_status")
SCENARIO_TYPE = sa.Enum("redemption", "deed_conversion", "assignment_resell", name="scenario_type")
PORTFOLIO_HOLDING_STATUS = sa.Enum(
    "held", "redeemed", "foreclosed", "sold_assignment", "written_off", name="portfolio_holding_status"
)
AGENT_TYPE = sa.Enum("orchestrator", "research", "underwriting", "document", name="agent_type")
AGENT_TASK_STATUS = sa.Enum("pending", "in_progress", "completed", "failed", name="agent_task_status")
AGENT_LOG_TYPE = sa.Enum("plan", "step", "error", "summary", name="agent_log_type")
DOCUMENT_TYPE = sa.Enum(
    "investor_summary", "promissory_note", "foreclosure_packet", "portfolio_report", "other", name="document_type"
)
NOTIFICATION_TYPE = sa.Enum("general", "workflow", "portfolio", "alert", name="notification_type")
INTEGRATION_SOURCE = sa.Enum("county", "mls", "gis", "auction_platform", "other", name="integration_source")
INTEGRATION_STATUS = sa.Enum("success", "failed", name="integration_status")


TIMESTAMP_DEFAULT = sa.text("CURRENT_TIMESTAMP")
UUID_COLUMN = lambda: sa.Column(
    "id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
)


def upgrade() -> None:
    bind = op.get_bind()
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    for enum_type in (
        USER_ROLE,
        STRATEGY_TYPE,
        COUNTY_AUCTION_TYPE,
        AUCTION_SALE_TYPE,
        PROPERTY_TYPE,
        LIEN_TYPE,
        INTEREST_TYPE,
        LIEN_STATUS,
        ANALYSIS_TYPE,
        ANALYSIS_STATUS,
        SCENARIO_TYPE,
        PORTFOLIO_HOLDING_STATUS,
        AGENT_TYPE,
        AGENT_TASK_STATUS,
        AGENT_LOG_TYPE,
        DOCUMENT_TYPE,
        NOTIFICATION_TYPE,
        INTEGRATION_SOURCE,
        INTEGRATION_STATUS,
    ):
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "users",
        UUID_COLUMN(),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", USER_ROLE, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
    )

    op.create_table(
        "investor_profiles",
        UUID_COLUMN(),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("investment_budget_total", sa.Numeric(18, 2), nullable=False),
        sa.Column("min_target_yield", sa.Numeric(5, 2)),
        sa.Column("max_risk_score", sa.Numeric(5, 2)),
        sa.Column("preferred_states", postgresql.ARRAY(sa.String(length=2))),
        sa.Column("time_horizon_months", sa.Integer()),
        sa.Column("strategy_type", STRATEGY_TYPE, nullable=False),
    )

    op.create_table(
        "counties",
        UUID_COLUMN(),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
        sa.Column("state_code", sa.String(length=2), nullable=False),
        sa.Column("county_name", sa.String(length=255), nullable=False),
        sa.Column("auction_type", COUNTY_AUCTION_TYPE, nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("data_source_url", sa.String(length=512)),
    )

    op.create_table(
        "properties",
        UUID_COLUMN(),
        sa.Column("county_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("counties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("apn", sa.String(length=128), nullable=False),
        sa.Column("street_address", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
        sa.Column("zip_code", sa.String(length=10), nullable=False),
        sa.Column("lat", sa.Float()),
        sa.Column("lng", sa.Float()),
        sa.Column("property_type", PROPERTY_TYPE, nullable=False),
        sa.Column("land_sqft", sa.Integer()),
        sa.Column("building_sqft", sa.Integer()),
        sa.Column("year_built", sa.Integer()),
        sa.Column("zoning", sa.String(length=120)),
        sa.Column("last_updated_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "auctions",
        UUID_COLUMN(),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
        sa.Column("county_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("counties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("auction_name", sa.String(length=255), nullable=False),
        sa.Column("auction_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("auction_type", AUCTION_SALE_TYPE, nullable=False),
        sa.Column("source_url", sa.String(length=512)),
        sa.Column("status", sa.String(length=32), nullable=False),
    )

    op.create_table(
        "liens",
        UUID_COLUMN(),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("auction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auctions.id", ondelete="SET NULL")),
        sa.Column("lien_certificate_number", sa.String(length=128), nullable=False),
        sa.Column("lien_type", LIEN_TYPE, nullable=False),
        sa.Column("lien_principal_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("interest_rate_nominal", sa.Numeric(5, 2), nullable=False),
        sa.Column("interest_type", INTEREST_TYPE, nullable=False),
        sa.Column("redemption_period_months", sa.Integer(), nullable=False),
        sa.Column("issue_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("redemption_deadline", sa.DateTime(timezone=True)),
        sa.Column("status", LIEN_STATUS, nullable=False),
        sa.Column("current_holder", sa.String(length=255)),
    )

    op.create_table(
        "property_valuations",
        UUID_COLUMN(),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("valuation_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("avm_value", sa.Numeric(18, 2)),
        sa.Column("low_value", sa.Numeric(18, 2)),
        sa.Column("high_value", sa.Numeric(18, 2)),
        sa.Column("valuation_source", sa.String(length=64)),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
    )

    op.create_table(
        "property_comps",
        UUID_COLUMN(),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("comp_property_address", sa.String(length=255), nullable=False),
        sa.Column("comp_sale_price", sa.Numeric(18, 2)),
        sa.Column("comp_sale_date", sa.DateTime(timezone=True)),
        sa.Column("distance_miles", sa.Float()),
        sa.Column("similarity_score", sa.Float()),
        sa.Column("source", sa.String(length=120)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
    )

    op.create_table(
        "analysis_runs",
        UUID_COLUMN(),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
        sa.Column("investor_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("investor_profiles.id", ondelete="SET NULL")),
        sa.Column("initiated_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("analysis_type", ANALYSIS_TYPE, nullable=False),
        sa.Column("target_county_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("counties.id", ondelete="SET NULL")),
        sa.Column("status", ANALYSIS_STATUS, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text()),
    )

    op.create_table(
        "deal_metrics",
        UUID_COLUMN(),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lien_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("liens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("valuation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("property_valuations.id", ondelete="SET NULL")),
        sa.Column("lien_to_value_ratio", sa.Numeric(8, 4)),
        sa.Column("estimated_redemption_hold_months", sa.Integer()),
        sa.Column("simple_yield", sa.Numeric(6, 3)),
        sa.Column("annualized_yield", sa.Numeric(6, 3)),
        sa.Column("cash_on_cash_return", sa.Numeric(6, 3)),
        sa.Column("irr_redemption_scenario", sa.Numeric(6, 3)),
        sa.Column("irr_deed_scenario", sa.Numeric(6, 3)),
        sa.Column("expected_value_overall", sa.Numeric(18, 2)),
        sa.Column("liquidity_score", sa.Numeric(6, 3)),
    )

    op.create_table(
        "risk_assessments",
        UUID_COLUMN(),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lien_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("liens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title_risk_score", sa.Float()),
        sa.Column("structural_risk_score", sa.Float()),
        sa.Column("neighborhood_risk_score", sa.Float()),
        sa.Column("vacancy_risk_score", sa.Float()),
        sa.Column("legal_complexity_risk_score", sa.Float()),
        sa.Column("overall_risk_score", sa.Float()),
        sa.Column("risk_flags", postgresql.JSONB()),
    )

    op.create_table(
        "scenario_analyses",
        UUID_COLUMN(),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lien_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("liens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario_type", SCENARIO_TYPE, nullable=False),
        sa.Column("probability", sa.Float()),
        sa.Column("projected_profit", sa.Numeric(18, 2)),
        sa.Column("projected_roi", sa.Numeric(6, 3)),
        sa.Column("projected_irr", sa.Numeric(6, 3)),
        sa.Column("holding_period_months", sa.Integer()),
        sa.Column("total_capital_required", sa.Numeric(18, 2)),
        sa.Column("notes", sa.Text()),
    )

    op.create_table(
        "deal_scores",
        UUID_COLUMN(),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("investor_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("investor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lien_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("liens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("composite_score", sa.Float()),
        sa.Column("yield_score", sa.Float()),
        sa.Column("risk_adjusted_return_score", sa.Float()),
        sa.Column("liquidity_score", sa.Float()),
        sa.Column("strategy_fit_score", sa.Float()),
        sa.Column("rank_within_run", sa.Integer()),
    )

    op.create_table(
        "portfolios",
        UUID_COLUMN(),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
        sa.Column("investor_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("investor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=512)),
    )

    op.create_table(
        "portfolio_holdings",
        UUID_COLUMN(),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lien_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("liens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("acquisition_date", sa.DateTime(timezone=True)),
        sa.Column("acquisition_price", sa.Numeric(18, 2)),
        sa.Column("current_status", PORTFOLIO_HOLDING_STATUS, nullable=False),
        sa.Column("redemption_amount_received", sa.Numeric(18, 2)),
        sa.Column("foreclosure_date", sa.DateTime(timezone=True)),
        sa.Column("disposition_date", sa.DateTime(timezone=True)),
        sa.Column("disposition_proceeds", sa.Numeric(18, 2)),
    )

    op.create_table(
        "agent_tasks",
        UUID_COLUMN(),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_runs.id", ondelete="SET NULL")),
        sa.Column("parent_task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agent_tasks.id", ondelete="SET NULL")),
        sa.Column("agent_type", AGENT_TYPE, nullable=False),
        sa.Column("task_name", sa.String(length=255), nullable=False),
        sa.Column("status", AGENT_TASK_STATUS, nullable=False),
        sa.Column("input_payload", postgresql.JSONB()),
        sa.Column("output_payload", postgresql.JSONB()),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "agent_logs",
        UUID_COLUMN(),
        sa.Column("agent_task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agent_tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("log_type", AGENT_LOG_TYPE, nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
    )

    op.create_table(
        "documents",
        UUID_COLUMN(),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=TIMESTAMP_DEFAULT),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("portfolios.id", ondelete="SET NULL")),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_runs.id", ondelete="SET NULL")),
        sa.Column("lien_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("liens.id", ondelete="SET NULL")),
        sa.Column("document_type", DOCUMENT_TYPE, nullable=False),
        sa.Column("storage_url", sa.String(length=512), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("generated_by_agent_task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agent_tasks.id", ondelete="SET NULL")),
    )

    op.create_table(
        "notifications",
        UUID_COLUMN(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notification_type", NOTIFICATION_TYPE, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB()),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
        sa.Column("read_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "embeddings",
        UUID_COLUMN(),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("embedding_vector", Vector(1536), nullable=False),
        sa.Column("model_name", sa.String(length=120)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
    )

    op.create_table(
        "integration_events",
        UUID_COLUMN(),
        sa.Column("source_system", INTEGRATION_SOURCE, nullable=False),
        sa.Column("request_payload", postgresql.JSONB()),
        sa.Column("response_payload", postgresql.JSONB()),
        sa.Column("status", INTEGRATION_STATUS, nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "audit_logs",
        UUID_COLUMN(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=TIMESTAMP_DEFAULT),
    )


def downgrade() -> None:
    for table in (
        "audit_logs",
        "integration_events",
        "embeddings",
        "notifications",
        "documents",
        "agent_logs",
        "agent_tasks",
        "portfolio_holdings",
        "portfolios",
        "deal_scores",
        "scenario_analyses",
        "risk_assessments",
        "deal_metrics",
        "analysis_runs",
        "property_comps",
        "property_valuations",
        "liens",
        "auctions",
        "properties",
        "counties",
        "investor_profiles",
        "users",
    ):
        op.drop_table(table)

    for enum_type in (
        INTEGRATION_STATUS,
        INTEGRATION_SOURCE,
        NOTIFICATION_TYPE,
        DOCUMENT_TYPE,
        AGENT_LOG_TYPE,
        AGENT_TASK_STATUS,
        AGENT_TYPE,
        PORTFOLIO_HOLDING_STATUS,
        SCENARIO_TYPE,
        ANALYSIS_STATUS,
        ANALYSIS_TYPE,
        LIEN_STATUS,
        INTEREST_TYPE,
        LIEN_TYPE,
        PROPERTY_TYPE,
        AUCTION_SALE_TYPE,
        COUNTY_AUCTION_TYPE,
        STRATEGY_TYPE,
        USER_ROLE,
    ):
        enum_type.drop(op.get_bind(), checkfirst=True)
