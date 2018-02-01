from sqlalchemy import event
from sqlalchemy import DDL


def _mysql_cidr_overlap(metadata):
    @event.listens_for(metadata, "after_create")
    def _create_mysql_proc(target, connection, **kw):
        if connection.engine.name != 'mysql':
            return

        if connection.scalar(
            "SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES "
            "WHERE ROUTINE_TYPE='FUNCTION' AND ROUTINE_SCHEMA=DATABASE() AND "
            "ROUTINE_NAME=%s",
            ("cidr_overlap", )
        ):
            connection.execute("DROP FUNCTION cidr_overlap")

        connection.execute(
            DDL("""
        CREATE FUNCTION cidr_overlap (cidr1 VARCHAR(30), cidr2 VARCHAR(30))
        RETURNS TINYINT
        BEGIN
        DECLARE bitmask INT;
        -- note - Mike is semi-guessing on the math here, needs tests!  don't stick
        -- into production pls :)
        SET bitmask = pow(
            2,
            (32 - least(
                cast(substring_index(cidr1, '/', -1) as integer),
                cast(substring_index(cidr2, '/', -1) as integer)
            ))
        ) - 1;

        RETURN
            inet_aton(substring_index(cidr1, '/', 1)) & ~bitmask =
            inet_aton(substring_index(cidr2, '/', 1)) & ~bitmask;
        END
        """)
        )


def _sqlite_cidr_overlap(engine):
    import ipaddr

    def python_cidr_overlap(n1, n2):
        n1 = ipaddr.IPNetwork(n1)
        n2 = ipaddr.IPNetwork(n2)
        return n1.overlaps(n2)

    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        if e.name == 'sqlite':
            dbapi_connection.create_function(
                "cidr_overlap", 2, python_cidr_overlap)


def cidr_overlap(engine, metadata):
    if engine.name == 'mysql':
        _mysql_cidr_overlap(metadata)
    elif engine.name == 'sqlite':
        _sqlite_cidr_overlap(engine)

if __name__ == '__main__':
    from sqlalchemy import Column, Integer, String, create_engine, func
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import Session, aliased

    Base = declarative_base()

    class A(Base):
        __tablename__ = 'a'
        id = Column(Integer, primary_key=True)
        subnet = Column(String(30))

    for url in [
        "mysql://scott:tiger@localhost/test",
        "sqlite://"
    ]:
        e = create_engine(url, echo=True)

        cidr_overlap(e, Base.metadata)

        Base.metadata.drop_all(e)
        Base.metadata.create_all(e)

        s = Session(e)

        s.add_all([
            A(subnet='192.168.1.0/24'),
            A(subnet='192.168.2.0/24'),
            A(subnet='192.168.2.0/25')
        ])
        s.commit()

        a1, a2 = aliased(A), aliased(A)

        # return all non-overlapping CIDR pairs
        for a, b in s.query(a1.subnet, a2.subnet).\
            filter(~func.cidr_overlap(a1.subnet, a2.subnet)).\
                filter(a1.id > a2.id):
                print a, b
