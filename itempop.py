from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcat.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Clear database
session.query(User).delete()
session.query(Category).delete()
session.query(Item).delete()

# Create dummy users
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png',
             gID="007")
User2 = User(name="Robort Bard", email="RobortTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png',
             fbID="008")
session.add(User1)
session.add(User2)
session.commit()

# 1-Soccer, 2-Basketball, 3-Baseball, 4-Frisbee, 5-Snowboarding,
# 6-Rock Climbing, 7-Football, 8-Skating, 9-Hockey
cat1 = Category(name="Soccer")
session.add(cat1)
session.commit()
cat2 = Category(name="Basketball")
session.add(cat2)
session.commit()
cat3 = Category(name="Baseball")
session.add(cat3)
session.commit()
cat4 = Category(name="Frisbee")
session.add(cat4)
session.commit()
cat5 = Category(name="Snowboarding")
session.add(cat5)
session.commit()
cat6 = Category(name="Rock Climbing")
session.add(cat6)
session.commit()
cat7 = Category(name="Football")
session.add(cat7)
session.commit()
cat8 = Category(name="Skating")
session.add(cat8)
session.commit()
cat9 = Category(name="Hockey")
session.add(cat9)
session.commit()

# Items for soccer
item1 = Item(user_id=1, name="Two shinguards", description=
             "So you can still walk after the game.", category=cat1)
session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Jersey", description="Looks cool!",category=cat1)
session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Soccer Cleats", description=
             "Perfect for butt-kicking.", category=cat1)
session.add(item3)
session.commit()

# Items for snowboarding
item4 = Item(user_id=2, name="Snowboard", description="It's a board.",
             category=cat5)
session.add(item4)
session.commit()


print "added menu items!"
