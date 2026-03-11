from app.repositories.base import BaseRepository
from app.models.onboarding import OnboardingInfo

class OnboardingRepository(BaseRepository[OnboardingInfo]):
    """Repositorio específico para Onboarding."""
    pass

onboarding_repo = OnboardingRepository(OnboardingInfo)
