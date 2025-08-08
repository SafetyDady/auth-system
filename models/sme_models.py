"""
SME Management System Database Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, ForeignKey, Date, Time, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date, time
import enum

Base = declarative_base()

# Enums
class EmploymentType(enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"

class LeaveType(enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    EMERGENCY = "emergency"

class LeaveStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class ProjectStatus(enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MaterialCategory(enum.Enum):
    RAW_MATERIAL = "raw_material"
    CONSUMABLE = "consumable"
    TOOL = "tool"
    EQUIPMENT = "equipment"
    SPARE_PART = "spare_part"

class PurchaseOrderStatus(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"

# Core Tables
class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(String(20), primary_key=True)
    department_name = Column(String(100), nullable=False)
    description = Column(Text)
    manager_id = Column(String(20), ForeignKey("employees.employee_id"))
    budget_allocation = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    employees = relationship("Employee", back_populates="department")
    manager = relationship("Employee", foreign_keys=[manager_id])

class Position(Base):
    __tablename__ = "positions"
    
    position_id = Column(String(20), primary_key=True)
    position_name = Column(String(100), nullable=False)
    department_id = Column(String(20), ForeignKey("departments.department_id"))
    base_salary = Column(Numeric(10, 2))
    overtime_rate = Column(Numeric(5, 2), default=1.5)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    employees = relationship("Employee", back_populates="position")
    department = relationship("Department")

class Employee(Base):
    __tablename__ = "employees"
    
    employee_id = Column(String(20), primary_key=True)
    employee_code = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    national_id = Column(String(20), unique=True)
    
    # Employment Details
    department_id = Column(String(20), ForeignKey("departments.department_id"))
    position_id = Column(String(20), ForeignKey("positions.position_id"))
    employment_type = Column(Enum(EmploymentType), default=EmploymentType.FULL_TIME)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    
    # Salary Information
    base_salary = Column(Numeric(10, 2), nullable=False)
    overtime_rate = Column(Numeric(5, 2), default=1.5)
    
    # Leave Balances
    annual_leave_balance = Column(Integer, default=15)
    sick_leave_balance = Column(Integer, default=10)
    personal_leave_balance = Column(Integer, default=5)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")
    time_entries = relationship("TimeEntry", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    project_assignments = relationship("ProjectAssignment", back_populates="employee")

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(String(20), primary_key=True)
    customer_code = Column(String(20), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    tax_id = Column(String(20))
    
    # Business Information
    business_type = Column(String(50))
    credit_limit = Column(Numeric(15, 2), default=0)
    payment_terms = Column(Integer, default=30)  # days
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="customer")

class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(String(20), primary_key=True)
    project_code = Column(String(20), unique=True, nullable=False)
    project_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Customer Information
    customer_id = Column(String(20), ForeignKey("customers.customer_id"))
    
    # Project Details
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    estimated_duration = Column(Integer)  # days
    
    # Financial Information
    contract_value = Column(Numeric(15, 2), nullable=False)
    estimated_cost = Column(Numeric(15, 2))
    actual_cost = Column(Numeric(15, 2), default=0)
    
    # Status
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    progress_percentage = Column(Numeric(5, 2), default=0)
    
    # Management
    project_manager_id = Column(String(20), ForeignKey("employees.employee_id"))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="projects")
    project_manager = relationship("Employee", foreign_keys=[project_manager_id])
    assignments = relationship("ProjectAssignment", back_populates="project")
    material_allocations = relationship("MaterialAllocation", back_populates="project")

class ProjectAssignment(Base):
    __tablename__ = "project_assignments"
    
    assignment_id = Column(String(20), primary_key=True)
    project_id = Column(String(20), ForeignKey("projects.project_id"))
    employee_id = Column(String(20), ForeignKey("employees.employee_id"))
    role = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    allocation_percentage = Column(Numeric(5, 2), default=100)
    hourly_rate = Column(Numeric(8, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="assignments")
    employee = relationship("Employee", back_populates="project_assignments")

class Material(Base):
    __tablename__ = "materials"
    
    material_id = Column(String(20), primary_key=True)
    material_code = Column(String(20), unique=True, nullable=False)
    material_name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(Enum(MaterialCategory), nullable=False)
    unit = Column(String(20), nullable=False)  # kg, pcs, m, etc.
    
    # Stock Information
    current_stock = Column(Numeric(10, 3), default=0)
    minimum_stock = Column(Numeric(10, 3), default=0)
    maximum_stock = Column(Numeric(10, 3))
    reorder_point = Column(Numeric(10, 3))
    
    # Cost Information
    unit_cost = Column(Numeric(10, 2), default=0)
    last_purchase_cost = Column(Numeric(10, 2))
    average_cost = Column(Numeric(10, 2))
    
    # Supplier Information
    primary_supplier_id = Column(String(20), ForeignKey("suppliers.supplier_id"))
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    primary_supplier = relationship("Supplier", foreign_keys=[primary_supplier_id])
    allocations = relationship("MaterialAllocation", back_populates="material")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="material")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    supplier_id = Column(String(20), primary_key=True)
    supplier_code = Column(String(20), unique=True, nullable=False)
    supplier_name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    tax_id = Column(String(20))
    
    # Business Information
    payment_terms = Column(Integer, default=30)  # days
    lead_time = Column(Integer, default=7)  # days
    rating = Column(Numeric(3, 2), default=0)  # 0-5 rating
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    materials = relationship("Material", back_populates="primary_supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    po_id = Column(String(20), primary_key=True)
    po_number = Column(String(20), unique=True, nullable=False)
    supplier_id = Column(String(20), ForeignKey("suppliers.supplier_id"))
    
    # Order Information
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date)
    actual_delivery_date = Column(Date)
    
    # Financial Information
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    
    # Status
    status = Column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT)
    
    # Management
    requested_by = Column(String(20), ForeignKey("employees.employee_id"))
    approved_by = Column(String(20), ForeignKey("employees.employee_id"))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    requester = relationship("Employee", foreign_keys=[requested_by])
    approver = relationship("Employee", foreign_keys=[approved_by])
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    
    item_id = Column(String(20), primary_key=True)
    po_id = Column(String(20), ForeignKey("purchase_orders.po_id"))
    material_id = Column(String(20), ForeignKey("materials.material_id"))
    
    # Quantity Information
    quantity_ordered = Column(Numeric(10, 3), nullable=False)
    quantity_received = Column(Numeric(10, 3), default=0)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    
    # Delivery Information
    expected_date = Column(Date)
    actual_date = Column(Date)
    
    # Status
    is_received = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    material = relationship("Material", back_populates="purchase_order_items")

class MaterialAllocation(Base):
    __tablename__ = "material_allocations"
    
    allocation_id = Column(String(20), primary_key=True)
    project_id = Column(String(20), ForeignKey("projects.project_id"))
    material_id = Column(String(20), ForeignKey("materials.material_id"))
    
    # Allocation Information
    allocated_quantity = Column(Numeric(10, 3), nullable=False)
    used_quantity = Column(Numeric(10, 3), default=0)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)
    
    # Management
    allocated_by = Column(String(20), ForeignKey("employees.employee_id"))
    allocation_date = Column(Date, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="material_allocations")
    material = relationship("Material", back_populates="allocations")
    allocated_by_employee = relationship("Employee", foreign_keys=[allocated_by])

class TimeEntry(Base):
    __tablename__ = "time_entries"
    
    entry_id = Column(String(20), primary_key=True)
    employee_id = Column(String(20), ForeignKey("employees.employee_id"))
    project_id = Column(String(20), ForeignKey("projects.project_id"))
    
    # Time Information
    entry_date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    normal_hours = Column(Numeric(4, 2), default=0)
    ot_hour_1 = Column(Numeric(4, 2), default=0)  # 1.5x rate
    ot_hour_2 = Column(Numeric(4, 2), default=0)  # 2.0x rate
    ot_hour_3 = Column(Numeric(4, 2), default=0)  # 3.0x rate
    
    # Work Information
    work_description = Column(Text)
    location = Column(String(100))
    
    # Approval
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String(20), ForeignKey("employees.employee_id"))
    approved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="time_entries", foreign_keys=[employee_id])
    project = relationship("Project", foreign_keys=[project_id])
    approver = relationship("Employee", foreign_keys=[approved_by])

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    request_id = Column(String(20), primary_key=True)
    employee_id = Column(String(20), ForeignKey("employees.employee_id"))
    
    # Leave Information
    leave_type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer, nullable=False)
    reason = Column(Text)
    
    # Approval Workflow
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)
    approved_by = Column(String(20), ForeignKey("employees.employee_id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Coverage Information
    coverage_employee_id = Column(String(20), ForeignKey("employees.employee_id"))
    coverage_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approved_by])
    coverage_employee = relationship("Employee", foreign_keys=[coverage_employee_id])

class Tool(Base):
    __tablename__ = "tools"
    
    tool_id = Column(String(20), primary_key=True)
    tool_code = Column(String(20), unique=True, nullable=False)
    tool_name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    brand = Column(String(50))
    model = Column(String(50))
    serial_number = Column(String(50), unique=True)
    
    # Cost Information
    purchase_cost = Column(Numeric(10, 2))
    purchase_date = Column(Date)
    depreciation_rate = Column(Numeric(5, 2), default=0)  # percentage per year
    current_value = Column(Numeric(10, 2))
    
    # Maintenance Information
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)
    maintenance_interval = Column(Integer)  # days
    
    # Status
    condition = Column(String(20), default="good")  # good, fair, poor, damaged
    is_available = Column(Boolean, default=True)
    location = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    assignments = relationship("ToolAssignment", back_populates="tool")

class ToolAssignment(Base):
    __tablename__ = "tool_assignments"
    
    assignment_id = Column(String(20), primary_key=True)
    tool_id = Column(String(20), ForeignKey("tools.tool_id"))
    employee_id = Column(String(20), ForeignKey("employees.employee_id"))
    project_id = Column(String(20), ForeignKey("projects.project_id"))
    
    # Assignment Information
    assigned_date = Column(Date, nullable=False)
    expected_return_date = Column(Date)
    actual_return_date = Column(Date)
    condition_at_assignment = Column(String(20))
    condition_at_return = Column(String(20))
    
    # Status
    is_returned = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Management
    assigned_by = Column(String(20), ForeignKey("employees.employee_id"))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    tool = relationship("Tool", back_populates="assignments")
    employee = relationship("Employee", foreign_keys=[employee_id])
    project = relationship("Project", foreign_keys=[project_id])
    assigned_by_employee = relationship("Employee", foreign_keys=[assigned_by])

class ExpenseRecord(Base):
    __tablename__ = "expense_records"
    
    expense_id = Column(String(20), primary_key=True)
    employee_id = Column(String(20), ForeignKey("employees.employee_id"))
    project_id = Column(String(20), ForeignKey("projects.project_id"))
    
    # Expense Information
    expense_date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="THB")
    
    # Receipt Information
    receipt_number = Column(String(50))
    receipt_file = Column(String(255))
    vendor = Column(String(100))
    
    # Approval Workflow
    status = Column(String(20), default="pending")  # pending, approved, rejected, paid
    approved_by = Column(String(20), ForeignKey("employees.employee_id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Payment Information
    paid_at = Column(DateTime)
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    project = relationship("Project", foreign_keys=[project_id])
    approver = relationship("Employee", foreign_keys=[approved_by])

# Additional utility tables
class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    setting_id = Column(String(50), primary_key=True)
    setting_value = Column(Text)
    description = Column(Text)
    category = Column(String(50))
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(String(20), ForeignKey("employees.employee_id"))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(String(20), primary_key=True)
    user_id = Column(String(20))
    action = Column(String(100), nullable=False)
    table_name = Column(String(50))
    record_id = Column(String(20))
    old_values = Column(Text)
    new_values = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=func.now())

