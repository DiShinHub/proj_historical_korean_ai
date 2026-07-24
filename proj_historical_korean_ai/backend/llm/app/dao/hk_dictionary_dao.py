from sqlalchemy import select, and_, update, func
from sqlalchemy.dialects.postgresql import insert

import datetime

from app.helper.sql_session_helper import SqlSessionHelper
from app.model.entity.hk_dictionary_entity import HKDictionaryEntity


class HkDictionaryDao:

    __get_scoped_session = None

    def __init__(self, get_scoped_session):
        self.__get_scoped_session = get_scoped_session

    ############################################################
    # HK Dictionary
    ############################################################
    async def add_hk_dictionary(
        self,
        hk_dictionary: HKDictionaryEntity
    ) -> list[HKDictionaryEntity]:

        stmt = (
            insert(HKDictionaryEntity)
            .values(
                modern_korean=hk_dictionary.modern_korean,
                historical_korean=hk_dictionary.historical_korean,
                historical_period_start_dt=hk_dictionary.historical_period_start_dt,
                historical_period_end_dt=hk_dictionary.historical_period_end_dt,
                reg_member_seq=hk_dictionary.reg_member_seq,
                mod_member_seq=hk_dictionary.mod_member_seq,
                reg_dt=datetime.datetime.now(),
                mod_dt=datetime.datetime.now(),
                delete_yn="N"
            )
            .returning(HKDictionaryEntity.seq)
        )

        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )

        return [
            HKDictionaryEntity(**row._mapping)
            for row in result.fetchall()
        ]

    async def get_hk_dictionary(
        self,
        seq: int
    ) -> HKDictionaryEntity | None:

        stmt = (
            select(HKDictionaryEntity)
            .where(
                and_(
                    HKDictionaryEntity.seq == seq,
                    HKDictionaryEntity.delete_yn == "N"
                )
            )
        )

        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        return result.scalar_one_or_none()

    async def get_hk_dictionary_list(
            self,
            modern_korean: str | None = None,
            start_dt: datetime.datetime | None = None,
            end_dt: datetime.datetime | None = None,
            order_by: str = "seq",
            order_direction: str = "desc",
            page: int = 1,
            page_size: int = 20,
        ) -> list[HKDictionaryEntity]:

        offset = (page - 1) * page_size

        # 1. 기본 조회 조건
        conditions = [HKDictionaryEntity.delete_yn == "N"]

        # 현대어 검색 (LIKE)
        if modern_korean:
            conditions.append(HKDictionaryEntity.modern_korean.like(f"%{modern_korean}%"))

        # 시기 검색 (Between 조건)
        # 시작/종료 일자가 모두 넘어온 경우 between 적용
        if start_dt and end_dt:
            conditions.append(
                and_(
                    HKDictionaryEntity.historical_period_start_dt >= start_dt,
                    HKDictionaryEntity.historical_period_end_dt <= end_dt
                )
            )
        elif start_dt:
            conditions.append(HKDictionaryEntity.historical_period_start_dt >= start_dt)
            
        elif end_dt:
            conditions.append(HKDictionaryEntity.historical_period_end_dt <= end_dt)

        # 2. 동적 정렬 컬럼 및 방향 설정
        order_column = getattr(HKDictionaryEntity, order_by, HKDictionaryEntity.seq)
        
        if order_direction.lower() == "asc":
            order_clause = order_column.asc()
        else:
            order_clause = order_column.desc()

        # 3. 쿼리 생성 및 실행
        stmt = (
            select(HKDictionaryEntity)
            .where(and_(*conditions))
            .order_by(order_clause)
            .offset(offset)
            .limit(page_size)
        )
        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        return result.scalars().all()

    async def get_hk_dictionary_count(
            self,
            modern_korean: str | None = None,
            start_dt: datetime.datetime | None = None,
            end_dt: datetime.datetime | None = None,
        ) -> int:

        # 1. 목록 조회와 동일한 검색 조건 구성
        conditions = [HKDictionaryEntity.delete_yn == "N"]

        if modern_korean:
            conditions.append(HKDictionaryEntity.modern_korean.like(f"%{modern_korean}%"))

        if start_dt and end_dt:
            conditions.append(
                and_(
                    HKDictionaryEntity.historical_period_start_dt >= start_dt,
                    HKDictionaryEntity.historical_period_end_dt <= end_dt
                )
            )

        elif start_dt:
            conditions.append(HKDictionaryEntity.historical_period_start_dt >= start_dt)

        elif end_dt:
            conditions.append(HKDictionaryEntity.historical_period_end_dt <= end_dt)

        # 2. COUNT 쿼리 생성
        stmt = (
            select(func.count(HKDictionaryEntity.seq))
            .where(and_(*conditions))
        )

        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        return result.scalar() or 0

    async def update_hk_dictionary(
        self,
        seq: int,
        **kwargs
    ):
        update_values = {
            key: value
            for key, value in kwargs.items()
            if value is not None
        }

        update_values["mod_dt"] = func.now()

        stmt = (
            update(HKDictionaryEntity)
            .where(
                and_(
                    HKDictionaryEntity.seq == seq,
                    HKDictionaryEntity.delete_yn == "N"
                )
            )
            .values(**update_values)
        )

        await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )

    async def delete_hk_dictionary(
        self,
        seq: int,
        mod_member_seq: int
    ):
        stmt = (
            update(HKDictionaryEntity)
            .where(HKDictionaryEntity.seq == seq)
            .values(
                delete_yn="Y",
                mod_member_seq=mod_member_seq,
                mod_dt=func.now()
            )
        )

        await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )