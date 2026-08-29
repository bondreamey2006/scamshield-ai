from sqlalchemy import text
from sqlalchemy.orm import Session

def get_vpa_reputation(db: Session, vpa_normalized: str) -> dict:
    """
    Fetches the VPA trust record and the approved report count.
    Person 2 will use this dictionary in scoring.py.
    """
    query = text("""
        SELECT 
            v.trusted_record, 
            v.trust_source,
            COUNT(r.id) as approved_reports
        FROM vpas v
        LEFT JOIN reports r ON v.id = r.vpa_id AND r.status = 'demo_approved'
        WHERE v.vpa_normalized = :vpa
        GROUP BY v.id
    """)
    
    result = db.execute(query, {"vpa": vpa_normalized}).fetchone()
    
    # If the VPA doesn't exist in our database at all
    if not result:
        return {
            "known": False, 
            "trusted": False, 
            "trust_source": None, 
            "approved_reports": 0
        }
        
    # If the VPA is known
    return {
        "known": True,
        "trusted": result.trusted_record,
        "trust_source": result.trust_source,
        "approved_reports": result.approved_reports
    }