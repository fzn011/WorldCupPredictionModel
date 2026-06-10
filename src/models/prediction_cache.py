"""Cached match prediction utilities for tournament simulation flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.models.predict_match import predict_future_match
import src.utils.constants as C

DEFAULT_FUTURE_TOURNAMENT = getattr(C, "DEFAULT_FUTURE_TOURNAMENT", "FIFA World Cup")
DEFAULT_FUTURE_CITY = getattr(C, "DEFAULT_FUTURE_CITY", "Unknown")
DEFAULT_FUTURE_COUNTRY = getattr(C, "DEFAULT_FUTURE_COUNTRY", "Unknown")
DEFAULT_FUTURE_NEUTRAL = int(getattr(C, "DEFAULT_FUTURE_NEUTRAL", 1))


@dataclass
class CachedMatchPredictor:
    """In-memory cache wrapper around ``predict_future_match``."""

    _cache: dict[tuple[str, str, str, str, str, str, int], dict[str, Any]] = field(default_factory=dict)
    _total_requests: int = 0
    _cache_hits: int = 0
    _cache_misses: int = 0

    def make_key(
        self,
        team_a: str,
        team_b: str,
        match_date: str,
        tournament: str,
        city: str,
        country: str,
        neutral: int,
    ) -> tuple[str, str, str, str, str, str, int]:
        """Create an order-sensitive cache key for a match prediction."""
        return (
            str(team_a),
            str(team_b),
            str(match_date),
            str(tournament),
            str(city),
            str(country),
            int(neutral),
        )

    def predict(
        self,
        team_a: str,
        team_b: str,
        match_date: str,
        tournament: str = DEFAULT_FUTURE_TOURNAMENT,
        city: str = DEFAULT_FUTURE_CITY,
        country: str = DEFAULT_FUTURE_COUNTRY,
        neutral: int = DEFAULT_FUTURE_NEUTRAL,
    ) -> dict[str, Any]:
        """Predict match probabilities using cache on repeated requests."""
        self._total_requests += 1

        key = self.make_key(
            team_a=team_a,
            team_b=team_b,
            match_date=match_date,
            tournament=tournament,
            city=city,
            country=country,
            neutral=neutral,
        )

        if key in self._cache:
            self._cache_hits += 1
            return self._cache[key]

        self._cache_misses += 1
        result = predict_future_match(
            team_a=team_a,
            team_b=team_b,
            match_date=match_date,
            tournament=tournament,
            city=city,
            country=country,
            neutral=int(neutral),
        )
        self._cache[key] = result
        return result

    def cache_info(self) -> dict[str, int]:
        """Return cache usage statistics."""
        return {
            "total_requests": int(self._total_requests),
            "cache_hits": int(self._cache_hits),
            "cache_misses": int(self._cache_misses),
            "cache_size": int(len(self._cache)),
        }


_GLOBAL_CACHED_PREDICTOR: CachedMatchPredictor | None = None


def get_global_cached_predictor() -> CachedMatchPredictor:
    """Return a lazily-created process-global cached predictor instance."""
    global _GLOBAL_CACHED_PREDICTOR
    if _GLOBAL_CACHED_PREDICTOR is None:
        _GLOBAL_CACHED_PREDICTOR = CachedMatchPredictor()
    return _GLOBAL_CACHED_PREDICTOR
