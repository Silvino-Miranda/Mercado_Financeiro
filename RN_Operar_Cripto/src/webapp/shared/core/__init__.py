"""
Shared Core Module
Classes base para banco de dados e repositórios
"""
from .database import db, Database
from .base_repository import BaseRepository

__all__ = ['db', 'Database', 'BaseRepository']
