from app import app, db

def criar_tabelas():
    with app.app_context():
        db.create_all()
        print("Tabelas criadas com sucesso!")

if __name__ == '__main__':
    criar_tabelas()
