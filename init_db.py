from ladder_classes import *

db.create_all()

#def __init__(self, team_name, email, password, name1,name2,name3,name4,name5,name6,dotaid1, dotaid2, dotaid3, dotaid4, dotaid5, dotaid6, captain_pos):
ruby = Team("The Ruby dream team", "ruby24yu@gmail.com", "wow",
            "best carry AU", "9k mid", "offlane god", "the ruby herself", "gabe the support", "poor reserve",
            181032461, 75431880, 136804356, 73853498, 55357091, 19750212,
            4)

lam = Team("Team Lammy", "mr.alexlam@yahoo.com", "lammy",
           "lammy1", "lammy2", "lammy3", "lammy4", "lammy5", "not lammy",
           97505594, 91785114, 194188265, 351922871, 108912284, 214716873,
           5)

eugene = Team("Team Eugene", "theeugenelin@gmail.com", "eugene",
              "eugene1", "eugene2","eugene3","eugene4","eugene5","not eugene",
              303387251, 181307353, 281621116, 142587627, 70763083, 117410333,
              2)

yuen = Team("Team Yuen", "ytc188@gmail.com", "yuen",
            "yuen1","yuen2","yuen3","yuen4","yuen5","yuen6",
            49757883, 27903687,219045406, 363588270, 84541181,168146273,
            1)

#db.session.add(ruby)
#db.session.commit()
#db.session.add(lam)
#db.session.commit()
#db.session.add(eugene)
#db.session.commit()
db.session.add(yuen)

db.session.commit()