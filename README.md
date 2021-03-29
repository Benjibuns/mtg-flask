# Database tool for managing accounts and cards/decks
## This app is intended to work alongside mtg-stone as a local database
- please reference Pipfile for dependencies


# How to add items to a database

```
>>> from mtg_database import *
>>> u1 = User(username="test1", email="test1@test1.com", password="test1")
>>> u1.username
'test1'
>>> db.session.add(u1)
>>> db.session.commit()

>>> c1 = Card(name="card1", api_card_id="something1")
>>> c1.api_card_id
'something1'
>>> db.session.add(c1)
>>> db.session.commit()

>>> c1.users   
[]
>>> c1.users.append(u1)
>>> c1.users       
[<User 1>]
>>> u1.cards
[<Card 1>]
>>> db.session.commit()

Card.query.filter_by(api_card_id=api_card_id).first()
```