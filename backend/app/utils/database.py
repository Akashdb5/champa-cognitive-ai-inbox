"""
Database transaction handling utilities
Validates: Requirements 16.4
"""
import logging
from contextlib import contextmanager
from typing import Generator, Optional, Callable, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.utils.errors import notify_error, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


@contextmanager
def transaction_scope(
    db: Session,
    user_id: Optional[str] = None,
    operation: Optional[str] = None
) -> Generator[Session, None, None]:
    """
    Context manager for database transactions with automatic rollback
    
    Args:
        db: Database session
        user_id: Optional user ID for error tracking
        operation: Optional operation name for logging
    
    Yields:
        Session: Database session
    
    Example:
        with transaction_scope(db, user_id="123", operation="create_message") as session:
            # Perform database operations
            session.add(message)
            # Commit happens automatically on success
            # Rollback happens automatically on error
    
    Validates: Requirements 16.4
    """
    try:
        yield db
        db.commit()
        
        if operation:
            logger.info(f"Transaction committed successfully: {operation}")
    
    except SQLAlchemyError as e:
        db.rollback()
        
        error_msg = f"Database transaction failed"
        if operation:
            error_msg = f"{error_msg}: {operation}"
        
        logger.error(f"{error_msg} - {str(e)}")
        
        # Notify error
        notify_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            user_id=user_id,
            context={"operation": operation} if operation else None
        )
        
        raise
    
    except Exception as e:
        db.rollback()
        
        error_msg = f"Unexpected error in transaction"
        if operation:
            error_msg = f"{error_msg}: {operation}"
        
        logger.error(f"{error_msg} - {str(e)}")
        
        # Notify error
        notify_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.CRITICAL,
            user_id=user_id,
            context={"operation": operation} if operation else None
        )
        
        raise


def safe_commit(
    db: Session,
    user_id: Optional[str] = None,
    operation: Optional[str] = None
) -> bool:
    """
    Safely commit a transaction with error handling
    
    Args:
        db: Database session
        user_id: Optional user ID for error tracking
        operation: Optional operation name for logging
    
    Returns:
        bool: True if commit succeeded, False otherwise
    
    Validates: Requirements 16.4
    """
    try:
        db.commit()
        
        if operation:
            logger.info(f"Transaction committed successfully: {operation}")
        
        return True
    
    except SQLAlchemyError as e:
        db.rollback()
        
        error_msg = f"Database commit failed"
        if operation:
            error_msg = f"{error_msg}: {operation}"
        
        logger.error(f"{error_msg} - {str(e)}")
        
        # Notify error
        notify_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            user_id=user_id,
            context={"operation": operation} if operation else None
        )
        
        return False
    
    except Exception as e:
        db.rollback()
        
        error_msg = f"Unexpected error during commit"
        if operation:
            error_msg = f"{error_msg}: {operation}"
        
        logger.error(f"{error_msg} - {str(e)}")
        
        # Notify error
        notify_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.CRITICAL,
            user_id=user_id,
            context={"operation": operation} if operation else None
        )
        
        return False


def safe_rollback(
    db: Session,
    operation: Optional[str] = None
) -> None:
    """
    Safely rollback a transaction with logging
    
    Args:
        db: Database session
        operation: Optional operation name for logging
    
    Validates: Requirements 16.4
    """
    try:
        db.rollback()
        
        if operation:
            logger.info(f"Transaction rolled back: {operation}")
    
    except Exception as e:
        logger.error(f"Error during rollback: {str(e)}")


def check_data_consistency(
    db: Session,
    checks: list[Callable[[Session], bool]],
    operation: Optional[str] = None
) -> bool:
    """
    Check data consistency using provided check functions
    
    Args:
        db: Database session
        checks: List of check functions that return True if consistent
        operation: Optional operation name for logging
    
    Returns:
        bool: True if all checks pass, False otherwise
    
    Example:
        def check_message_has_user(session):
            # Check that message has valid user
            return True
        
        consistent = check_data_consistency(
            db,
            [check_message_has_user],
            operation="create_message"
        )
    
    Validates: Requirements 16.4
    """
    for i, check in enumerate(checks):
        try:
            if not check(db):
                logger.warning(
                    f"Data consistency check {i+1} failed"
                    + (f" for operation: {operation}" if operation else "")
                )
                return False
        except Exception as e:
            logger.error(
                f"Error running consistency check {i+1}: {str(e)}"
                + (f" for operation: {operation}" if operation else "")
            )
            return False
    
    return True


class TransactionManager:
    """
    Manager for handling complex transactions with consistency checks
    Validates: Requirements 16.4
    """
    
    def __init__(self, db: Session, user_id: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.operations = []
    
    def add_operation(self, operation: str) -> None:
        """Add an operation to the transaction log"""
        self.operations.append(operation)
    
    def commit(self) -> bool:
        """
        Commit the transaction with logging
        
        Returns:
            bool: True if successful
        """
        operation_summary = " -> ".join(self.operations) if self.operations else "transaction"
        return safe_commit(self.db, self.user_id, operation_summary)
    
    def rollback(self) -> None:
        """Rollback the transaction with logging"""
        operation_summary = " -> ".join(self.operations) if self.operations else "transaction"
        safe_rollback(self.db, operation_summary)
    
    def check_consistency(self, checks: list[Callable[[Session], bool]]) -> bool:
        """
        Check data consistency
        
        Args:
            checks: List of check functions
        
        Returns:
            bool: True if all checks pass
        """
        operation_summary = " -> ".join(self.operations) if self.operations else "transaction"
        return check_data_consistency(self.db, checks, operation_summary)
