from app.models.onboarding import OnboardingInfo
from app.repositories.base import BaseRepository


class OnboardingRepository(BaseRepository[OnboardingInfo]):
    """Repositorio específico para Onboarding."""
    pass

onboarding_repo = OnboardingRepository(OnboardingInfo)
