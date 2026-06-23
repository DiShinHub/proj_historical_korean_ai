from pydantic import BaseModel, Field


class ResultVo(BaseModel):
    success: bool = Field(default=True, description="Result")
    message: str | None = Field(default=None, description="Result Message")
    data: dict | None = Field(default=None, description="Result Data")

    class Config:
        frozen = True


class ResultExceptionVo(ResultVo):
    success: bool = Field(default=False, description="Result")
    message: str | None = Field(default=None, description="Cause Of Exception")

    class Config:
        frozen = True
