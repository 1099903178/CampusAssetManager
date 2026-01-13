"""
CampusAssetManager/backend/app/middleware/operation_log.py
操作日志记录中间件

功能说明：
- 自动记录API请求和响应到操作日志
- 记录用户、操作类型、模块、请求参数、结果等信息
- 支持配置哪些接口需要记录日志

设计原则：
- 声明式：使用FastAPI中间件机制
- 配置化：通过配置决定哪些接口需要记录日志
- 异步处理：不阻塞主请求流程

作者：CampusAssetManager开发团队
日期：2026-01-10
"""

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session
from typing import Optional, Callable, Any
import json
import time

from ..database.config import SessionLocal, get_db
from ..services.system_service import operation_log_service
from ..services.auth_service import AuthService
from ..core.security import decode_access_token

# 创建认证服务实例（用于查询用户信息）
auth_service_for_log = AuthService()


class OperationLogMiddleware(BaseHTTPMiddleware):
    """
    操作日志记录中间件
    
    自动记录API请求和响应信息到操作日志表
    """
    
    # 需要记录日志的路径模式
    LOGGED_PATHS = [
        "/v1/auth/login",           # 登录
        "/v1/goods",                # 物品管理
        "/v1/stock/in",             # 入库
        "/v1/stock/out",            # 出库
        "/v1/stock/check",          # 盘点
        "/v1/users",                # 用户管理
        "/v1/system/config",        # 系统配置
    ]
    
    # 不需要记录日志的路径模式（可选）
    EXCLUDED_PATHS = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    
    def __init__(self, app: ASGIApp) -> None:
        """
        初始化中间件
        
        Args:
            app (ASGIApp): ASGI应用实例
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录日志
        
        Args:
            request (Request): 请求对象
            call_next (Callable): 下一个中间件处理函数
        
        Returns:
            Response: 响应对象
        """
        # 获取请求路径
        path = request.url.path
        
        # 检查是否需要记录日志
        if not self._should_log(path):
            return await call_next(request)
        
        # 记录开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        
        # 获取用户信息
        user_id = None
        username = "anonymous"
        
        try:
            # 从Authorization header获取token
            auth_header = request.headers.get("authorization", "")
            
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                
                payload = decode_access_token(token)
                
                # 从token提取用户名
                username = payload.get("username", payload.get("sub", "anonymous"))
                
                # 查询数据库获取真实的user_id
                db: Session = SessionLocal()
                try:
                    user = auth_service_for_log.get_user_by_username(username, db)
                    if user:
                        user_id = user.user_id
                        username = user.username
                finally:
                    db.close()
        except Exception:
            pass
        
        # 获取请求体（仅POST/PUT等有请求体的方法）
        params = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                # 读取请求体
                body_bytes = await request.body()
                if body_bytes:
                    body_str = body_bytes.decode("utf-8")
                    # 尝试解析JSON
                    try:
                        body_json = json.loads(body_str)
                        # 过滤敏感信息（如密码）
                        body_json = self._filter_sensitive_data(body_json)
                        params = json.dumps(body_json, ensure_ascii=False)
                    except json.JSONDecodeError:
                        params = body_str[:500]  # 限制长度
            except Exception:
                params = None
        
        # 执行请求
        response: Optional[Response] = None
        log_operation = "unknown"
        log_module = "unknown"
        log_result = "failed"
        log_error = None
        
        try:
            # 调用下一个中间件
            response = await call_next(request)
            
            # 判断操作是否成功
            if 200 <= response.status_code < 300:
                log_result = "success"
            else:
                log_result = "failed"
            
            # 根据路径判断操作类型和模块
            log_operation, log_module = self._parse_operation_and_module(path, method)
            
        except Exception as e:
            # 处理异常
            log_result = "failed"
            log_error = str(e)
            
            # 创建错误响应
            response = Response(
                content=json.dumps({"error": str(e)}),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/json"
            )
        
        # 记录操作日志
        try:
            # 获取数据库会话
            db_gen = get_db()
            db: Session = next(db_gen)
            
            # 异步记录日志（不阻塞主流程）
            operation_log_service.create_log(
                user_id=user_id or 0,
                username=username,
                operation=log_operation,
                module=log_module,
                method=method,
                url=path,
                params=params,
                result=log_result,
                error_message=log_error,
                ip_address=client_host,
                user_agent=user_agent,
                db=db
            )
            
            # 关闭数据库会话
            db_gen.close()
        except Exception:
            # 记录日志失败不影响主流程
            pass
        
        # 记录处理时间
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _should_log(self, path: str) -> bool:
        """
        判断是否需要记录日志
        
        Args:
            path (str): 请求路径
        
        Returns:
            bool: 是否需要记录
        """
        # 检查排除的路径
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return False
        
        # 检查需要记录的路径
        for logged in self.LOGGED_PATHS:
            if path.startswith(logged):
                return True
        
        return False
    
    def _parse_operation_and_module(
        self,
        path: str,
        method: str
    ) -> tuple[str, str]:
        """
        根据路径和HTTP方法解析操作类型和模块
        
        Args:
            path (str): 请求路径
            method (str): HTTP方法
        
        Returns:
            tuple: (operation, module)
        """
        # 登录
        if "/auth/login" in path:
            return "login", "auth"
        
        # 物品管理
        if "/goods" in path:
            if method == "POST":
                return "create", "goods"
            elif method == "PUT":
                return "update", "goods"
            elif method == "DELETE":
                return "delete", "goods"
            else:
                return "query", "goods"
        
        # 入库
        if "/stock/in" in path and method == "POST":
            return "stock_in", "stock"
        
        # 出库
        if "/stock/out" in path and method == "POST":
            return "stock_out", "stock"
        
        # 盘点
        if "/stock/check" in path:
            if method == "POST":
                return "check", "stock"
            else:
                return "query_check", "stock"
        
        # 用户管理
        if "/users" in path:
            if method == "POST":
                return "create_user", "user"
            elif method == "PUT":
                return "update_user", "user"
            elif method == "DELETE":
                return "delete_user", "user"
            else:
                return "query_user", "user"
        
        # 系统配置
        if "/system/config" in path:
            if method == "PUT":
                return "update_config", "system"
            else:
                return "query_config", "system"
        
        # 默认
        return "api_request", "system"
    
    def _filter_sensitive_data(self, data: dict) -> dict:
        """
        过滤敏感数据（如密码）
        
        Args:
            data (dict): 原始数据
        
        Returns:
            dict: 过滤后的数据
        """
        if not isinstance(data, dict):
            return data
        
        # 需要过滤的字段
        sensitive_fields = [
            "password",
            "password_hash",
            "token",
            "secret",
            "access_token",
            "refresh_token"
        ]
        
        # 创建数据副本
        filtered_data = data.copy()
        
        # 过滤敏感字段
        for field in sensitive_fields:
            if field in filtered_data:
                filtered_data[field] = "******"
        
        return filtered_data