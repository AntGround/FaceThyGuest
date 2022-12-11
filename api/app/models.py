
from app import db

class GuestModel(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(100), nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    id_card = db.Column(db.Text, nullable=False)
    profile_url = db.Column(db.Text, nullable=False)
    membership_id = db.Column(db.ForeignKey('memberships.id'))

    def __init__(self, guest_name, room_number, id_card, profile_url, membership_id):
        self.guest_name = guest_name
        self.room_number = room_number
        self.id_card = id_card
        self.profile_url = profile_url
        self.membership_id = membership_id

    def json(self):
        return {'id':self.id, 'id_card':self.id_card,'name': self.guest_name, 'room_number':self.room_number,'profile_url':self.profile_url}

class MembershipModel(db.Model):
    __tablename__ = 'memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    membership_name = db.Column(db.String(100), nullable=False)

    def __init__(self, membership_name):
        self.membership_name = membership_name

    def json(self):
        return {'id':self.id, 'name': self.membership_name}

class GuestFaceImagesModel(db.Model):
    __tablename__ = 'guest_face_images'
    
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.ForeignKey('guests.id'))
    face_images = db.Column(db.Text, nullable=False)

    def __init__(self, guest_id, face_images):
        self.guest_id = guest_id
        self.face_images = face_images