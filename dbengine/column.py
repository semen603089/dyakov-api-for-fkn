import logging
from typing import Optional, Tuple, Union

from sqlalchemy import and_

from .exceptions import ProhibitedActionInBranch
from .models import Branch, Commit, DbColumn, DbColumnAttributes, DbTable, BranchTypes, AttributeTypes

logger = logging.getLogger(__name__)

from .models import session


def create_column(
        branch: Branch, table: DbTable, *, name: str, datatype: str
) -> Tuple[DbColumn, DbColumnAttributes, Commit]:
    """Create column in table in branch"""
    logging.debug('create_column')
    if branch.type != BranchTypes.MAIN:
        s = session.query(Commit).filter(Commit.branch_id == branch.id).order_by(Commit.id.desc()).first()
        new_commit = Commit()
        new_commit.branch_id = branch.id
        if s:
            new_commit.prev_commit_id = s.prev_commit_id + 1
        new_commit.attribute_id_in = None
        new_column = DbColumn()
        new_column.type = AttributeTypes.COLUMN
        new_column.table_id = table.id
        session.add(new_column)
        session.flush()
        session.commit()
        new_column_attribute = DbColumnAttributes()
        new_column_attribute.type = AttributeTypes.COLUMN
        new_column_attribute.column_id = new_column.id
        new_column_attribute.datatype = datatype
        new_column_attribute.name = name
        session.add(new_column_attribute)
        session.flush()
        session.commit()
        new_commit.attribute_id_out = new_column.id
        session.add(new_commit)
        session.flush()
        session.commit()
    else:
        raise ProhibitedActionInBranch("Column creating", branch.name)
    return new_column, new_column_attribute, new_commit


def get_column(
        branch: Branch, table: DbTable, id: int
) -> Tuple[DbColumn, DbColumnAttributes]:
    """Get last version of column in table in branch"""
    logging.debug('get_column')
    s = session.query(Commit).filter(and_(Commit.branch_id == branch.id, Commit.attribute_id_out == id)).order_by(
        Commit.id.desc()).first()
    return session.query(DbColumn).filter(DbColumn.id == s.attribute_id_out).one(), session.query(DbColumnAttributes).filter(
        DbColumnAttributes.column_id == s.attribute_id_out).one()


def update_column(
        branch: Branch,
        table: DbTable,
        column: DbColumn,
        *,
        name: Optional[str] = None,
        datatype: Optional[str] = None
) -> Tuple[DbColumn, DbColumnAttributes, Commit]:
    """Update one or more attributes

    То есть создать новые атрибуты и указать начало и конец
    """
    logging.debug('update_column')
    if branch.type != BranchTypes.MAIN:
        s = session.query(Commit).filter(Commit.branch_id == branch.id).order_by(Commit.id.desc()).first()
        new_commit = Commit()
        new_commit.branch_id = branch.id
        if s:
            new_commit.prev_commit_id = s.prev_commit_id + 1
        new_commit.attribute_id_in = column.id
        new_column = DbColumn()
        new_column.type = AttributeTypes.COLUMN
        new_column.table_id = table.id
        session.add(new_column)
        session.flush()
        session.commit()
        new_column_attribute = DbColumnAttributes()
        new_column_attribute.type = AttributeTypes.COLUMN
        new_column_attribute.column_id = new_column.id
        new_column_attribute.datatype = datatype
        new_column_attribute.name = name
        session.add(new_column_attribute)
        session.flush()
        session.commit()
        new_commit.attribute_id_out = new_column.id
        session.add(new_commit)
        session.flush()
        session.commit()
    else:
        raise ProhibitedActionInBranch("Column altering", branch.name)
    return new_column, new_column_attribute, new_commit


def delete_column(branch: Branch, column: DbColumn):
    """Delete column from table from branch

    То есть надо удалить у колонки атрибуты, сам объект колонки останется
    То есть создать коммит с пустым концом
    """
    logging.debug('delete_column')
    if branch.type != BranchTypes.MAIN:
        s = session.query(Commit).filter(Commit.branch_id == branch.id).order_by(
            Commit.id.desc()).first()
        new_commit = Commit()
        new_commit.branch_id = branch.id
        if s:
            new_commit.prev_commit_id = s.prev_commit_id + 1
        new_commit.attribute_id_in = column.table_id
        new_commit.attribute_id_out = None
        session.add(new_commit)
        session.flush()
        session.commit()
