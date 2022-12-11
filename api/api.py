import shutil
from app import app, socketio, db, cache
from app.models import GuestModel, MembershipModel
import os
def env_setup():
    with app.app_context():
        # create model tables in database
        db.create_all()

        #initialize cache with db data
        for data in GuestModel.query.all():
            membership = MembershipModel.query.get(data.membership_id)
            cache.set(
                str(data.id), 
                {
                    "guest_name":data.guest_name, 
                    "room_number":str(data.room_number), 
                    "membership":membership.membership_name
                })
        print("cache loaded")

        #create dataset folder and move a test jpg in it if not already done
        if not os.path.exists(os.path.join(app.root_path, "FaceStuff", "dataset")):
            os.makedirs(os.path.join(app.root_path, "FaceStuff", "dataset"))
            shutil.copy(os.path.join(app.root_path, "default.jpg"), os.path.join(app.root_path, "FaceStuff", "dataset"))
            print(" + creating dataset folder")

        #create documents folder if not already crated
        if not os.path.exists(os.path.join(app.root_path, "Documents")):
            os.makedirs(os.path.join(app.root_path, "Documents"))
            print(" + creating documents folders")

        

if __name__=="__main__":
    env_setup()
    socketio.run(app, debug=True)