from src.model import User

class AthleteService:
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.filter_by(user_id=user_id).first()



