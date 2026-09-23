from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class HRFBachat(Base):
    __tablename__ = "hrf_bachat"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shg_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)


class AnshPunji(Base):
    __tablename__ = "ansh_punji"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shg_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)

class SadasyataSulk(Base):
    __tablename__ = "sadasyata_sulk"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shg_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)


class CmAnshdan(Base):
    __tablename__ = "cm_anshdan"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shg_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)

class SamanyaMulWapsi(Base):
    __tablename__ = "samanyamul_wapsi"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shg_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)


class SamanyaByajWapsi(Base):
    __tablename__ = "samanyabyaj_wapsi"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shg_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)


class IcfMulWapsi(Base):
    __tablename__ = "icfmul_wapsi"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shg_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)

class IcfByajWapsi(Base):
    __tablename__ = "icfbyaj_wapsi"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shg_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)

class FoodGrainprapti(Base):
    __tablename__ = "foodgrain_prapti"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shg_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)