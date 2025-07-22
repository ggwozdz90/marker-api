from fastapi import APIRouter

from api.dtos.health_check_response_dto import HealthCheckResponseDto


class HealthCheckRouter:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.get("/healthcheck")(self.healthcheck)

    async def healthcheck(self) -> HealthCheckResponseDto:
        return HealthCheckResponseDto(status="OK")
