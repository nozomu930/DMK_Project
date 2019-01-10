from sqlalchemy import create_engine, Column, Integer, String, REAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

# SQLite 使用時
# SQLite - File（通常のファイル保存）
engine = create_engine('sqlite:///electricpower_db.sqlite3')  # スラッシュは3本

# SQLログを表示したい場合には echo=True を指定
engine = create_engine('sqlite:///electricpower_db.sqlite3', echo=True)

Base = declarative_base()

# ベースモデルを継承してモデルクラスを定義
class ElectricPower(Base):
    
    __tablename__ = 'ElectricPowers'

    id = Column(Integer, primary_key=True)
    time = Column(String(255))
    ep1 = Column(REAL)  # 電力値
    ep2 = Column(REAL)
    ep3 = Column(REAL)
    module_num = Column(Integer)

    def __init__(self, time, ep1, ep2, ep3, module_num):
        self.time = time
        self.ep1 = ep1
        self.ep2 = ep2
        self.ep3 = ep3
        self.module_num = module_num

 
    #def __repr__(self):
    #    return "<ElectricPower(id='%s', name='%s', score='%s')>" % (self.id, self.name, self.score)

def AddDataBase(li):
    # テーブルの作成
    # テーブルがない場合 CREATE TABLE 文が実行される
    Base.metadata.create_all(engine)  # 作成した engine を引数にすること

    # SQLAlchemy はセッションを介してクエリを実行する
    Session = sessionmaker(bind=engine)
    session = Session()

    session.add(ElectricPower(*li))
    session.commit()

    # セッション・クローズ
    # DB処理が不要になったタイミングやスクリプトの最後で実行
    session.close()