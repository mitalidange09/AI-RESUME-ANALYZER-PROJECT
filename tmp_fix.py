from pathlib import Path
root = Path(r'C:\Users\Sai\OneDrive\ai-resume-job-recommender')
app = root / 'app.py'
text = app.read_text(encoding='utf-8-sig')
text = text.replace('''user = User(\n            name=name,\n            email=email,\n            ******\n            phone=phone,\n            role='candidate'\n        )''', '''user = User(\n            name=name,\n            email=email,\n            password=generate_password_hash(password),\n            phone=phone,\n            role='candidate'\n        )''', 1)
app.write_text(text, encoding='utf-8-sig')

db = root / 'database.py'
text2 = db.read_text(encoding='utf-8-sig')
text2 = text2.replace('''conn = pymysql.connect(host=db_host, user=db_user, ****** autocommit=True)''', '''conn = pymysql.connect(host=db_host, user=db_user, password=db_password, autocommit=True)''', 1)
db.write_text(text2, encoding='utf-8-sig')

admin = root / 'create_admin.py'
text3 = admin.read_text(encoding='utf-8-sig')
text3 = text3.replace('''admin = User(\n            name='Admin User',\n            email='admin@example.com',\n            ******'admin123'),\n            phone='0000000000',\n            role='admin'\n        )''', '''admin = User(\n            name='Admin User',\n            email='admin@example.com',\n            password=generate_password_hash('admin123'),\n            phone='0000000000',\n            role='admin'\n        )''', 1)
admin.write_text(text3, encoding='utf-8-sig')
print('done')
