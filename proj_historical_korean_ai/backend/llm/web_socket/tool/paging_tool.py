import math


class PagingTool:

    @staticmethod
    def generate_paging(total_count: int, page_no: int, row_count: int, key: str = "paging") -> dict:
        if row_count <= 0:
            raise ValueError("Row Count Must Be Greater Than Zero(0).")
        total_pages = math.ceil(total_count / row_count)
        return {
            key: {
                "totalCount": total_count,
                "rowCount": row_count,
                "totalPages": total_pages,
                "pageNo": page_no,
                "prevPageNo": 0 if total_pages <= 0 else (
                    total_pages if page_no > total_pages else (
                        page_no - 1 if page_no > 1 else None)
                ),
                "nextPageNo": 0 if total_pages <= 0 else (
                    page_no + 1 if page_no < total_pages else None
                ),
            }
        }
