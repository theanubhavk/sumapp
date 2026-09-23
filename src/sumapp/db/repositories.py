from sqlalchemy import select, func

from src.sumapp.headmap import HEAD_MAP
from src.sumapp.constants import SHG_NAMES

class HeadRepos:
    def __init__(self, session):
        self.session = session

    def add(self, head_name:str, shg_name: str, datetime: str, amount: int):
        head = HEAD_MAP[head_name](shg_name=shg_name, datetime=datetime, amount=amount)
        self.session.add(head)
        self.session.commit()
        self.session.refresh(head)
        return head

    def get_shg_records_by_year(self, head_name: str, target_shg_name: str) -> list[dict]:
        head = HEAD_MAP[head_name]
        
        stmt = (
            select(head)
            .where(head.shg_name == target_shg_name)
            # .asc() for oldest first, use .desc() if you want newest first
            .order_by(head.datetime.asc()) 
        )
        
        records = self.session.scalars(stmt).all()
        return [
            {
                "id": row.id,
                "shg_name": row.shg_name,
                "amount": row.amount,
                "datetime": row.datetime
            }
            for row in records
        ]

    def get_all_shg_summaries(self, head_name: str) -> dict:
        head = HEAD_MAP[head_name]
        shg_list = [shg.lower() for shg in SHG_NAMES]
        
        # 1. Initialize the dictionary with 0s for all known SHGs
        result_dict = {
            shg: {"total_rows": 0, "total_amount": 0} 
            for shg in shg_list
        }
        
        # 2. Query the DB using GROUP BY and IN
        stmt = (
            select(
                head.shg_name,
                func.count(head.id).label("total_rows"),
                func.sum(head.amount).label("total_amount")
            )
            .where(head.shg_name.in_(shg_list))
            .group_by(head.shg_name)
        )
        
        # 3. Execute and map the results
        records = self.session.execute(stmt).all()
        
        for row in records:
            result_dict[row.shg_name] = {
                "total_rows": row.total_rows,
                "total_amount": row.total_amount or 0
            }
            
        return result_dict

    # def get_all(self):
    #     return self.session.query(HNFBachat).all()