"""
CampusAssetManager/backend/app/services/goods_service.py
物品管理服务类

功能说明：
- 物品分类列表查询
- 创建物品分类
- 获取分类详情
- 更新分类信息
- 删除分类
- 物品列表查询（支持分页、搜索）
- 创建物品
- 获取物品详情
- 更新物品信息
- 删除物品（软删除）
- 物品批量导入导出
- 导入模板生成

设计原则：
- 面向对象：使用 GoodsService 类封装物品管理逻辑
- 声明式：使用 Pydantic 定义数据模型
- 封装清晰：提供简洁的公共方法

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO
from datetime import datetime

from ..models.goods_category import GoodsCategory
from ..models.goods_info import Goods
from ..models.stock_info import Stock
from ..schemas.goods import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    GoodsCreate,
    GoodsUpdate,
    GoodsQuery,
    GoodsResponse,
    GoodsListResponse,
    GoodsImportItem,
    GoodsImportResponse,
    GoodsImportError,
    GoodsExportQuery
)


class GoodsService:
    """
    物品管理服务类
    
    负责处理物品相关的所有业务逻辑
    """
    
    # ==================== 物品分类管理 ====================
    
    def get_category_list(
        self,
        db: Session
    ) -> CategoryListResponse:
        """
        查询物品分类列表
        
        Args:
            db (Session): 数据库会话
        
        Returns:
            CategoryListResponse: 分类列表响应
        
        Examples:
            >>> service = GoodsService()
            >>> result = service.get_category_list(db)
        """
        # 查询所有分类
        categories = db.query(GoodsCategory).order_by(
            GoodsCategory.sort_order,
            GoodsCategory.category_id
        ).all()
        
        # 转换为响应模型
        items = [CategoryResponse.model_validate(category) for category in categories]
        
        return CategoryListResponse(
            items=items,
            total=len(items)
        )
    
    def create_category(
        self,
        category_data: CategoryCreate,
        db: Session
    ) -> CategoryResponse:
        """
        创建新分类
        
        Args:
            category_data (CategoryCreate): 分类创建数据
            db (Session): 数据库会话
        
        Returns:
            CategoryResponse: 创建的分类信息
        
        Raises:
            ValueError: 分类编码已存在
        
        Examples:
            >>> service = GoodsService()
            >>> category_data = CategoryCreate(
            ...     category_name="办公设备",
            ...     category_code="BG_SB"
            ... )
            >>> category = service.create_category(category_data, db)
        """
        # 检查分类编码是否已存在
        existing_category = db.query(GoodsCategory).filter(
            GoodsCategory.category_code == category_data.category_code
        ).first()
        
        if existing_category:
            raise ValueError("分类编码已存在")
        
        # 计算分类层级
        level = 1
        if category_data.parent_id:
            parent_category = db.query(GoodsCategory).filter(
                GoodsCategory.category_id == category_data.parent_id
            ).first()
            if parent_category:
                level = parent_category.level + 1
            else:
                raise ValueError("父分类不存在")
        
        # 创建分类对象
        new_category = GoodsCategory(
            category_name=category_data.category_name,
            category_code=category_data.category_code,
            parent_id=category_data.parent_id,
            level=level,
            description=category_data.description,
            sort_order=category_data.sort_order,
            is_active=category_data.is_active
        )
        
        # 保存到数据库
        try:
            db.add(new_category)
            db.commit()
            db.refresh(new_category)
            return CategoryResponse.model_validate(new_category)
        except Exception as e:
            db.rollback()
            raise Exception(f"创建分类失败: {str(e)}")
    
    def get_category_by_id(
        self,
        category_id: int,
        db: Session
    ) -> CategoryResponse:
        """
        根据ID获取分类详情
        
        Args:
            category_id (int): 分类ID
            db (Session): 数据库会话
        
        Returns:
            CategoryResponse: 分类信息
        
        Raises:
            ValueError: 分类不存在
        
        Examples:
            >>> service = GoodsService()
            >>> category = service.get_category_by_id(1, db)
        """
        category = db.query(GoodsCategory).filter(
            GoodsCategory.category_id == category_id
        ).first()
        
        if not category:
            raise ValueError("分类不存在")
        
        return CategoryResponse.model_validate(category)
    
    def update_category(
        self,
        category_id: int,
        category_data: CategoryUpdate,
        db: Session
    ) -> CategoryResponse:
        """
        更新分类信息
        
        Args:
            category_id (int): 分类ID
            category_data (CategoryUpdate): 分类更新数据
            db (Session): 数据库会话
        
        Returns:
            CategoryResponse: 更新后的分类信息
        
        Raises:
            ValueError: 分类不存在
        
        Examples:
            >>> service = GoodsService()
            >>> category_data = CategoryUpdate(category_name="新分类名")
            >>> category = service.update_category(1, category_data, db)
        """
        # 查询分类
        category = db.query(GoodsCategory).filter(
            GoodsCategory.category_id == category_id
        ).first()
        
        if not category:
            raise ValueError("分类不存在")
        
        # 更新字段
        update_dict = category_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(category, field, value)
        
        # 保存到数据库
        try:
            db.commit()
            db.refresh(category)
            return CategoryResponse.model_validate(category)
        except Exception as e:
            db.rollback()
            raise Exception(f"更新分类失败: {str(e)}")
    
    def delete_category(
        self,
        category_id: int,
        db: Session
    ) -> None:
        """
        删除分类
        
        注意：删除分类前需要检查是否有子分类或关联的物品
        
        Args:
            category_id (int): 分类ID
            db (Session): 数据库会话
        
        Raises:
            ValueError: 分类不存在、有子分类或有关联物品
        
        Examples:
            >>> service = GoodsService()
            >>> service.delete_category(1, db)
        """
        # 查询分类
        category = db.query(GoodsCategory).filter(
            GoodsCategory.category_id == category_id
        ).first()
        
        if not category:
            raise ValueError("分类不存在")
        
        # 检查是否有子分类
        has_children = db.query(GoodsCategory).filter(
            GoodsCategory.parent_id == category_id
        ).first()
        
        if has_children:
            raise ValueError("该分类下包含子分类，无法删除")
        
        # 检查是否有关联的物品
        has_goods = db.query(Goods).filter(
            Goods.category_id == category_id
        ).first()
        
        if has_goods:
            raise ValueError("该分类下包含物品，无法删除")
        
        # 删除分类
        try:
            db.delete(category)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"删除分类失败: {str(e)}")
    
    # ==================== 物品信息管理 ====================
    
    def get_goods_list(
        self,
        query: GoodsQuery,
        db: Session
    ) -> GoodsListResponse:
        """
        查询物品列表
        
        Args:
            query (GoodsQuery): 查询参数（分页、搜索、筛选）
            db (Session): 数据库会话
        
        Returns:
            GoodsListResponse: 物品列表响应
        
        Examples:
            >>> service = GoodsService()
            >>> query = GoodsQuery(page=1, page_size=20)
            >>> result = service.get_goods_list(query, db)
        """
        # 构建基础查询（关联分类表）
        db_query = db.query(
            Goods,
            GoodsCategory.category_name
        ).outerjoin(
            GoodsCategory,
            Goods.category_id == GoodsCategory.category_id
        )
        
        # 搜索过滤
        if query.search:
            search_pattern = f"%{query.search}%"
            db_query = db_query.filter(
                or_(
                    Goods.goods_name.like(search_pattern),
                    Goods.goods_code.like(search_pattern)
                )
            )
        
        # 分类过滤
        if query.category_id:
            db_query = db_query.filter(Goods.category_id == query.category_id)
        
        # 状态过滤
        if query.status:
            db_query = db_query.filter(Goods.status == query.status)
        
        # 计算总数
        total = db_query.count()
        
        # 分页
        offset = (query.page - 1) * query.page_size
        goods_list = db_query.offset(offset).limit(query.page_size).all()
        
        # 转换为响应模型
        items = []
        for goods, category_name in goods_list:
            goods_dict = {
                **GoodsResponse.model_validate(goods).model_dump(),
                'category_name': category_name
            }
            items.append(GoodsResponse(**goods_dict))
        
        return GoodsListResponse(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    def create_goods(
        self,
        goods_data: GoodsCreate,
        db: Session
    ) -> GoodsResponse:
        """
        创建新物品
        
        Args:
            goods_data (GoodsCreate): 物品创建数据
            db (Session): 数据库会话
        
        Returns:
            GoodsResponse: 创建的物品信息
        
        Raises:
            ValueError: 物品编码已存在、分类不存在
        
        Examples:
            >>> service = GoodsService()
            >>> goods_data = GoodsCreate(
            ...     goods_name="笔记本电脑",
            ...     goods_code="NB_001",
            ...     category_id=1,
            ...     unit="台",
            ...     purchase_price=8000.00
            ... )
            >>> goods = service.create_goods(goods_data, db)
        """
        # 检查物品编码是否已存在
        existing_goods = db.query(Goods).filter(
            Goods.goods_code == goods_data.goods_code
        ).first()
        
        if existing_goods:
            raise ValueError("物品编码已存在")
        
        # 检查分类是否存在
        category = db.query(GoodsCategory).filter(
            GoodsCategory.category_id == goods_data.category_id
        ).first()
        
        if not category:
            raise ValueError("分类不存在")
        
        # 创建物品对象
        new_goods = Goods(
            goods_name=goods_data.goods_name,
            goods_code=goods_data.goods_code,
            category_id=goods_data.category_id,
            specification=goods_data.specification,
            unit=goods_data.unit,
            purchase_price=goods_data.purchase_price,
            retail_price=goods_data.retail_price,
            description=goods_data.description,
            status=goods_data.status
        )
        
        # 保存到数据库
        try:
            db.add(new_goods)
            db.commit()
            db.refresh(new_goods)
            return GoodsResponse.model_validate(new_goods)
        except Exception as e:
            db.rollback()
            raise Exception(f"创建物品失败: {str(e)}")
    
    def get_goods_by_id(
        self,
        goods_id: int,
        db: Session
    ) -> GoodsResponse:
        """
        根据ID获取物品详情
        
        Args:
            goods_id (int): 物品ID
            db (Session): 数据库会话
        
        Returns:
            GoodsResponse: 物品信息
        
        Raises:
            ValueError: 物品不存在
        
        Examples:
            >>> service = GoodsService()
            >>> goods = service.get_goods_by_id(1, db)
        """
        # 查询物品（包含分类信息）
        result = db.query(
            Goods,
            GoodsCategory.category_name
        ).outerjoin(
            GoodsCategory,
            Goods.category_id == GoodsCategory.category_id
        ).filter(
            Goods.goods_id == goods_id
        ).first()
        
        if not result:
            raise ValueError("物品不存在")
        
        goods, category_name = result
        
        # 构建响应数据
        goods_dict = {
            **GoodsResponse.model_validate(goods).model_dump(),
            'category_name': category_name
        }
        
        return GoodsResponse(**goods_dict)
    
    def update_goods(
        self,
        goods_id: int,
        goods_data: GoodsUpdate,
        db: Session
    ) -> GoodsResponse:
        """
        更新物品信息
        
        Args:
            goods_id (int): 物品ID
            goods_data (GoodsUpdate): 物品更新数据
            db (Session): 数据库会话
        
        Returns:
            GoodsResponse: 更新后的物品信息
        
        Raises:
            ValueError: 物品不存在、分类不存在
        
        Examples:
            >>> service = GoodsService()
            >>> goods_data = GoodsUpdate(goods_name="新名称")
            >>> goods = service.update_goods(1, goods_data, db)
        """
        # 查询物品
        goods = db.query(Goods).filter(Goods.goods_id == goods_id).first()
        
        if not goods:
            raise ValueError("物品不存在")
        
        # 如果更新分类，需要检查分类是否存在
        if goods_data.category_id is not None:
            category = db.query(GoodsCategory).filter(
                GoodsCategory.category_id == goods_data.category_id
            ).first()
            
            if not category:
                raise ValueError("分类不存在")
        
        # 更新字段
        update_dict = goods_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(goods, field, value)
        
        # 保存到数据库
        try:
            db.commit()
            db.refresh(goods)
            return GoodsResponse.model_validate(goods)
        except Exception as e:
            db.rollback()
            raise Exception(f"更新物品失败: {str(e)}")
    
    def delete_goods(
        self,
        goods_id: int,
        db: Session
    ) -> None:
        """
        删除物品（物理删除）
        
        Args:
            goods_id (int): 物品ID
            db (Session): 数据库会话
        
        Raises:
            ValueError: 物品不存在
        
        Examples:
            >>> service = GoodsService()
            >>> service.delete_goods(1, db)
        """
        # 查询物品
        goods = db.query(Goods).filter(Goods.goods_id == goods_id).first()
        
        if not goods:
            raise ValueError("物品不存在")
        
        # 物理删除：从数据库中删除记录
        try:
            db.delete(goods)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"删除物品失败: {str(e)}")
    
    # ==================== 物品导入导出管理 ====================
    
    def generate_import_template(self) -> BytesIO:
        """
        生成物品导入模板
        
        Returns:
            BytesIO: Excel文件流
        
        Examples:
            >>> service = GoodsService()
            >>> excel_file = service.generate_import_template()
        """
        # 创建工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = "Template"
        
        # 设置表头（第1行）
        headers = [
            "物品名称*",
            "物品编码*",
            "分类编码*",
            "规格型号",
            "计量单位*",
            "采购单价*",
            "零售单价",
            "物品描述",
            "状态*"
        ]
        
        # 写入表头
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # 使用说明（合并单元格在表头右侧，只占用前4行，不影响数据读取）
        ws.merge_cells(start_row=1, start_column=10, end_row=4, end_column=15)
        note_cell = ws.cell(row=1, column=10)
        note_text = "【使用说明】\n•必填(带*项)：名称、编码、分类、单位、单价\n•可选：规格、零售价、描述、状态(默认1)\n•状态值:1-正常 2-报废 3-维修\n•注意:分类不存在时会自动创建、编码唯一、金额≥0\n•示例:左侧3行"
        note_cell.value = note_text
        note_cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        note_cell.font = Font(size=11)
        note_cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
        
        # 增加前4行的高度以显示完整说明
        # ws.row_dimensions[1].height = 80
        ws.row_dimensions[2].height = 25
        ws.row_dimensions[3].height = 25
        ws.row_dimensions[4].height = 25
        
        # 添加示例数据（第2-4行，共3行）
        example_data = [
            ["示例1：笔记本电脑", "NB_001", "BG_SB", "ThinkPad X1 Carbon", "台", "8000.00", "10000.00", "说明：ThinkPad X1系列高性能商务笔记本", "1"],
            ["示例2：显示器", "DP_001", "BG_DP", "Dell 27英寸", "台", "1500.00", "1800.00", "说明：高清显示器", "2"],
            ["示例3：打印机", "PR_001", "BG_SB", "HP LaserJet Pro", "台", "2000.00", "2500.00", "说明：激光打印机，适合日常办公使用", "3"]
        ]
        
        # 写入示例数据
        for row_num, row_data in enumerate(example_data, 2):
            for col_num, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                if row_num == 2:
                    # 第一行示例数据高亮显示
                    cell.fill = PatternFill(start_color="E7F3FF", end_color="E7F3FF", fill_type="solid")
                    cell.font = Font(italic=True, color="004080")
                elif row_num > 2:
                    # 其他示例数据使用浅色背景
                    cell.fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
                    cell.font = Font(italic=True, color="666666")
        
        # 导入读取起始行（示例数据从第2行开始，共3行，所以从第5行开始读取）
        self.import_start_row = 5
        
        # 调整列宽
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 25
        ws.column_dimensions['E'].width = 10
        ws.column_dimensions['F'].width = 12
        ws.column_dimensions['G'].width = 12
        ws.column_dimensions['H'].width = 40
        ws.column_dimensions['I'].width = 10
        
        # 保存到内存
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        
        return file_stream
    
    def import_goods_from_excel(
        self,
        file_content: bytes,
        db: Session
    ) -> GoodsImportResponse:
        """
        从Excel文件批量导入物品
        
        Args:
            file_content (bytes): Excel文件内容
            db (Session): 数据库会话
        
        Returns:
            GoodsImportResponse: 导入结果统计
        
        Raises:
            ValueError: 文件格式错误
        
        Examples:
            >>> service = GoodsService()
            >>> result = service.import_goods_from_excel(file_bytes, db)
        """
        # 加载Excel文件
        try:
            wb = load_workbook(BytesIO(file_content))
            ws = wb.active
        except Exception as e:
            raise ValueError(f"Excel文件格式错误: {str(e)}")
        
        # 统计变量
        total_count = 0
        success_count = 0
        failed_count = 0
        errors = []
        
        # 获取所有分类编码映射
        categories = db.query(GoodsCategory).all()
        category_map = {cat.category_code: cat.category_id for cat in categories}
        
        # 从第5行开始读取数据（第1行是表头，第2-4行是示例数据）
        for row_num in range(5, ws.max_row + 1):
            total_count += 1
            
            try:
                # 读取单元格数据
                goods_name = ws.cell(row=row_num, column=1).value
                goods_code = ws.cell(row=row_num, column=2).value
                category_code = ws.cell(row=row_num, column=3).value
                specification = ws.cell(row=row_num, column=4).value
                unit = ws.cell(row=row_num, column=5).value
                purchase_price = ws.cell(row=row_num, column=6).value
                retail_price = ws.cell(row=row_num, column=7).value
                description = ws.cell(row=row_num, column=8).value
                status = ws.cell(row=row_num, column=9).value
                
                # 数据验证
                if not goods_name or not isinstance(goods_name, str):
                    raise ValueError("物品名称不能为空")
                if not goods_code or not isinstance(goods_code, str):
                    raise ValueError("物品编码不能为空")
                if not category_code or not isinstance(category_code, str):
                    raise ValueError("分类编码不能为空")
                if not unit or not isinstance(unit, str):
                    raise ValueError("计量单位不能为空")
                if purchase_price is None or purchase_price == '':
                    raise ValueError("采购单价不能为空")
                
                # 转换数据类型
                try:
                    purchase_price = float(purchase_price)
                    if purchase_price < 0:
                        raise ValueError("采购单价不能为负数")
                except (ValueError, TypeError):
                    raise ValueError("采购单价格式错误")
                
                if retail_price:
                    try:
                        retail_price = float(retail_price)
                        if retail_price < 0:
                            raise ValueError("零售单价不能为负数")
                    except (ValueError, TypeError):
                        raise ValueError("零售单价格式错误")
                    if retail_price == '':
                        retail_price = None
                else:
                    retail_price = None
                
                if status:
                    try:
                        status = int(status)
                        if status not in [1, 2, 3]:
                            raise ValueError("状态必须是1、2或3")
                    except (ValueError, TypeError):
                        raise ValueError("状态格式错误")
                else:
                    status = 1
                
                # 检查分类编码是否存在，不存在则自动创建
                if category_code not in category_map:
                    # 自动创建新分类（一级分类，默认激活）
                    new_category = GoodsCategory(
                        category_name=category_code,
                        category_code=category_code,
                        parent_id=None,
                        level=1,
                        description=f"物品导入时自动创建的分类",
                        sort_order=999,
                        is_active=1
                    )
                    db.add(new_category)
                    db.flush()
                    
                    # 更新映射表
                    category_map[category_code] = new_category.category_id
                    category_id = new_category.category_id
                else:
                    category_id = category_map[category_code]
                
                # 检查物品编码是否已存在
                existing_goods = db.query(Goods).filter(
                    Goods.goods_code == goods_code
                ).first()
                
                if existing_goods:
                    raise ValueError("物品编码已存在")
                
                # 创建物品对象
                new_goods = Goods(
                    goods_name=goods_name.strip(),
                    goods_code=goods_code.strip(),
                    category_id=category_id,
                    specification=specification.strip() if specification else None,
                    unit=unit.strip(),
                    purchase_price=purchase_price,
                    retail_price=retail_price,
                    description=description.strip() if description else None,
                    status=status
                )
                
                db.add(new_goods)
                db.flush()
                
                # 自动创建库存记录（库存默认为0）
                new_stock = Stock(
                    goods_id=new_goods.goods_id,
                    current_stock=0,
                    total_value=0.0,
                    min_stock=0
                )
                db.add(new_stock)
                
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                goods_code = ws.cell(row=row_num, column=2).value or ""
                errors.append(
                    GoodsImportError(
                        row=row_num,
                        goods_code=str(goods_code),
                        error_message=str(e)
                    )
                )
        
        # 提交事务
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"导入失败: {str(e)}")
        
        return GoodsImportResponse(
            total_count=total_count,
            success_count=success_count,
            failed_count=failed_count,
            errors=errors
        )
    
    def export_goods_to_excel(
        self,
        query: GoodsExportQuery,
        db: Session
    ) -> BytesIO:
        """
        导出物品列表到Excel
        
        Args:
            query (GoodsExportQuery): 导出查询参数
            db (Session): 数据库会话
        
        Returns:
            BytesIO: Excel文件流
        
        Examples:
            >>> service = GoodsService()
            >>> excel_file = service.export_goods_to_excel(query, db)
        """
        # 构建查询
        db_query = db.query(
            Goods,
            GoodsCategory.category_code,
            GoodsCategory.category_name
        ).outerjoin(
            GoodsCategory,
            Goods.category_id == GoodsCategory.category_id
        )
        
        # 应用过滤条件
        if query.search:
            search_pattern = f"%{query.search}%"
            db_query = db_query.filter(
                or_(
                    Goods.goods_name.like(search_pattern),
                    Goods.goods_code.like(search_pattern)
                )
            )
        
        if query.category_id:
            db_query = db_query.filter(Goods.category_id == query.category_id)
        
        if query.status:
            db_query = db_query.filter(Goods.status == query.status)
        
        # 查询所有数据
        results = db_query.all()
        
        # 创建工作簿（使用英文标题避免编码问题，但表头用中文）
        wb = Workbook()
        ws = wb.active
        ws.title = "Goods List"
        
        # 设置表头（中文表头）
        headers = [
            "物品ID",
            "物品名称",
            "物品编码",
            "分类编码",
            "分类名称",
            "规格型号",
            "计量单位",
            "采购单价",
            "零售单价",
            "物品描述",
            "状态",
            "创建时间",
            "更新时间"
        ]
        
        # 写入表头
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # 写入数据
        for row_num, (goods, category_code, category_name) in enumerate(results, 2):
            status_map = {1: "正常", 2: "报废", 3: "维修中"}
            
            ws.cell(row=row_num, column=1, value=goods.goods_id)
            ws.cell(row=row_num, column=2, value=goods.goods_name)
            ws.cell(row=row_num, column=3, value=goods.goods_code)
            ws.cell(row=row_num, column=4, value=category_code or "")
            ws.cell(row=row_num, column=5, value=category_name or "")
            ws.cell(row=row_num, column=6, value=goods.specification or "")
            ws.cell(row=row_num, column=7, value=goods.unit)
            ws.cell(row=row_num, column=8, value=goods.purchase_price)
            ws.cell(row=row_num, column=9, value=goods.retail_price or "")
            ws.cell(row=row_num, column=10, value=goods.description or "")
            ws.cell(row=row_num, column=11, value=status_map.get(goods.status, ""))
            
            # 格式化时间
            if goods.create_time:
                ws.cell(row=row_num, column=12, value=goods.create_time.strftime("%Y-%m-%d %H:%M:%S"))
            if goods.update_time:
                ws.cell(row=row_num, column=13, value=goods.update_time.strftime("%Y-%m-%d %H:%M:%S"))
        
        # 调整列宽
        column_widths = [10, 20, 20, 15, 20, 25, 15, 15, 15, 40, 10, 20, 20]
        for col_num, width in enumerate(column_widths, 1):
            ws.column_dimensions[chr(64 + col_num)].width = width
        
        # 保存到内存
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        
        return file_stream