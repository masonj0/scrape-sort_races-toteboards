#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: Logging Configuration
# ==============================================================================
# This module, restored by the Great Correction, provides a centralized
# configuration for structured logging using structlog.
# ==============================================================================

import logging
import sys
import structlog

def configure_logging():
    """Configures structlog for JSON-based structured logging."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )