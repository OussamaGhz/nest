from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    x_pos = Column(Float, nullable=False)
    y_pos = Column(Float, nullable=False)

    # Relationships
    outgoing_edges = relationship("Edge", foreign_keys="Edge.source_id", back_populates="source_node")
    incoming_edges = relationship("Edge", foreign_keys="Edge.target_id", back_populates="target_node")
    robots = relationship("Robot", back_populates="current_node")
    
    # Tasks starting or ending at this node
    starting_tasks = relationship("Task", foreign_keys="Task.start_node_id", back_populates="start_node")
    ending_tasks = relationship("Task", foreign_keys="Task.end_node_id", back_populates="end_node")
    
    # Index for spatial queries (will help with finding nearest nodes)
    __table_args__ = (
        Index('idx_node_position', 'x_pos', 'y_pos'),
    )

class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    weight_cm = Column(Integer, nullable=False)  # Distance in centimeters

    # Relationships
    source_node = relationship("Node", foreign_keys=[source_id], back_populates="outgoing_edges")
    target_node = relationship("Node", foreign_keys=[target_id], back_populates="incoming_edges")
    
    # Composite index for quickly finding paths between nodes
    __table_args__ = (
        Index('idx_edge_source_target', 'source_id', 'target_id', unique=True),
    )

class Robot(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True, index=True)
    current_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    battery = Column(Float, nullable=False)  # Battery percentage (0-100)

    # Relationships
    current_node = relationship("Node", back_populates="robots")
    tasks = relationship("Task", back_populates="robot")
    
    # Index for finding robots by battery level (useful for scheduling)
    __table_args__ = (
        Index('idx_robot_battery', 'battery'),
    )

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    start_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    end_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    robot_id = Column(Integer, ForeignKey("robots.id"), nullable=True)  # Nullable for unassigned tasks
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    
    # Relationships
    start_node = relationship("Node", foreign_keys=[start_node_id], back_populates="starting_tasks")
    end_node = relationship("Node", foreign_keys=[end_node_id], back_populates="ending_tasks")
    robot = relationship("Robot", back_populates="tasks")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_task_status', 'status'),
        Index('idx_task_robot', 'robot_id'),
        Index('idx_task_nodes', 'start_node_id', 'end_node_id'),
    )