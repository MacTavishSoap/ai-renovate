"""业务异常定义"""

from fastapi import HTTPException, status


class AppException(HTTPException):
    """业务异常基类"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppException):
    """资源不存在"""
    def __init__(self, resource: str = "资源"):
        super().__init__(detail=f"{resource}不存在", status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(AppException):
    """校验失败"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
