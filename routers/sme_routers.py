"""
SME Management System API Routers
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.database import get_db
from app.auth import get_current_user
from app.models import User
from models.sme_models import (
    Employee, Department, Position, Customer, Project, 
    Material, Supplier, TimeEntry, LeaveRequest, Tool
)

# Employee Management Router
employee_router = APIRouter(prefix="/employees", tags=["Employee Management"])

@employee_router.get("/", response_model=List[dict])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of employees with filtering and pagination"""
    query = db.query(Employee)
    
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    
    employees = query.offset(skip).limit(limit).all()
    
    return [
        {
            "employee_id": emp.employee_id,
            "employee_code": emp.employee_code,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "department_id": emp.department_id,
            "position_id": emp.position_id,
            "employment_type": emp.employment_type.value if emp.employment_type else None,
            "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
            "is_active": emp.is_active
        }
        for emp in employees
    ]

@employee_router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get employee details by ID"""
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {
        "employee_id": employee.employee_id,
        "employee_code": employee.employee_code,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "phone": employee.phone,
        "address": employee.address,
        "national_id": employee.national_id,
        "department_id": employee.department_id,
        "position_id": employee.position_id,
        "employment_type": employee.employment_type.value if employee.employment_type else None,
        "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
        "base_salary": float(employee.base_salary) if employee.base_salary else None,
        "annual_leave_balance": employee.annual_leave_balance,
        "sick_leave_balance": employee.sick_leave_balance,
        "personal_leave_balance": employee.personal_leave_balance,
        "is_active": employee.is_active,
        "created_at": employee.created_at.isoformat() if employee.created_at else None
    }

# Department Management Router
department_router = APIRouter(prefix="/departments", tags=["Department Management"])

@department_router.get("/", response_model=List[dict])
async def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of departments"""
    query = db.query(Department)
    
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)
    
    departments = query.offset(skip).limit(limit).all()
    
    return [
        {
            "department_id": dept.department_id,
            "department_name": dept.department_name,
            "description": dept.description,
            "manager_id": dept.manager_id,
            "budget_allocation": float(dept.budget_allocation) if dept.budget_allocation else None,
            "is_active": dept.is_active,
            "employee_count": len(dept.employees) if dept.employees else 0
        }
        for dept in departments
    ]

# Project Management Router
project_router = APIRouter(prefix="/projects", tags=["Project Management"])

@project_router.get("/", response_model=List[dict])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of projects with filtering"""
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    if customer_id:
        query = query.filter(Project.customer_id == customer_id)
    
    projects = query.offset(skip).limit(limit).all()
    
    return [
        {
            "project_id": proj.project_id,
            "project_code": proj.project_code,
            "project_name": proj.project_name,
            "description": proj.description,
            "customer_id": proj.customer_id,
            "start_date": proj.start_date.isoformat() if proj.start_date else None,
            "end_date": proj.end_date.isoformat() if proj.end_date else None,
            "contract_value": float(proj.contract_value) if proj.contract_value else None,
            "estimated_cost": float(proj.estimated_cost) if proj.estimated_cost else None,
            "actual_cost": float(proj.actual_cost) if proj.actual_cost else None,
            "status": proj.status.value if proj.status else None,
            "progress_percentage": float(proj.progress_percentage) if proj.progress_percentage else None,
            "project_manager_id": proj.project_manager_id
        }
        for proj in projects
    ]

@project_router.get("/{project_id}")
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project details by ID"""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "project_id": project.project_id,
        "project_code": project.project_code,
        "project_name": project.project_name,
        "description": project.description,
        "customer_id": project.customer_id,
        "start_date": project.start_date.isoformat() if project.start_date else None,
        "end_date": project.end_date.isoformat() if project.end_date else None,
        "estimated_duration": project.estimated_duration,
        "contract_value": float(project.contract_value) if project.contract_value else None,
        "estimated_cost": float(project.estimated_cost) if project.estimated_cost else None,
        "actual_cost": float(project.actual_cost) if project.actual_cost else None,
        "status": project.status.value if project.status else None,
        "progress_percentage": float(project.progress_percentage) if project.progress_percentage else None,
        "project_manager_id": project.project_manager_id,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None
    }

# Customer Management Router
customer_router = APIRouter(prefix="/customers", tags=["Customer Management"])

@customer_router.get("/", response_model=List[dict])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of customers"""
    query = db.query(Customer)
    
    if is_active is not None:
        query = query.filter(Customer.is_active == is_active)
    
    customers = query.offset(skip).limit(limit).all()
    
    return [
        {
            "customer_id": cust.customer_id,
            "customer_code": cust.customer_code,
            "customer_name": cust.customer_name,
            "contact_person": cust.contact_person,
            "email": cust.email,
            "phone": cust.phone,
            "business_type": cust.business_type,
            "credit_limit": float(cust.credit_limit) if cust.credit_limit else None,
            "payment_terms": cust.payment_terms,
            "is_active": cust.is_active
        }
        for cust in customers
    ]

# Material Management Router
material_router = APIRouter(prefix="/materials", tags=["Material Management"])

@material_router.get("/", response_model=List[dict])
async def get_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    low_stock: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of materials with filtering"""
    query = db.query(Material)
    
    if category:
        query = query.filter(Material.category == category)
    if low_stock:
        query = query.filter(Material.current_stock <= Material.minimum_stock)
    
    materials = query.offset(skip).limit(limit).all()
    
    return [
        {
            "material_id": mat.material_id,
            "material_code": mat.material_code,
            "material_name": mat.material_name,
            "category": mat.category.value if mat.category else None,
            "unit": mat.unit,
            "current_stock": float(mat.current_stock) if mat.current_stock else None,
            "minimum_stock": float(mat.minimum_stock) if mat.minimum_stock else None,
            "unit_cost": float(mat.unit_cost) if mat.unit_cost else None,
            "is_active": mat.is_active,
            "low_stock_alert": (mat.current_stock or 0) <= (mat.minimum_stock or 0)
        }
        for mat in materials
    ]

# Time Entry Router
timeentry_router = APIRouter(prefix="/time-entries", tags=["Time Management"])

@timeentry_router.get("/", response_model=List[dict])
async def get_time_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[str] = None,
    project_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get time entries with filtering"""
    query = db.query(TimeEntry)
    
    if employee_id:
        query = query.filter(TimeEntry.employee_id == employee_id)
    if project_id:
        query = query.filter(TimeEntry.project_id == project_id)
    if start_date:
        query = query.filter(TimeEntry.entry_date >= start_date)
    if end_date:
        query = query.filter(TimeEntry.entry_date <= end_date)
    
    entries = query.offset(skip).limit(limit).all()
    
    return [
        {
            "entry_id": entry.entry_id,
            "employee_id": entry.employee_id,
            "project_id": entry.project_id,
            "entry_date": entry.entry_date.isoformat() if entry.entry_date else None,
            "start_time": entry.start_time.isoformat() if entry.start_time else None,
            "end_time": entry.end_time.isoformat() if entry.end_time else None,
            "normal_hours": float(entry.normal_hours) if entry.normal_hours else None,
            "ot_hour_1": float(entry.ot_hour_1) if entry.ot_hour_1 else None,
            "ot_hour_2": float(entry.ot_hour_2) if entry.ot_hour_2 else None,
            "ot_hour_3": float(entry.ot_hour_3) if entry.ot_hour_3 else None,
            "work_description": entry.work_description,
            "location": entry.location,
            "is_approved": entry.is_approved,
            "approved_by": entry.approved_by,
            "approved_at": entry.approved_at.isoformat() if entry.approved_at else None
        }
        for entry in entries
    ]

# Leave Request Router
leave_router = APIRouter(prefix="/leave-requests", tags=["Leave Management"])

@leave_router.get("/", response_model=List[dict])
async def get_leave_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[str] = None,
    status: Optional[str] = None,
    leave_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get leave requests with filtering"""
    query = db.query(LeaveRequest)
    
    if employee_id:
        query = query.filter(LeaveRequest.employee_id == employee_id)
    if status:
        query = query.filter(LeaveRequest.status == status)
    if leave_type:
        query = query.filter(LeaveRequest.leave_type == leave_type)
    
    requests = query.offset(skip).limit(limit).all()
    
    return [
        {
            "request_id": req.request_id,
            "employee_id": req.employee_id,
            "leave_type": req.leave_type.value if req.leave_type else None,
            "start_date": req.start_date.isoformat() if req.start_date else None,
            "end_date": req.end_date.isoformat() if req.end_date else None,
            "total_days": req.total_days,
            "reason": req.reason,
            "status": req.status.value if req.status else None,
            "approved_by": req.approved_by,
            "approved_at": req.approved_at.isoformat() if req.approved_at else None,
            "rejection_reason": req.rejection_reason,
            "coverage_employee_id": req.coverage_employee_id,
            "created_at": req.created_at.isoformat() if req.created_at else None
        }
        for req in requests
    ]

# Tool Management Router
tool_router = APIRouter(prefix="/tools", tags=["Tool Management"])

@tool_router.get("/", response_model=List[dict])
async def get_tools(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    is_available: Optional[bool] = None,
    condition: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of tools with filtering"""
    query = db.query(Tool)
    
    if category:
        query = query.filter(Tool.category == category)
    if is_available is not None:
        query = query.filter(Tool.is_available == is_available)
    if condition:
        query = query.filter(Tool.condition == condition)
    
    tools = query.offset(skip).limit(limit).all()
    
    return [
        {
            "tool_id": tool.tool_id,
            "tool_code": tool.tool_code,
            "tool_name": tool.tool_name,
            "category": tool.category,
            "brand": tool.brand,
            "model": tool.model,
            "serial_number": tool.serial_number,
            "purchase_cost": float(tool.purchase_cost) if tool.purchase_cost else None,
            "current_value": float(tool.current_value) if tool.current_value else None,
            "condition": tool.condition,
            "is_available": tool.is_available,
            "location": tool.location,
            "last_maintenance_date": tool.last_maintenance_date.isoformat() if tool.last_maintenance_date else None,
            "next_maintenance_date": tool.next_maintenance_date.isoformat() if tool.next_maintenance_date else None
        }
        for tool in tools
    ]

# Dashboard Analytics Router
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics & Reports"])

@analytics_router.get("/dashboard")
async def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard analytics data"""
    
    # Employee statistics
    total_employees = db.query(Employee).filter(Employee.is_active == True).count()
    total_departments = db.query(Department).filter(Department.is_active == True).count()
    
    # Project statistics
    active_projects = db.query(Project).filter(Project.status == "active").count()
    total_projects = db.query(Project).count()
    
    # Material statistics
    total_materials = db.query(Material).filter(Material.is_active == True).count()
    low_stock_materials = db.query(Material).filter(
        Material.current_stock <= Material.minimum_stock,
        Material.is_active == True
    ).count()
    
    # Leave requests statistics
    pending_leave_requests = db.query(LeaveRequest).filter(
        LeaveRequest.status == "pending"
    ).count()
    
    # Tool statistics
    available_tools = db.query(Tool).filter(Tool.is_available == True).count()
    total_tools = db.query(Tool).count()
    
    return {
        "employees": {
            "total": total_employees,
            "departments": total_departments
        },
        "projects": {
            "active": active_projects,
            "total": total_projects,
            "completion_rate": round((total_projects - active_projects) / total_projects * 100, 2) if total_projects > 0 else 0
        },
        "materials": {
            "total": total_materials,
            "low_stock": low_stock_materials,
            "stock_alert_percentage": round(low_stock_materials / total_materials * 100, 2) if total_materials > 0 else 0
        },
        "leave_requests": {
            "pending": pending_leave_requests
        },
        "tools": {
            "available": available_tools,
            "total": total_tools,
            "utilization_rate": round((total_tools - available_tools) / total_tools * 100, 2) if total_tools > 0 else 0
        },
        "timestamp": datetime.now().isoformat()
    }

