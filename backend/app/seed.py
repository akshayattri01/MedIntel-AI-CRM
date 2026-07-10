from datetime import datetime, timezone
from sqlalchemy import select
from app.auth.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import HCP, Interaction, Product, User

def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == "rep@medintel.ai"))
        if not user:
            user = User(email="rep@medintel.ai", full_name="Aarav Mehta", role="rep", hashed_password=hash_password("Password123!"))
            db.add(user)
            db.flush()
        for name in ["Cardiolex", "Glycora", "Neurovia"]:
            if not db.scalar(select(Product).where(Product.name == name)):
                db.add(Product(name=name, therapy_area="Primary Care", description=f"{name} clinical evidence pack"))
        if not db.scalar(select(HCP).where(HCP.owner_id == user.id)):
            hcp = HCP(owner_id=user.id, name="Dr Sharma", specialty="Cardiologist", institution="Apollo Heart Centre", city="Mumbai", sentiment_score=0.85)
            db.add(hcp)
            db.flush()
            db.add(Interaction(owner_id=user.id, hcp_id=hcp.id, interaction_type="in-person", occurred_at=datetime.now(timezone.utc), attendees=["Aarav Mehta"], topics_discussed=["Cardiolex efficacy"], materials_shared=["Clinical brochure"], samples_distributed=["2 samples"], observed_sentiment="positive", outcome="Interested in efficacy data", follow_up_action="Send outcome study next Monday", summary="Discussed Product X efficacy; doctor responded positively."))
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    run()
