from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.database import create_db_pool
from app.schemas import RepoInfo, RepoActivity

app = FastAPI(title="GitHub Repos API")


@app.on_event("startup")
async def startup():
    app.state.db_pool = await create_db_pool()


@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()


# Зависимость для получения пула подключений
async def get_db_pool():
    return app.state.db_pool


@app.get("/api/repos/top100", response_model=List[RepoInfo])
async def get_top_repos(
        order_by: Optional[str] = Query(
            "stars", regex="^(stars|forks|watchers|open_issues)$", description="Поле для сортировки"
        ),
        db_pool=Depends(get_db_pool)  # Используем зависимость для получения пула подключений
):
    query = f"""
        SELECT repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language
        FROM repos
        ORDER BY {order_by} DESC
        LIMIT 100;
    """
    try:
        async with db_pool.acquire() as conn:
            results = await conn.fetch(query)
            return [dict(record) for record in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/repos/{owner}/{repo}/activity", response_model=List[RepoActivity])
async def get_repo_activity(
        owner: str,
        repo: str,
        since: date,
        until: date,
        db_pool=Depends(get_db_pool)
):
    query = """
        SELECT date, commits, authors
        FROM repo_activity
        WHERE owner = $1 AND repo = $2 AND date BETWEEN $3 AND $4
        ORDER BY date;
    """
    try:
        async with db_pool.acquire() as conn:
            results = await conn.fetch(query, owner, repo, since, until)
            return [dict(record) for record in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
