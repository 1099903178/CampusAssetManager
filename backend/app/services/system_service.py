"""
CampusAssetManager/backend/app/services/system_service.py
系统服务模块

功能说明：
- 操作日志记录和查询
- 系统配置管理
- 配置初始化和批量更新

设计原则：
- 面向对象：使用Service类封装业务逻辑
- 声明式：使用Pydantic定义数据模型
- 封装清晰：提供简洁的公共方法

作者：CampusAssetManager开发团队
日期：2026-01-10
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_, text
import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from app.models.sys_operation_log import OperationLog
from app.models.sys_config import Config
from app.models.goods_info import Goods
from app.models.goods_category import GoodsCategory
from app.models.stock_info import Stock
from app.models.stock_in import StockIn
from app.models.stock_out import StockOut
from app.models.stock_check import StockCheck
from app.schemas.system import (
    OperationLogResponse,
    OperationLogQuery,
    ConfigResponse,
    ConfigUpdate,
    ConfigBatchUpdate,
    SystemConfigGroup,
    SystemConfigResponse,
    SystemResetRequest,
    PREDEFINED_CONFIGS,
    BackupFileResponse,
    BackupListResponse,
    BackupCreateResponse,
    RestoreResponse,
    RestoreRequest
)
from app.core.security import verify_password


class OperationLogService:
    """
    操作日志服务类
    
    负责操作日志的记录和查询功能
    """
    
    def create_log(
        self,
        user_id: int,
        username: str,
        operation: str,
        module: str = "system",
        method: str = "GET",
        url: Optional[str] = None,
        params: Optional[str] = None,
        result: str = "success",
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        db: Session = None
    ) -> OperationLogResponse:
        """
        创建操作日志记录
        
        Args:
            user_id (int): 操作人ID
            username (str): 操作人用户名
            operation (str): 操作类型（login/create/update/delete等）
            module (str): 操作模块（auth/goods/stock等）
            method (str): 请求方法（GET/POST/PUT/DELETE）
            url (str): 请求URL
            params (str): 请求参数
            result (str): 操作结果（success/failed）
            error_message (str): 错误信息
            ip_address (str): IP地址
            user_agent (str): 用户代理
            db (Session): 数据库会话
        
        Returns:
            OperationLogResponse: 创建的操作日志记录
        
        Raises:
            ValueError: 数据验证失败
        """
        if not db:
            raise ValueError("数据库会话不能为空")
        
        try:
            # 创建操作日志记录
            log = OperationLog(
                user_id=user_id,
                username=username,
                operation=operation,
                module=module,
                method=method,
                url=url,
                params=params,
                result=result,
                error_message=error_message,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # 保存到数据库
            db.add(log)
            db.commit()
            db.refresh(log)
            
            # 转换为响应模型
            return OperationLogResponse.model_validate(log)
        except Exception as e:
            db.rollback()
            raise ValueError(f"创建操作日志失败: {str(e)}")
    
    def get_logs(
        self,
        query: OperationLogQuery,
        db: Session
    ) -> Dict[str, Any]:
        """
        查询操作日志列表（支持分页和筛选）
        
        Args:
            query (OperationLogQuery): 查询参数
            db (Session): 数据库会话
        
        Returns:
            dict: 包含日志列表和分页信息的字典
        
        Raises:
            ValueError: 查询失败
        """
        try:
            # 构建基础查询
            db_query = db.query(OperationLog)
            
            # 按用户名筛选
            if query.username:
                db_query = db_query.filter(
                    OperationLog.username.like(f"%{query.username}%")
                )
            
            # 按操作类型筛选
            if query.operation:
                db_query = db_query.filter(
                    OperationLog.operation == query.operation
                )
            
            # 按模块筛选
            if query.module:
                db_query = db_query.filter(
                    OperationLog.module == query.module
                )
            
            # 按结果筛选
            if query.result:
                db_query = db_query.filter(
                    OperationLog.result == query.result
                )
            
            # 按时间范围筛选
            if query.start_date:
                db_query = db_query.filter(
                    OperationLog.create_time >= query.start_date
                )
            
            if query.end_date:
                db_query = db_query.filter(
                    OperationLog.create_time <= query.end_date
                )
            
            # 按创建时间倒序排序
            db_query = db_query.order_by(desc(OperationLog.create_time))
            
            # 查询总数
            total = db_query.count()
            
            # 分页查询
            offset = (query.page - 1) * query.page_size
            logs = db_query.offset(offset).limit(query.page_size).all()
            
            # 转换为响应模型
            log_list = [OperationLogResponse.model_validate(log) for log in logs]
            
            return {
                "items": log_list,
                "total": total,
                "page": query.page,
                "page_size": query.page_size
            }
        except Exception as e:
            raise ValueError(f"查询操作日志失败: {str(e)}")


class ConfigService:
    """
    系统配置服务类
    
    负责系统配置的初始化、查询和更新功能
    """
    
    def initialize_configs(self, db: Session) -> bool:
        """
        初始化系统配置
        
        创建预定义的系统配置项
        
        Args:
            db (Session): 数据库会话
        
        Returns:
            bool: 初始化是否成功
        
        Raises:
            ValueError: 初始化失败
        """
        try:
            for config_data in PREDEFINED_CONFIGS:
                # 检查配置是否已存在
                existing_config = db.query(Config).filter(
                    Config.config_key == config_data["config_key"]
                ).first()
                
                if not existing_config:
                    # 创建新配置
                    config = Config(**config_data)
                    db.add(config)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise ValueError(f"初始化系统配置失败: {str(e)}")
    
    def get_all_configs(self, db: Session) -> Dict[str, Any]:
        """
        获取所有系统配置（按分类分组）
        
        Args:
            db (Session): 数据库会话
        
        Returns:
            dict: 按分类分组的配置列表
        
        Raises:
            ValueError: 查询失败
        """
        try:
            # 查询所有配置
            configs = db.query(Config).order_by(Config.category, Config.config_id).all()
            
            # 按分类分组
            category_map = {
                "system": "系统配置",
                "stock": "库存配置",
                "backup": "备份配置",
                "notification": "通知配置"
            }
            
            groups = {}
            for config in configs:
                category = config.category
                if category not in groups:
                    groups[category] = {
                        "category": category,
                        "category_name": category_map.get(category, category),
                        "configs": []
                    }
                groups[category]["configs"].append(ConfigResponse.model_validate(config))
            
            # 转换为列表
            config_groups = list(groups.values())
            
            return {
                "configs": config_groups
            }
        except Exception as e:
            raise ValueError(f"获取系统配置失败: {str(e)}")
    
    def get_config_by_key(
        self,
        config_key: str,
        db: Session
    ) -> ConfigResponse:
        """
        根据配置键获取单个配置
        
        Args:
            config_key (str): 配置键
            db (Session): 数据库会话
        
        Returns:
            ConfigResponse: 配置信息
        
        Raises:
            ValueError: 配置不存在
        """
        config = db.query(Config).filter(
            Config.config_key == config_key
        ).first()
        
        if not config:
            raise ValueError(f"配置 {config_key} 不存在")
        
        return ConfigResponse.model_validate(config)
    
    def update_config(
        self,
        config_key: str,
        config_value: str,
        db: Session
    ) -> ConfigResponse:
        """
        更新单个系统配置
        
        Args:
            config_key (str): 配置键
            config_value (str): 新的配置值
            db (Session): 数据库会话
        
        Returns:
            ConfigResponse: 更新后的配置信息
        
        Raises:
            ValueError: 配置不存在或更新失败
        """
        try:
            # 查询配置
            config = db.query(Config).filter(
                Config.config_key == config_key
            ).first()
            
            if not config:
                raise ValueError(f"配置 {config_key} 不存在")
            
            # 更新配置值
            config.config_value = config_value
            db.commit()
            db.refresh(config)
            
            return ConfigResponse.model_validate(config)
        except Exception as e:
            db.rollback()
            raise ValueError(f"更新配置失败: {str(e)}")
    
    def batch_update_configs(
        self,
        update_data: ConfigBatchUpdate,
        db: Session
    ) -> List[ConfigResponse]:
        """
        批量更新系统配置
        
        Args:
            update_data (ConfigBatchUpdate): 批量更新数据
            db (Session): 数据库会话
        
        Returns:
            list: 更新后的配置列表
        
        Raises:
            ValueError: 批量更新失败
        """
        try:
            updated_configs = []
            
            for config_item in update_data.configs:
                # 查询并更新配置
                config = db.query(Config).filter(
                    Config.config_key == config_item.config_key
                ).first()
                
                if config:
                    config.config_value = config_item.config_value
                    updated_configs.append(config)
            
            db.commit()
            
            # 刷新所有更新后的配置
            for config in updated_configs:
                db.refresh(config)
            
            return [ConfigResponse.model_validate(config) for config in updated_configs]
        except Exception as e:
            db.rollback()
            raise ValueError(f"批量更新配置失败: {str(e)}")
    
    def reset_system(
        self,
        reset_data: SystemResetRequest,
        db: Session
    ) -> bool:
        """
        系统完全重置
        
        清空所有业务数据、操作日志和配置，并重新初始化默认配置
        记录系统重置操作日志（log_id=1）
        
        Args:
            reset_data (SystemResetRequest): 重置请求数据
            db (Session): 数据库会话
        
        Returns:
            bool: 重置是否成功
        
        Raises:
            ValueError: 密码错误或重置失败
        """
        try:
            # 验证管理员密码
            # 需要从数据库获取当前用户的密码哈希
            from ..models.sys_user import User
            
            # 使用当前登录用户的用户名查询（这里假设管理员用户名为admin，实际应该从token中获取）
            current_user = db.query(User).filter(
                User.username == "admin"
            ).first()
            
            if not current_user:
                raise ValueError("用户不存在")
            
            if not verify_password(reset_data.password, current_user.password_hash):
                raise ValueError("密码错误，重置操作被拒绝")
            
            # 完全重置：清空所有数据并重新初始化配置
            db.query(GoodsCategory).delete()
            db.query(Goods).delete()
            db.query(Stock).delete()
            db.query(StockIn).delete()
            db.query(StockOut).delete()
            db.query(StockCheck).delete()
            
            # 清空操作日志
            db.query(OperationLog).delete()
            
            # 清空系统配置并重新初始化
            db.query(Config).delete()
            for config_data in PREDEFINED_CONFIGS:
                config = Config(**config_data)
                db.add(config)
            db.commit()
            
            # 插入系统重置操作日志（log_id=1，手动指定ID以确保为第一条记录）
            reset_log = OperationLog(
                log_id=1,
                user_id=current_user.user_id,
                username=current_user.username,
                operation="系统重置",
                module="system",
                method="POST",
                url="/v1/system/reset",
                params='{"action": "system_reset"}',
                result="success",
                error_message=None,
                ip_address="127.0.0.1",
                user_agent="System"
            )
            db.add(reset_log)
            db.commit()
            
            return True
            
        except ValueError as e:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise ValueError(f"系统重置失败: {str(e)}")


class BackupRestoreService:
    """
    数据备份恢复服务类
    
    负责数据备份、恢复和备份文件管理功能
    """
    
    # 备份文件存储目录
    BACKUP_DIR = Path("backups")
    
    # 数据库文件路径
    DB_FILE = "campus_asset.db"
    
    def __init__(self):
        """
        初始化备份恢复服务
        
        确保备份目录存在
        """
        # 确保备份目录存在
        self.BACKUP_DIR.mkdir(exist_ok=True)
    
    def _format_file_size(self, size: int) -> str:
        """
        格式化文件大小为人类可读格式
        
        Args:
            size (int): 文件大小（字节）
        
        Returns:
            str: 格式化后的文件大小
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def create_backup(self) -> BackupCreateResponse:
        """
        创建数据库备份
        
        使用SQLite的.backup命令进行备份
        
        Returns:
            BackupCreateResponse: 备份文件信息
        
        Raises:
            ValueError: 备份失败
        """
        try:
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"campus_asset_backup_{timestamp}.db"
            backup_path = self.BACKUP_DIR / backup_filename
            
            # 检查源数据库文件是否存在
            if not os.path.exists(self.DB_FILE):
                raise ValueError("数据库文件不存在")
            
            # 使用SQLite的.backup命令进行备份
            source_conn = sqlite3.connect(self.DB_FILE)
            backup_conn = sqlite3.connect(str(backup_path))
            
            try:
                source_conn.backup(backup_conn)
            finally:
                source_conn.close()
                backup_conn.close()
            
            # 获取备份文件大小
            file_size = os.path.getsize(backup_path)
            
            # 创建时间
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return BackupCreateResponse(
                filename=backup_filename,
                create_time=create_time,
                size=file_size,
                size_human=self._format_file_size(file_size)
            )
        except Exception as e:
            raise ValueError(f"创建备份失败: {str(e)}")
    
    def get_backup_list(self) -> BackupListResponse:
        """
        获取备份文件列表
        
        Returns:
            BackupListResponse: 备份文件列表
        
        Raises:
            ValueError: 获取列表失败
        """
        try:
            backups = []
            
            if not self.BACKUP_DIR.exists():
                return BackupListResponse(backups=backups, total=0)
            
            # 遍历备份目录
            for file_path in sorted(self.BACKUP_DIR.glob("campus_asset_backup_*.db"), reverse=True):
                # 提取文件信息
                stat = file_path.stat()
                file_size = stat.st_size
                
                # 解析创建时间（从文件名中提取）
                filename = file_path.name
                try:
                    # 文件名格式：campus_asset_backup_YYYYMMDD_HHMMSS.db
                    timestamp_str = filename.split("campus_asset_backup_")[1].replace(".db", "")
                    create_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                except:
                    create_time = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                
                backups.append(BackupFileResponse(
                    filename=filename,
                    create_time=create_time,
                    size=file_size,
                    size_human=self._format_file_size(file_size)
                ))
            
            return BackupListResponse(backups=backups, total=len(backups))
        except Exception as e:
            raise ValueError(f"获取备份列表失败: {str(e)}")
    
    def delete_backup(self, filename: str) -> bool:
        """
        删除备份文件
        
        Args:
            filename (str): 备份文件名
        
        Returns:
            bool: 删除是否成功
        
        Raises:
            ValueError: 删除失败
        """
        try:
            backup_path = self.BACKUP_DIR / filename
            
            # 检查文件是否存在
            if not backup_path.exists():
                raise ValueError(f"备份文件 {filename} 不存在")
            
            # 检查文件是否是备份文件
            if not filename.startswith("campus_asset_backup_") or not filename.endswith(".db"):
                raise ValueError("只能删除备份文件")
            
            # 删除文件
            os.remove(backup_path)
            
            return True
        except Exception as e:
            raise ValueError(f"删除备份文件失败: {str(e)}")
    
    def download_backup(self, filename: str) -> str:
        """
        获取备份文件路径用于下载
        
        Args:
            filename (str): 备份文件名
        
        Returns:
            str: 备份文件的绝对路径
        
        Raises:
            ValueError: 文件不存在
        """
        backup_path = self.BACKUP_DIR / filename
        
        # 检查文件是否存在
        if not backup_path.exists():
            raise ValueError(f"备份文件 {filename} 不存在")
        
        return str(backup_path.resolve())
    
    def restore_database(
        self,
        restore_data: RestoreRequest,
        current_password_hash: str
    ) -> RestoreResponse:
        """
        从备份文件恢复数据
        
        恢复前会自动创建当前数据库的备份
        
        Args:
            restore_data (RestoreRequest): 恢复请求数据
            current_password_hash (str): 当前用户的密码哈希
        
        Returns:
            RestoreResponse: 恢复操作结果
        
        Raises:
            ValueError: 恢复失败或密码错误
        """
        try:
            # 验证管理员密码
            if not verify_password(restore_data.password, current_password_hash):
                raise ValueError("密码错误，恢复操作被拒绝")
             
            # 检查备份文件是否存在
            backup_path = self.BACKUP_DIR / restore_data.filename
            if not backup_path.exists():
                raise ValueError(f"备份文件 {restore_data.filename} 不存在")
             
            # 检查文件是否是备份文件
            if not restore_data.filename.startswith("campus_asset_backup_") or not restore_data.filename.endswith(".db"):
                raise ValueError("只能使用备份文件进行恢复")
             
            # 使用SQLite的在线恢复功能
            # 连接到当前数据库
            current_conn = sqlite3.connect(self.DB_FILE)
            
            # 连接到备份数据库
            backup_conn = sqlite3.connect(str(backup_path))
            
            try:
                # 使用备份恢复当前数据库（在线恢复）
                backup_conn.backup(current_conn)
            finally:
                current_conn.close()
                backup_conn.close()
             
            restore_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             
            return RestoreResponse(
                success=True,
                message="数据恢复成功",
                restore_time=restore_time,
                backup_filename=restore_data.filename,
                pre_backup_filename=None
            )
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"数据恢复失败: {str(e)}")


# 创建服务实例
operation_log_service = OperationLogService()
config_service = ConfigService()
backup_restore_service = BackupRestoreService()