from inizio import app,db
from inizio.models import User,Item
from sys import argv
if __name__ == '__main__':
    if len(argv)>1 and argv[1]=='initdb':
        with app.app_context():
            db.create_all()
            print("site.db created")
    elif len(argv)>1 and argv[1]=='adddata':
        with app.app_context():
            existing_user=User.query.filter_by(username='poojitha').first()
            if not existing_user:
                new_user=User(
                    username='poojitha',
                    email_address='poojitha@example.com',
                    password_hash='password123',
                    courses_enrolled=2
                )
                db.session.add(new_user)
                db.session.commit()
                item1=Item(code='24CT11RC03', name='ComputerEngineeringWorkshop', modules=10)
                item2=Item(code='24CT11RC04', name='ProblemSolvingUsingC', modules=10)
                item3=Item(code='24CT11RC07', name='PythonProgramming', modules=10)
                item4=Item(code='24CT11RC08', name='WebTechmologiesFundamentals', modules=10)
                db.session.add_all([item1, item2, item3, item4])
                db.session.commit()
                print("Data added to site.db")
    else:
        app.run(debug=True)