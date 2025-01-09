"""
Python script starting up a RESTful web API server. It serves US CIM data.

This takes configurations from environment variables:
- DATABASE_URL: str Required. Pointing to a Postgresql database. e.g. `"postgresql://username:password@database:5432/databasename"`.
- PORT: int Optional. Port the server will listen to. Defaults to `8080`.
- HOST: str Optional. Host for the server. Defaults to `"127.0.0.1"`, for safe local dev. Use `"0.0.0.0"` for all public IPs or container deployments.
"""

from contextlib import asynccontextmanager
import datetime
from dotenv import load_dotenv
from typing import Annotated
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.exc import IntegrityError, OperationalError


load_dotenv()  # Load anything in a .env file.
DB_URL = str(os.environ["DATABASE_URL"])


# Adapted from mei_facilities.csv
class Facility(SQLModel, table=True):
    uid: str = Field(primary_key=True, index=True)
    segment: str = Field(index=True)
    company: str
    # facility_id: str
    technology: str = Field(index=True)
    subcategory: str
    # decarb_sector: str
    # investment_type: str
    investment_status: str
    # status_description: str
    # state: str
    # address: str
    latitude: Annotated[float, Field(gt=-90, lt=90)]
    longitude: Annotated[float, Field(gt=-180, lt=180)]
    # latlon_valid: bool
    # cd118_2022: str
    # cd118_2022_name: str
    # ussenator1_name: str
    # ussenator1_party: str
    # ussenator2_name: str
    # ussenator2_party: str
    # us_representative_name: str
    # us_representative_party: str
    # jobs_reported: int
    # construction_jobs: int
    # investment_reported_flag: bool
    estimated_investment: int | None = None
    announcement_date: Annotated[datetime.date, Field(index=True)]
    # production_date: date
    # construction_start: date
    # construction_end: date

    # Puts an example of this object in publish docs.
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "uid": "M.B.ABC_VA.0",
                    "segment": "Manufacturing",
                    "company": "ABC Group",
                    "technology": "Batteries",
                    "subcategory": "EAM",
                    "investment_status": "U",
                    "latitude": 36.63792,
                    "longitude": -76.39912,
                    "investment_estimated": 6023143,
                    "announcement_date": "2023-06-19",
                }
            ]
        }
    }


engine = create_engine(DB_URL)


def _get_session():
    """
    Creates/tears down database session for each request transaction.

    Helps prevent partial commits to database if something goes wrong.
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(_get_session)]


def _create_db_and_tables():
    """
    Populates a database with tables, if doesn't already exist.
    """
    SQLModel.metadata.create_all(engine, checkfirst=True)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """
    Things to run before and after the app runs.
    """
    _create_db_and_tables()
    yield


app = FastAPI(
    title="Clean Investment Monitor",
    summary="This is optional summary text. Lorem ipsum odor amet, consectetuer adipiscing elit.",
    description="This is optional description text. Lorem ipsum odor amet, consectetuer adipiscing elit. Habitant taciti quisque fermentum nisl ligula praesent. Venenatis nostra lacinia pellentesque efficitur netus dignissim. Eget aenean sapien semper nisi maecenas nunc. Ac nec a potenti donec nunc sit. Penatibus sapien ante commodo, viverra netus vitae nam cras. Duis porttitor platea penatibus viverra etiam velit. Egestas et venenatis dictum gravida viverra nullam nullam donec mus.\n```\nimport coolpackage\n\noutput = coolpackage.do_something_cool()\n```\nLorem ipsum odor amet, consectetuer adipiscing elit. Habitant taciti quisque fermentum nisl ligula praesent. Venenatis nostra lacinia pellentesque efficitur netus dignissim. Eget aenean sapien semper nisi maecenas nunc. Ac nec a potenti donec nunc sit. Penatibus sapien ante commodo, viverra netus vitae nam cras. Duis porttitor platea penatibus viverra etiam velit. Egestas et venenatis dictum gravida viverra nullam nullam donec mus.",
    version="0.0.1",
    terms_of_service="https://ourcompany.example.com/tos",
        contact={
        "name": "Some Optional Guy",
        "url": "http://ourcompany.example.com/contact/",
        "email": "someguy@ourcompany.example.com",
    },
    license_info={
        "name": "Optional License 2.0",
        "identifier": "MIT",
    },
    openapi_tags=[
        {
            "name": "facilities",
            "description": "Energy facilities.",
        },
    ],
    lifespan=_lifespan,
)


@app.post("/facilities/", tags=["facilities"])
def create_facility(facility: Facility, session: SessionDep) -> Facility:
    """
    Create a Facility.
    """
    # TODO: Not sure we're handing the exception correctly for FastAPI as it's not in the OpenAPI docs.
    try:

        session.add(facility)
        session.commit()
        session.refresh(facility)
    except IntegrityError as e:
        session.rollback()
        if "duplicate key" in str(e.orig):
            # Facility request is trying to create has uid of existing facility.
            # Apparently SQLmodel isn't catching these, yet?
            raise HTTPException(
                status_code=409, detail="A resource with this uid already exists",
            )
        else:
            raise
    return facility


@app.get("/facilities/", tags=["facilities"])
def read_facilities(
    session: SessionDep,
    segment: Annotated[str | None, Query(description="Facilities from segment")] = None,
    technology: Annotated[str | None, Query(description="Facilities for technology")] = None,
    announced_before: Annotated[datetime.date | None, Query(description="Announcement date before YYYY-MM-DD")] = None,
    announced_after: Annotated[datetime.date | None, Query(description="Announcement date after YYYY-MM-DD")] = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=5000)] = 100,
) -> list[Facility]:
    """
    Get Facilities.
    """
    this_query = select(Facility)

    # Query facilities from a certain segment.
    if segment is not None:
        this_query = this_query.where(Facility.segment == str(segment))

    # Query facilities for a certain technology.
    if technology is not None:
        this_query = this_query.where(Facility.technology == str(technology))

    # Query by announement date.
    if announced_before is not None:
        before_date = datetime.date.fromisoformat(str(announced_before))
        this_query = this_query.where(Facility.announcement_date < before_date)
    if announced_after is not None:
        after_date = datetime.date.fromisoformat(str(announced_after))
        this_query = this_query.where(Facility.announcement_date > after_date)

    # Ordering output by announcement date.
    this_query = this_query.order_by(Facility.announcement_date)

    # Pagination
    this_query = this_query.offset(offset).limit(limit)

    facilities = session.exec(this_query).all()
    return facilities


@app.get("/facilities/{uid}", tags=["facilities"])
def read_facility(uid: str, session: SessionDep) -> Facility:
    """
    Get a specific Facility.
    """
    facility = session.get(Facility, uid)
    # TODO: Confirm this is bet way to handle this so appears in docs?
    if facility is None:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility


@app.delete("/facilities/{uid}", tags=["facilities"])
def delete_facility(uid: str, session: SessionDep):
    """
    Delete a specific Facility.
    """
    facility = session.get(Facility, uid)
    # TODO: Do we return exception on this or be silent? Check standards.
    if facility is None:
        raise HTTPException(status_code=404, detail="Facility not found")
    session.delete(facility)
    session.commit()
    return {"ok": True}


if __name__ == "__main__":
    # We're launching web server here so we can set port and host information from environment variables.
    import uvicorn

    # Configs when run as script.
    PORT = int(os.environ.get("PORT", 8080))
    # Listen local only, use "0.0.0.0" to listen to all public IPs, like in container or prod deployment.
    HOST = str(
        os.environ.get("HOST", "127.0.0.1")
    )  # For local dev outside container use "127.0.0.1"

    uvicorn.run(app, host=HOST, port=PORT)