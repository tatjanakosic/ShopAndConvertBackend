# connection with database - mydatabase

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'tatjanakosic14@gmail.com'  # Tvoj email
MAIL_PASSWORD = 'ylqhhwikovznuhxq'   # Tvoja lozinka
MAIL_DEFAULT_SENDER = 'tatjanakosic14@gmail.com'  # Tvoj email koji šalje poruke


JWT_SECRET_KEY = 'b8f471504c115504696fa162f0d735f3233ef52c447c024f1f36b9f31363820829d3605eaf0629bf12ed51de3ea937ecdd984e6df5ea254d4d5d33906c74103b96732751948ea6324010a725d56ff16e37b200ff690a2edb8a9186e076334ee3631d97c22d6ae459f519b19c9ed7b5a213927c138b6e46b1c55efcebeacf890dd5216604f40e2424b65c60d3427b8607f32267ae181a11a630add00e4436cab74e57629e547858b246522be1d490d50e586571d74ab7b6be2f759547f16888d6295406bf96d5a08d6f2f931ac964c914cb12ff556624e40d7dfa2f7c118d45aecf8f3874c5519b587fcb34f6440939003038733cfd0cfe0441a480ce5b115964'  # Change this to a strong secret in production

SQLALCHEMY_DATABASE_URI = 'postgresql://tatjanakosic@localhost:5432/mydatabase'
SQLALCHEMY_TRACK_MODIFICATIONS = False





