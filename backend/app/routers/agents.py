
import asyncio
import importlib
import json
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable, Mapping
from typing import Annotated, Protocol, TypedDict, cast

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..dependencies import get_current_user
from ..database import AsyncSessionLocal
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_MODELS = frozenset({"gpt-4o-mini", "gpt-4o"})


class SearchChunks(Protocol):
    async def __call__(
        self,
        query: str,
        db: AsyncSession,
        *,
        limit: int,
    ) -> object: ...


def _resolve_search_relevant_chunks() -> SearchChunks | None:
    """Resolve the RAG service without an unresolved static import."""
    try:
        module = importlib.import_module("..services.ai_service", package=__package__)
    except ImportError:
        logger.exception("Could not import the AI service module")
        return None

    candidate = getattr(module, "search_relevant_chunks", None)

    if not callable(candidate):
        logger.error(
            "search_relevant_chunks is missing from "
            "the app.services.ai_service module"
        )
        return None

    return cast(SearchChunks, candidate)


search_relevant_chunks = _resolve_search_relevant_chunks()
