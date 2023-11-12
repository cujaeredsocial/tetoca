from fastapi import HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session


async def _ascertain(up: BaseModel, keys: set[str]):
    model = up.model_fields_set
    data = up.__dict__
    for k in keys:
        if not data[k]:
            raise HTTPException(status_code=400, detail="Is not Exists.")
    for k in model - set(keys):
        if data[k] is not None:
            return
    raise HTTPException(status_code=400, detail="Is Empty.")


async def _composer(up: BaseModel, keys: set[str]):
    model = up.model_fields_set
    data = up.__dict__
    query_aux = {}
    for k in model - set(keys):
        if data[k] is not None:
            query_aux[k] = data[k]
    return query_aux


async def _query_first(query: Query, con: bool = True):
    try:
        update_query = query.first()
    except (Exception,):
        raise HTTPException(status_code=500, detail="Error in Query")
    else:
        if (con and update_query) or (con == False and not update_query):
            raise HTTPException(status_code=400, detail=f"Is {'' if con else 'not '}Exists")
    return update_query


async def _commit(update_query, db: Session, ret: bool = True):
    try:
        db.commit()
        if ret:
            db.refresh(update_query)
    except (Exception,):
        raise HTTPException(status_code=500, detail="Error in DataServer")


async def read(query: Query):
    return await _query_first(query, False)


async def update(up: BaseModel, query: Query, keys: [str], db: Session):
    await _ascertain(up, keys)
    update_query = await _query_first(query, False)
    query_aux = await _composer(up, keys)
    try:
        query.update(query_aux)
    except (Exception,):
        raise HTTPException(status_code=400, detail="Is not Exists")
    await _commit(update_query, db)
    return update_query


async def create(model, query: Query, db: Session):
    await _query_first(query, True)
    try:
        db.add(model)
    except (Exception,):
        raise HTTPException(status_code=400, detail="Is not Exists")
    try:
        await _commit(model, db)
    except (Exception,):
        raise HTTPException(status_code=505, detail="Internal Error")
    return model


async def delete(query: Query, db: Session):
    delete_query = await _query_first(query, False)
    try:
        db.delete(delete_query)
    except (Exception,):
        raise HTTPException(status_code=400, detail="Problems Cascade")
    await _commit(delete_query, db, False)
    return delete_query


async def activate(query: Query, db: Session):
    act_query = await _query_first(query, False)
    try:
        query.update({'desac': not act_query.desac})
    except (Exception,):
        raise HTTPException(status_code=400, detail="Is not Exists")
    await _commit(act_query, db)
    return act_query
